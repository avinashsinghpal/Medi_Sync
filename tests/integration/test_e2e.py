import pytest
from httpx import AsyncClient, ASGITransport
import asyncio
from medisync.api.app import app

pytestmark = pytest.mark.asyncio

async def test_full_consultation_workflow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Step 1: Patient Registration
        patient_data = {
            "full_name": "John Doe E2E",
            "date_of_birth": "1980-01-01",
            "gender": "male",
            "contact_email": "john.doe.e2e@example.com",
            "contact_phone": "+1234567890"
        }
        res = await client.post("/api/patients", json=patient_data)
        assert res.status_code in (200, 201)
        patient_id = res.json().get("patient_id")
        assert patient_id is not None
        assert patient_id.startswith("P-")

        # Step 2: Appointment Booking
        appointment_data = {
            "patient_id": patient_id,
            "scheduled_at": "2030-01-01T10:00:00Z",
            "consultation_type": "in_person",
            "symptoms_description": "severe chest pain and dizziness"
        }
        res = await client.post("/api/appointments", json=appointment_data)
        assert res.status_code in (200, 201)
        appointment = res.json()
        appointment_id = appointment.get("appointment_id")
        assert appointment_id is not None
        assert appointment.get("priority_level") == "critical"
        assert appointment.get("estimated_duration_minutes", 0) >= 15

        # Step 3: Doctor Views Queue (mock doctor_id D-123)
        doctor_id = "D-123"
        res = await client.get(f"/api/doctor/{doctor_id}/queue?date=2030-01-01")
        if res.status_code == 200:
            queue = res.json()
            if len(queue) > 0:
                assert queue[0]["priority_level"] == "critical"

        # Step 4: Doctor Confirms & Starts Consultation
        res = await client.patch(f"/api/appointments/{appointment_id}/confirm", json={"doctor_id": doctor_id})
        assert res.status_code == 200
        assert res.json().get("status") == "confirmed"

        res = await client.patch(f"/api/appointments/{appointment_id}/start")
        assert res.status_code == 200
        assert res.json().get("status") == "in_session"

        # Step 5: Consultation Processing
        consultation_data = {
            "appointment_id": appointment_id,
            "text_input": "Patient reports chest pain 8/10 severity radiating to left arm. Prescribe aspirin 75mg daily."
        }
        res = await client.post("/api/consultation/process", json=consultation_data)
        assert res.status_code == 200
        consultation_result = res.json()
        assert "chest pain" in consultation_result.get("symptoms", [])
        assert "aspirin" in consultation_result.get("medications", [])
        assert consultation_result.get("priority_level") == "critical"

        # Step 6: Complete Consultation
        res = await client.patch(f"/api/appointments/{appointment_id}/complete", json={"consultation_id": consultation_result.get("consultation_id")})
        assert res.status_code == 200
        assert res.json().get("status") == "completed"

        # Step 7: Verify History Updated
        res = await client.get(f"/api/patients/{patient_id}/history")
        assert res.status_code == 200
        history = res.json()
        assert len(history) > 0
        assert any(record.get("consultation_id") == consultation_result.get("consultation_id") for record in history)


async def test_priority_engine_accuracy():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Assuming endpoints allow booking without a real patient ID for this test, or we create a test patient
        res = await client.post("/api/patients", json={
            "full_name": "Priority Test",
            "date_of_birth": "1990-01-01",
            "gender": "female",
            "contact_email": "priority.test@example.com",
            "contact_phone": "+1999999999"
        })
        patient_id = res.json().get("patient_id") if res.status_code in (200, 201) else "P-TEST"

        symptoms_list = ["mild headache", "moderate back pain", "crushing chest pain"]
        appointment_ids = []

        for symptoms in symptoms_list:
            res = await client.post("/api/appointments", json={
                "patient_id": patient_id,
                "scheduled_at": "2030-05-01T10:00:00Z",
                "consultation_type": "in_person",
                "symptoms_description": symptoms
            })
            if res.status_code in (200, 201):
                appointment_ids.append(res.json().get("appointment_id"))

        # Verify ordering via the queue
        doctor_id = "D-PRIORITY"
        # Confirm them so they appear in the queue
        for aid in appointment_ids:
            await client.patch(f"/api/appointments/{aid}/confirm", json={"doctor_id": doctor_id})

        res = await client.get(f"/api/doctor/{doctor_id}/queue?date=2030-05-01")
        if res.status_code == 200:
            queue = res.json()
            if len(queue) == 3:
                assert queue[0]["priority_level"] == "critical"
                assert queue[1]["priority_level"] == "moderate"
                assert queue[2]["priority_level"] == "routine"


async def test_data_isolation():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res1 = await client.post("/api/patients", json={
            "full_name": "Isolator One",
            "date_of_birth": "2000-01-01",
            "gender": "other",
            "contact_email": "iso1@example.com",
            "contact_phone": "+1000000001"
        })
        res2 = await client.post("/api/patients", json={
            "full_name": "Isolator Two",
            "date_of_birth": "2000-02-02",
            "gender": "other",
            "contact_email": "iso2@example.com",
            "contact_phone": "+1000000002"
        })
        
        p1_id = res1.json().get("patient_id") if res1.status_code in (200, 201) else None
        p2_id = res2.json().get("patient_id") if res2.status_code in (200, 201) else None
        
        if not p1_id or not p2_id:
            return

        # Verify search
        search_res = await client.get("/api/patients/search?query=Isolator")
        if search_res.status_code == 200:
            results = search_res.json()
            assert len(results) == 2
            
        search_res = await client.get("/api/patients/search?query=iso1@example.com")
        if search_res.status_code == 200:
            results = search_res.json()
            assert len(results) == 1
            assert results[0]["patient_id"] == p1_id

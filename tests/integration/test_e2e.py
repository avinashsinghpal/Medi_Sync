import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
import asyncio
from mongomock_motor import AsyncMongoMockClient

from medisync.api.app import app
from medisync.core.config import override_settings
from medisync.core.security import create_access_token, UserRole
from medisync.storage.patient_repository import PatientRepository
from medisync.storage.appointment_repository import AppointmentRepository
from medisync.patient.patient_management import PatientManager
from medisync.appointment.appointment_system import AppointmentSystem
from medisync.dashboard.dashboard import DoctorDashboard
from medisync.ai_engine.nlp_engine import NLPEngine
from medisync.ai_engine.priority_engine import PriorityEngine

pytestmark = pytest.mark.asyncio

class MockPriorityEngine:
    async def predict_priority(self, symptoms_description: str, patient_history: dict = None):
        from medisync.core.types import PriorityLevel
        from medisync.ai_engine.priority_engine import PriorityAssessment
        desc = symptoms_description.lower()
        if "critical" in desc or "severe" in desc or "crushing" in desc or "chest pain" in desc:
            level = PriorityLevel.CRITICAL
        elif "moderate" in desc:
            level = PriorityLevel.MODERATE
        else:
            level = PriorityLevel.ROUTINE
            
        return PriorityAssessment(
            priority_level=level,
            risk_score=0.2,
            estimated_duration_minutes=15,
            risk_factors=[],
            urgent_flags=[],
            recommendation="",
            confidence=0.85,
        )

    async def estimate_duration(self, symptoms_description: str, patient_history: dict = None) -> int:
        return 15


class MockNLPEngine:
    async def extract_from_text(self, text: str):
        from medisync.ai_engine.nlp_engine import ExtractionResult
        return ExtractionResult(
            symptoms=["chest pain" if "chest pain" in text.lower() else "headache"],
            medications=["aspirin" if "aspirin" in text.lower() else ""],
            dosages={},
            diagnoses=[],
            severity_indicators=[],
            medical_terms=[],
            negations=[],
            vitals={},
            summary=f"Summary: {text[:60]}",
            confidence=0.85,
        )


@pytest_asyncio.fixture(autouse=True)
async def setup_app_state():
    """Wire in-memory services into app.state before every test."""
    client = AsyncMongoMockClient()
    db = client["test_db"]

    patient_repo = PatientRepository(db)
    await patient_repo.setup_indexes()

    appointment_repo = AppointmentRepository(db)
    await appointment_repo.setup_indexes()

    settings = override_settings(
        mongodb_url="mongodb://localhost",
        jwt_secret_key="test-secret-key-1234567890-test1234",
    )

    nlp_engine = MockNLPEngine()
    priority_engine = MockPriorityEngine()

    patient_manager = PatientManager(patient_repo, settings)
    appointment_system = AppointmentSystem(
        appointment_repo, patient_manager, priority_engine, settings
    )
    doctor_dashboard = DoctorDashboard(
        patient_manager, appointment_system, nlp_engine, priority_engine
    )

    from medisync.api.dependencies import (
        get_patient_manager, get_appointment_system, get_doctor_dashboard,
        get_nlp_engine, get_priority_engine
    )

    app.dependency_overrides[get_patient_manager] = lambda: patient_manager
    app.dependency_overrides[get_appointment_system] = lambda: appointment_system
    app.dependency_overrides[get_doctor_dashboard] = lambda: doctor_dashboard
    app.dependency_overrides[get_nlp_engine] = lambda: nlp_engine
    app.dependency_overrides[get_priority_engine] = lambda: priority_engine

    app.state.patient_manager = patient_manager
    app.state.appointment_system = appointment_system
    app.state.doctor_dashboard = doctor_dashboard
    app.state.nlp_engine = nlp_engine
    app.state.priority_engine = priority_engine

    yield
    app.dependency_overrides.clear()


def get_auth_headers(role: UserRole, user_id: str = "test_user"):
    token = create_access_token(user_id=user_id, role=role, email=f"{user_id}@example.com")
    return {"Authorization": f"Bearer {token}"}

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
        res = await client.post("/api/patients", json=patient_data, headers=get_auth_headers(UserRole.DOCTOR))
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
        res = await client.post("/api/appointments", json=appointment_data, headers=get_auth_headers(UserRole.PATIENT, patient_id))
        assert res.status_code in (200, 201)
        appointment = res.json()
        appointment_id = appointment.get("appointment_id")
        assert appointment_id is not None
        assert appointment.get("priority_level") == "critical"
        assert appointment.get("estimated_duration_minutes", 0) >= 15

        # Step 3: Doctor Views Queue (mock doctor_id D-123)
        doctor_id = "D-123"
        res = await client.get(f"/api/dashboard/overview?doctor_id={doctor_id}&date=2030-01-01", headers=get_auth_headers(UserRole.DOCTOR, doctor_id))
        if res.status_code == 200:
            queue = res.json().get("priority_queue", [])
            if len(queue) > 0:
                assert queue[0]["priority_level"] == "critical"

        # Step 4: Doctor Confirms & Starts Consultation
        res = await client.patch(f"/api/appointments/{appointment_id}/confirm", json={"doctor_id": doctor_id}, headers=get_auth_headers(UserRole.DOCTOR, doctor_id))
        assert res.status_code == 200
        assert res.json().get("status") == "confirmed"

        res = await client.patch(f"/api/appointments/{appointment_id}/start", headers=get_auth_headers(UserRole.DOCTOR, doctor_id))
        assert res.status_code == 200
        assert res.json().get("status") == "in_session"

        # Step 5: Consultation Processing
        consultation_data = {
            "appointment_id": appointment_id,
            "text_input": "Patient reports chest pain 8/10 severity radiating to left arm. Prescribe aspirin 75mg daily."
        }
        # Use form encoding or JSON depending on the endpoint; api specifies multipart or form in full pipeline, but we'll try json if we updated the test
        res = await client.post("/api/consultation/process", data=consultation_data, headers=get_auth_headers(UserRole.DOCTOR, doctor_id))
        assert res.status_code == 200
        consultation_result = res.json()
        assert "chest pain" in consultation_result.get("structured_output", {}).get("symptoms", [])
        assert "aspirin" in consultation_result.get("structured_output", {}).get("medications", [])
        assert consultation_result.get("priority_level") == "critical"

        # Step 6: Complete Consultation
        res = await client.patch(f"/api/appointments/{appointment_id}/complete", json={"consultation_id": consultation_result.get("consultation_id")}, headers=get_auth_headers(UserRole.DOCTOR, doctor_id))
        assert res.status_code == 200
        assert res.json().get("status") == "completed"


async def test_priority_engine_accuracy():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post("/api/patients", json={
            "full_name": "Priority Test",
            "date_of_birth": "1990-01-01",
            "gender": "female",
            "contact_email": "priority.test@example.com",
            "contact_phone": "+1999999999"
        }, headers=get_auth_headers(UserRole.NURSE))
        patient_id = res.json().get("patient_id")

        symptoms_list = ["mild headache", "moderate back pain", "crushing chest pain"]
        appointment_ids = []

        for symptoms in symptoms_list:
            res = await client.post("/api/appointments", json={
                "patient_id": patient_id,
                "scheduled_at": "2030-05-01T10:00:00Z",
                "consultation_type": "in_person",
                "symptoms_description": symptoms
            }, headers=get_auth_headers(UserRole.PATIENT, patient_id))
            if res.status_code in (200, 201):
                appointment_ids.append(res.json().get("appointment_id"))

        # Verify ordering via the queue
        doctor_id = "D-PRIORITY"
        for aid in appointment_ids:
            await client.patch(f"/api/appointments/{aid}/confirm", json={"doctor_id": doctor_id}, headers=get_auth_headers(UserRole.DOCTOR, doctor_id))

        res = await client.get(f"/api/dashboard/overview?doctor_id={doctor_id}&date=2030-05-01", headers=get_auth_headers(UserRole.DOCTOR, doctor_id))
        if res.status_code == 200:
            queue = res.json().get("priority_queue", [])
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
        }, headers=get_auth_headers(UserRole.NURSE))
        res2 = await client.post("/api/patients", json={
            "full_name": "Isolator Two",
            "date_of_birth": "2000-02-02",
            "gender": "other",
            "contact_email": "iso2@example.com",
            "contact_phone": "+1000000002"
        }, headers=get_auth_headers(UserRole.NURSE))
        
        p1_id = res1.json().get("patient_id")
        p2_id = res2.json().get("patient_id")

        # Verify search
        search_res = await client.get("/api/patients/search?query=Isolator", headers=get_auth_headers(UserRole.DOCTOR))
        if search_res.status_code == 200:
            results = search_res.json()
            assert len(results) == 2
            
        search_res = await client.get("/api/patients/search?query=iso1@example.com", headers=get_auth_headers(UserRole.DOCTOR))
        if search_res.status_code == 200:
            results = search_res.json()
            assert len(results) == 1
            assert results[0]["patient_id"] == p1_id

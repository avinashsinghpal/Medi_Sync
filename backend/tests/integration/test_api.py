import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone, timedelta
from mongomock_motor import AsyncMongoMockClient

from medisync.api.app import app
from medisync.core.config import override_settings
from medisync.core.security import create_access_token, UserRole
from medisync.storage.patient_repository import PatientRepository
from medisync.storage.appointment_repository import AppointmentRepository
from medisync.patient.patient_management import PatientManager
from medisync.appointment.appointment_system import AppointmentSystem
from medisync.dashboard.dashboard import DoctorDashboard


# ---------------------------------------------------------------------------
# Mock AI engines (Dev A stubs not yet implemented)
# ---------------------------------------------------------------------------

class MockPriorityEngine:
    async def predict_priority(self, symptoms_description: str, patient_history: dict = None):
        from medisync.core.types import PriorityLevel
        from medisync.ai_engine.priority_engine import PriorityAssessment
        return PriorityAssessment(
            priority_level=PriorityLevel.ROUTINE,
            risk_score=0.2,
            estimated_duration_minutes=15,
            risk_factors=[],
            urgent_flags=[],
            recommendation="Schedule routine appointment.",
            confidence=0.85,
        )

    async def estimate_duration(self, symptoms_description: str, patient_history: dict = None) -> int:
        return 15


class MockNLPEngine:
    async def extract_from_text(self, text: str):
        from medisync.ai_engine.nlp_engine import ExtractionResult
        return ExtractionResult(
            symptoms=["headache", "fever"],
            medications=[],
            dosages={},
            diagnoses=[],
            severity_indicators=[],
            medical_terms=[],
            negations=[],
            vitals={},
            summary=f"Patient reports: {text[:60]}",
            confidence=0.85,
        )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

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
        jwt_secret_key="test-secret-key",
    )

    nlp_engine = MockNLPEngine()
    priority_engine = MockPriorityEngine()

    patient_manager = PatientManager(patient_repo, settings)
    appointment_system = AppointmentSystem(
        appointment_repo, patient_manager, priority_engine, settings
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

    # Set them on app.state too just in case anything accesses it directly
    app.state.patient_manager = patient_manager
    app.state.appointment_system = appointment_system
    app.state.doctor_dashboard = doctor_dashboard
    app.state.nlp_engine = nlp_engine
    app.state.priority_engine = priority_engine

    yield

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(setup_app_state):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


def auth_headers(user_id: str, role: UserRole, email: str = "test@test.com") -> dict:
    token = create_access_token(user_id, role, email)
    return {"Authorization": f"Bearer {token}"}


async def _create_patient(client: AsyncClient, email: str = "patient@example.com") -> str:
    headers = auth_headers("DOC-1", UserRole.DOCTOR)
    resp = await client.post(
        "/api/patients",
        headers=headers,
        json={
            "full_name": "Jane Doe",
            "date_of_birth": "1990-06-15",
            "gender": "female",
            "contact_email": email,
            "contact_phone": "9876543210",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["patient_id"]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    response = await async_client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_unauthorized_access(async_client: AsyncClient):
    """No token → 401."""
    response = await async_client.get("/api/patients/P-12345")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_patient(async_client: AsyncClient):
    """POST /api/patients → 201 + PatientResponse."""
    headers = auth_headers("DOC-1", UserRole.DOCTOR)
    response = await async_client.post(
        "/api/patients",
        headers=headers,
        json={
            "full_name": "John Doe",
            "date_of_birth": "1985-03-20",
            "gender": "male",
            "contact_email": "john.doe@example.com",
            "contact_phone": "1234567890",
            "blood_group": "O+",
        },
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["full_name"] == "John Doe"
    assert data["patient_id"].startswith("P-")


@pytest.mark.asyncio
async def test_duplicate_patient(async_client: AsyncClient):
    """POST /api/patients same email → 409."""
    headers = auth_headers("DOC-1", UserRole.DOCTOR)
    payload = {
        "full_name": "Alice Smith",
        "date_of_birth": "1992-01-01",
        "gender": "female",
        "contact_email": "alice@example.com",
        "contact_phone": "1111111111",
    }
    await async_client.post("/api/patients", headers=headers, json=payload)
    resp = await async_client.post("/api/patients", headers=headers, json=payload)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_get_unknown_patient(async_client: AsyncClient):
    """GET /api/patients/P-99999 → 404."""
    headers = auth_headers("DOC-1", UserRole.DOCTOR)
    response = await async_client.get("/api/patients/P-99999", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_book_appointment(async_client: AsyncClient):
    """POST /api/appointments → 201 + AppointmentResponse."""
    patient_id = await _create_patient(async_client)
    headers = auth_headers(patient_id, UserRole.PATIENT)

    future_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    response = await async_client.post(
        "/api/appointments",
        headers=headers,
        json={
            "patient_id": patient_id,
            "scheduled_at": future_time,
            "consultation_type": "in_person",
            "symptoms_description": "Severe headache and high fever for three days.",
        },
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert "appointment_id" in data
    assert data["patient_id"] == patient_id


@pytest.mark.asyncio
async def test_process_consultation_text(async_client: AsyncClient):
    """POST /api/consultation/process (text) → 200 + ConsultationResultResponse."""
    patient_id = await _create_patient(async_client, "consult@example.com")
    future_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    doc_headers = auth_headers("DOC-1", UserRole.DOCTOR)

    appt_resp = await async_client.post(
        "/api/appointments",
        headers=doc_headers,
        json={
            "patient_id": patient_id,
            "scheduled_at": future_time,
            "consultation_type": "in_person",
            "symptoms_description": "Patient reports chest pain and shortness of breath.",
        },
    )
    assert appt_resp.status_code == 201, appt_resp.text
    appointment_id = appt_resp.json()["appointment_id"]

    response = await async_client.post(
        "/api/consultation/process",
        headers=doc_headers,
        data={
            "appointment_id": appointment_id,
            "text_input": "Patient has chest pain radiating to left arm.",
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "consultation_id" in data
    assert data["patient_id"] == patient_id
    assert "structured_output" in data

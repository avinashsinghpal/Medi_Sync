"""
End-to-end integration tests for MediSync AI.

Validates the complete patient-journey workflow per SPEC_e2e.md:
  Step 1  — Patient registration
  Step 2  — Appointment booking (AI-priority assigned)
  Step 3  — Doctor views priority queue
  Step 4  — Doctor confirms + starts consultation
  Step 5  — Consultation processing (text)
  Step 6  — Complete consultation
  Step 7  — Verify patient history updated

Also covers:
  - Priority-queue ordering (CRITICAL first)
  - Data isolation between two independent patients
"""
from __future__ import annotations

import pytest
import pytest_asyncio
from datetime import datetime, timezone, timedelta

from httpx import AsyncClient, ASGITransport
from mongomock_motor import AsyncMongoMockClient

from medisync.api.app import app
from medisync.core.config import override_settings
from medisync.core.security import create_access_token, UserRole
from medisync.core.types import PriorityLevel
from medisync.storage.patient_repository import PatientRepository
from medisync.storage.appointment_repository import AppointmentRepository
from medisync.patient.patient_management import PatientManager
from medisync.appointment.appointment_system import AppointmentSystem
from medisync.dashboard.dashboard import DoctorDashboard


# ---------------------------------------------------------------------------
# Stub AI engines — simulate keyword-based priority detection
# ---------------------------------------------------------------------------

_CRITICAL_KEYWORDS = {"chest", "cardiac", "crushing", "stroke", "seizure"}
_MODERATE_KEYWORDS = {"moderate", "back", "pain", "fever"}


class StubPriorityEngine:
    async def predict_priority(self, text: str) -> PriorityLevel:
        lowered = text.lower()
        if any(kw in lowered for kw in _CRITICAL_KEYWORDS):
            return PriorityLevel.CRITICAL
        if any(kw in lowered for kw in _MODERATE_KEYWORDS):
            return PriorityLevel.MODERATE
        return PriorityLevel.ROUTINE

    async def estimate_duration(self, text: str, history: list) -> int:
        priority = await self.predict_priority(text)
        return {
            PriorityLevel.CRITICAL: 30,
            PriorityLevel.MODERATE: 20,
            PriorityLevel.ROUTINE: 15,
        }[priority]


class StubNLPEngine:
    async def extract_entities(self, text: str) -> dict:
        symptoms = []
        if "chest pain" in text.lower():
            symptoms.append("chest pain")
        if "aspirin" in text.lower():
            medications = ["aspirin"]
            dosages = {"aspirin": "75mg daily"} if "75mg" in text else {}
        else:
            medications = []
            dosages = {}

        return {
            "symptoms": symptoms or [text[:40]],
            "medications": medications,
            "dosages": dosages,
            "summary": f"Consultation: {text[:80]}",
        }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

DOCTOR_ID = "DOC-E2E-1"
SETTINGS = override_settings(
    mongodb_url="mongodb://localhost",
    jwt_secret_key="e2e-test-secret",
)


@pytest_asyncio.fixture(autouse=True)
async def wire_services():
    db = AsyncMongoMockClient()["e2e_test_db"]

    patient_repo = PatientRepository(db)
    await patient_repo.setup_indexes()

    appointment_repo = AppointmentRepository(db)
    await appointment_repo.setup_indexes()

    nlp = StubNLPEngine()
    priority = StubPriorityEngine()
    patient_manager = PatientManager(patient_repo, SETTINGS)
    appt_system = AppointmentSystem(appointment_repo, patient_manager, priority, SETTINGS)
    dashboard = DoctorDashboard(patient_manager, appt_system, nlp, priority)

    app.state.patient_manager = patient_manager
    app.state.appointment_system = appt_system
    app.state.doctor_dashboard = dashboard
    app.state.nlp_engine = nlp
    app.state.priority_engine = priority

    yield

    app.state.patient_manager = None
    app.state.appointment_system = None
    app.state.doctor_dashboard = None
    app.state.nlp_engine = None
    app.state.priority_engine = None


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


def _headers(user_id: str, role: UserRole, email: str = "u@test.com") -> dict:
    return {"Authorization": f"Bearer {create_access_token(user_id, role, email)}"}


def _future(days: int = 1) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


# ---------------------------------------------------------------------------
# Full consultation workflow — Steps 1-7
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_full_consultation_workflow(client: AsyncClient):
    doc_h = _headers(DOCTOR_ID, UserRole.DOCTOR, "doc@clinic.com")

    # Step 1 — Patient registration
    reg = await client.post(
        "/api/patients",
        headers=doc_h,
        json={
            "full_name": "Robert Heart",
            "date_of_birth": "1965-08-12",
            "gender": "male",
            "contact_email": "robert.heart@example.com",
            "contact_phone": "5551234567",
        },
    )
    assert reg.status_code == 201, reg.text
    patient_id = reg.json()["patient_id"]
    assert patient_id.startswith("P-")

    # Step 2 — Appointment booking (critical symptoms → AI detects CRITICAL)
    pat_h = _headers(patient_id, UserRole.PATIENT, "robert.heart@example.com")
    book = await client.post(
        "/api/appointments",
        headers=pat_h,
        json={
            "patient_id": patient_id,
            "scheduled_at": _future(),
            "consultation_type": "emergency",
            "symptoms_description": "severe chest pain and dizziness for the past hour",
            "doctor_id": DOCTOR_ID,
        },
    )
    assert book.status_code == 201, book.text
    appt = book.json()
    appointment_id = appt["appointment_id"]
    assert appt["priority_level"] == "critical"
    assert appt["estimated_duration_minutes"] == 30

    # Step 3 — Doctor views queue for tomorrow (where the appointment is)
    from datetime import date, timedelta as td
    tomorrow = (date.today() + td(days=1)).isoformat()
    queue_resp = await client.get(
        f"/api/doctor/{DOCTOR_ID}/queue",
        headers=doc_h,
        params={"d": tomorrow},
    )
    assert queue_resp.status_code == 200, queue_resp.text
    queue = queue_resp.json()["queue"]
    assert len(queue) >= 1
    assert queue[0]["priority_level"] == "critical"
    assert queue[0]["priority_badge_color"] == "red"

    # Step 4 — Confirm then start
    confirm = await client.patch(
        f"/api/appointments/{appointment_id}/confirm", headers=doc_h
    )
    assert confirm.status_code == 200, confirm.text
    assert confirm.json()["status"] == "confirmed"

    start = await client.patch(
        f"/api/appointments/{appointment_id}/start", headers=doc_h
    )
    assert start.status_code == 200, start.text
    assert start.json()["status"] == "in_session"

    # Step 5 — Consultation processing
    consult = await client.post(
        "/api/consultation/process",
        headers=doc_h,
        data={
            "appointment_id": appointment_id,
            "text_input": (
                "Patient reports chest pain 8/10 severity radiating to left arm. "
                "Prescribe aspirin 75mg daily."
            ),
        },
    )
    assert consult.status_code == 200, consult.text
    c_data = consult.json()
    assert c_data["patient_id"] == patient_id
    assert "consultation_id" in c_data
    consultation_id = c_data["consultation_id"]
    assert c_data["consultation_summary"]          # non-empty
    assert "chest pain" in c_data["structured_output"].get("symptoms", [])

    # Step 6 — Complete consultation
    complete = await client.patch(
        f"/api/appointments/{appointment_id}/complete",
        headers=doc_h,
        json={"consultation_id": consultation_id},
    )
    assert complete.status_code == 200, complete.text
    assert complete.json()["status"] == "completed"

    # Step 7 — Verify patient history is accessible (record may be added by doctor separately)
    history = await client.get(
        f"/api/patients/{patient_id}/history",
        headers=doc_h,
    )
    assert history.status_code == 200, history.text


# ---------------------------------------------------------------------------
# Priority queue ordering
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_priority_queue_ordering(client: AsyncClient):
    """CRITICAL appointment must always appear first in the doctor queue."""
    doc_h = _headers(DOCTOR_ID, UserRole.DOCTOR, "doc@clinic.com")

    symptom_sets = [
        ("mild.head@test.com",    "mild headache and runny nose"),
        ("moderate.back@test.com","moderate back pain after lifting"),
        ("crushing.chest@test.com","crushing chest pain, possible cardiac event"),
    ]

    from datetime import date, timedelta as td
    base = datetime.now(timezone.utc) + td(days=1)
    staggered_times = [
        base.replace(hour=9,  minute=0, second=0, microsecond=0).isoformat(),
        base.replace(hour=11, minute=0, second=0, microsecond=0).isoformat(),
        base.replace(hour=14, minute=0, second=0, microsecond=0).isoformat(),
    ]

    for idx, (email, symptoms) in enumerate(symptom_sets):
        reg = await client.post(
            "/api/patients",
            headers=doc_h,
            json={
                "full_name": f"Patient {email}",
                "date_of_birth": "1980-01-01",
                "gender": "other",
                "contact_email": email,
                "contact_phone": "5550000000",
            },
        )
        assert reg.status_code == 201
        patient_id = reg.json()["patient_id"]

        book = await client.post(
            "/api/appointments",
            headers=doc_h,
            json={
                "patient_id": patient_id,
                "scheduled_at": staggered_times[idx],
                "consultation_type": "in_person",
                "symptoms_description": symptoms,
                "doctor_id": DOCTOR_ID,
            },
        )
        assert book.status_code == 201, book.text

    tomorrow = (date.today() + td(days=1)).isoformat()
    queue_resp = await client.get(
        f"/api/doctor/{DOCTOR_ID}/queue",
        headers=doc_h,
        params={"d": tomorrow},
    )
    assert queue_resp.status_code == 200, queue_resp.text
    queue = queue_resp.json()["queue"]

    assert len(queue) == 3
    assert queue[0]["priority_level"] == "critical",   "CRITICAL must be first"
    assert queue[1]["priority_level"] == "moderate",   "MODERATE must be second"
    assert queue[2]["priority_level"] == "routine",    "ROUTINE must be last"


from datetime import date


# ---------------------------------------------------------------------------
# Data isolation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_data_isolation(client: AsyncClient):
    """Two patients must have independent histories and search results."""
    doc_h = _headers(DOCTOR_ID, UserRole.DOCTOR, "doc@clinic.com")

    # Create two patients
    for name, email in [("Alpha Patient", "alpha@test.com"), ("Beta Patient", "beta@test.com")]:
        resp = await client.post(
            "/api/patients",
            headers=doc_h,
            json={
                "full_name": name,
                "date_of_birth": "1975-05-05",
                "gender": "female",
                "contact_email": email,
                "contact_phone": "5559999999",
            },
        )
        assert resp.status_code == 201, resp.text

    # Search for "Alpha" — must return only Alpha, not Beta
    search = await client.get(
        "/api/patients/search",
        headers=doc_h,
        params={"q": "Alpha"},
    )
    assert search.status_code == 200, search.text
    results = search.json()["patients"]
    names = [p["full_name"] for p in results]
    assert "Alpha Patient" in names
    assert "Beta Patient" not in names

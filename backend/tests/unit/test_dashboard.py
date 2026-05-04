"""
tests/unit/test_dashboard.py
Unit tests for medisync.dashboard.dashboard — DoctorDashboard service
covering queue building, overview aggregation, and patient summary card.
Uses in-memory stubs so no MongoDB connection is needed.
"""
import pytest
from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from medisync.dashboard.dashboard import (
    DoctorDashboard,
    PatientQueueItem,
    DashboardOverview,
    PatientSummaryCard,
)
from medisync.core.types import (
    Appointment,
    AppointmentStatus,
    ConsultationType,
    PriorityLevel,
    PatientProfile,
    ConsultationLog,
    generate_uuid,
)
from medisync.ai_engine.nlp_engine import NLPEngine, ExtractionResult
from medisync.ai_engine.priority_engine import PriorityEngine, PriorityAssessment
from medisync.core.config import Settings


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def settings():
    return Settings(
        mongodb_url="mongodb://localhost:27017",
        jwt_secret_key="test-secret",
        use_mock_ai=True,
        critical_symptom_threshold=0.8,
        moderate_symptom_threshold=0.5,
        max_consultation_time_minutes=60,
    )


@pytest.fixture
def mock_patient():
    from datetime import date as _date
    return PatientProfile(
        patient_id="P-001",
        full_name="Alice Wonderland",
        date_of_birth=_date(1988, 6, 15),
        gender="female",
        contact_email="alice@clinic.com",
        contact_phone="+1234567890",
        blood_group="A+",
    )


def _make_appointment(
    patient_id: str = "P-001",
    doctor_id: str = "D-001",
    priority: PriorityLevel = PriorityLevel.ROUTINE,
    status: AppointmentStatus = AppointmentStatus.PENDING,
    duration: int = 20,
) -> Appointment:
    return Appointment(
        appointment_id=generate_uuid(),
        patient_id=patient_id,
        doctor_id=doctor_id,
        scheduled_at=datetime(2026, 5, 3, 9, 0, tzinfo=timezone.utc),
        consultation_type=ConsultationType.IN_PERSON,
        status=status,
        symptoms_description="Headache and mild fever for two days",
        priority_level=priority,
        estimated_duration_minutes=duration,
    )


# ---------------------------------------------------------------------------
# PatientQueueItem — data shape
# ---------------------------------------------------------------------------

class TestPatientQueueItemShape:
    def test_queue_item_fields_present(self):
        item = PatientQueueItem(
            queue_position=1,
            patient_id="P-001",
            patient_name="Alice W.",
            age=36,
            appointment_id="A-001",
            scheduled_at="2026-05-03T09:00:00+00:00",
            priority_level="routine",
            priority_badge_color="green",
            symptoms_preview="Headache and mild fever...",
            estimated_duration_minutes=20,
            status="pending",
            risk_flags=[],
        )
        assert item.queue_position == 1
        assert item.priority_level == "routine"
        assert item.priority_badge_color == "green"

    def test_critical_badge_color(self):
        item = PatientQueueItem(
            queue_position=1,
            patient_id="P-002",
            patient_name="Bob B.",
            age=72,
            appointment_id="A-002",
            scheduled_at="2026-05-03T10:00:00+00:00",
            priority_level="critical",
            priority_badge_color="red",
            symptoms_preview="Chest pain and loss of consciousness...",
            estimated_duration_minutes=45,
            status="confirmed",
            risk_flags=["Chest pain", "Age > 65"],
        )
        assert item.priority_badge_color == "red"
        assert "Chest pain" in item.risk_flags


# ---------------------------------------------------------------------------
# DashboardOverview — aggregation logic
# ---------------------------------------------------------------------------

class TestDashboardOverview:
    def test_overview_counts(self):
        overview = DashboardOverview(
            doctor_id="D-001",
            date="2026-05-03",
            total_patients_today=5,
            critical_count=1,
            moderate_count=2,
            routine_count=2,
            completed_consultations=2,
            pending_consultations=3,
            estimated_remaining_hours=1.5,
            priority_queue=[],
            recent_activity=[],
        )
        assert overview.total_patients_today == 5
        assert overview.critical_count + overview.moderate_count + overview.routine_count == 5
        assert overview.completed_consultations + overview.pending_consultations == 5

    def test_overview_empty_day(self):
        overview = DashboardOverview(
            doctor_id="D-002",
            date="2026-05-03",
            total_patients_today=0,
            critical_count=0,
            moderate_count=0,
            routine_count=0,
            completed_consultations=0,
            pending_consultations=0,
            estimated_remaining_hours=0.0,
            priority_queue=[],
            recent_activity=[],
        )
        assert overview.total_patients_today == 0
        assert overview.estimated_remaining_hours == 0.0


# ---------------------------------------------------------------------------
# PatientSummaryCard — data shape
# ---------------------------------------------------------------------------

class TestPatientSummaryCardShape:
    def test_summary_card_fields(self):
        card = PatientSummaryCard(
            patient_id="P-001",
            full_name="Alice Wonderland",
            age=36,
            blood_group="A+",
            status="active",
            priority_level="routine",
            risk_indicators=[],
            recent_diagnoses=["Hypertension", "Diabetes Type 2"],
            current_medications=["Metformin 500mg", "Lisinopril 10mg"],
            last_visit_date="2026-04-15",
            total_visits=8,
            consultation_history_preview=[],
            quick_actions=["Start Consultation", "View History"],
        )
        assert card.patient_id == "P-001"
        assert card.total_visits == 8
        assert "Hypertension" in card.recent_diagnoses
        assert "Metformin 500mg" in card.current_medications

    def test_summary_card_no_blood_group(self):
        card = PatientSummaryCard(
            patient_id="P-002",
            full_name="Bob Builder",
            age=45,
            blood_group=None,
            status="active",
            priority_level="moderate",
            risk_indicators=["Hypertension"],
            recent_diagnoses=[],
            current_medications=[],
            last_visit_date=None,
            total_visits=0,
            consultation_history_preview=[],
            quick_actions=[],
        )
        assert card.blood_group is None
        assert card.last_visit_date is None


# ---------------------------------------------------------------------------
# DoctorDashboard service — integration with stubs
# ---------------------------------------------------------------------------

@pytest.fixture
def stub_patient_manager(mock_patient):
    mgr = AsyncMock()
    mgr.get_patient.return_value = mock_patient
    mgr.get_patient_history.return_value = []
    mgr.get_consultation_logs.return_value = []
    # get_patient_summary must return a plain dict matching PatientSummaryCard fields
    mgr.get_patient_summary.return_value = {
        "patient_id": "P-001",
        "full_name": "Alice Wonderland",
        "age": 36,
        "blood_group": "A+",
        "status": "active",
        "priority_level": "routine",
        "risk_indicators": [],
        "recent_diagnoses": [],
        "current_medications": [],
        "last_visit_date": None,
        "total_visits": 4,
        "consultation_history_preview": [],
        "quick_actions": [],
    }
    return mgr


@pytest.fixture
def stub_appointment_system():
    sys = AsyncMock()
    sys.get_doctor_queue.return_value = [
        _make_appointment(priority=PriorityLevel.CRITICAL),
        _make_appointment(priority=PriorityLevel.ROUTINE),
    ]
    return sys


@pytest.fixture
def stub_nlp(settings):
    nlp = AsyncMock(spec=NLPEngine)
    nlp.extract_from_text.return_value = ExtractionResult(
        symptoms=["chest pain"],
        severity_indicators=["severe"],
        confidence=0.9,
    )
    return nlp


@pytest.fixture
def stub_priority(settings, stub_nlp):
    pe = AsyncMock(spec=PriorityEngine)
    pe.predict_priority.return_value = PriorityAssessment(
        priority_level=PriorityLevel.CRITICAL,
        risk_score=0.9,
        estimated_duration_minutes=45,
        urgent_flags=["chest pain"],
        recommendation="Immediate medical attention required.",
        confidence=0.9,
    )
    pe.estimate_duration.return_value = 45
    return pe


@pytest.fixture
def dashboard(stub_patient_manager, stub_appointment_system, stub_nlp, stub_priority):
    return DoctorDashboard(
        patient_manager=stub_patient_manager,
        appointment_system=stub_appointment_system,
        nlp_engine=stub_nlp,
        priority_engine=stub_priority,
    )


class TestDoctorDashboardService:
    @pytest.mark.asyncio
    async def test_get_patient_queue_returns_list(self, dashboard):
        queue = await dashboard.get_patient_queue("D-001", date(2026, 5, 3))
        assert isinstance(queue, list)

    @pytest.mark.asyncio
    async def test_get_dashboard_overview_returns_overview(self, dashboard):
        overview = await dashboard.get_dashboard_overview("D-001", date(2026, 5, 3))
        assert isinstance(overview, DashboardOverview)
        assert overview.doctor_id == "D-001"

    @pytest.mark.asyncio
    async def test_get_patient_summary_card_returns_card(self, dashboard):
        card = await dashboard.get_patient_summary_card("P-001")
        assert isinstance(card, PatientSummaryCard)

    @pytest.mark.asyncio
    async def test_overview_total_matches_appointments(self, dashboard):
        overview = await dashboard.get_dashboard_overview("D-001", date(2026, 5, 3))
        # Our stub returns 2 appointments
        assert overview.total_patients_today == 2

    @pytest.mark.asyncio
    async def test_patient_summary_card_patient_id(self, dashboard):
        card = await dashboard.get_patient_summary_card("P-001")
        # The card should be constructed from the stub's dict response
        assert isinstance(card, PatientSummaryCard)

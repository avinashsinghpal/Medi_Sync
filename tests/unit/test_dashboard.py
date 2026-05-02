"""
tests/unit/test_dashboard.py

Unit tests for DoctorDashboard (SPEC_dashboard.md).

All tests run without Docker or a real MongoDB instance — dependencies
(PatientManager, AppointmentSystem) are replaced by lightweight in-memory
fakes that mirror their public interfaces exactly.
"""
from __future__ import annotations

import pytest
from datetime import datetime, date, timezone, timedelta
from typing import Optional

from medisync.core.types import (
    Appointment, AppointmentStatus, ConsultationType,
    PriorityLevel, PatientProfile, PatientStatus, ConsultationLog,
    generate_uuid, utc_now,
)
from medisync.core.config import Settings
from medisync.core.errors import NLPExtractionError
from medisync.ai_engine.nlp_engine import NLPEngine
from medisync.ai_engine.priority_engine import PriorityEngine
from medisync.dashboard.dashboard import (
    DoctorDashboard,
    DashboardOverview,
    PatientQueueItem,
    PatientSummaryCard,
    ConsultationResult,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_appointment(
    appointment_id: str,
    patient_id: str,
    doctor_id: str,
    priority: PriorityLevel,
    status: AppointmentStatus = AppointmentStatus.PENDING,
    symptoms: str = "mild headache",
    duration: int = 15,
    offset_hours: int = 1,
) -> Appointment:
    return Appointment(
        appointment_id=appointment_id,
        patient_id=patient_id,
        doctor_id=doctor_id,
        scheduled_at=utc_now() + timedelta(hours=offset_hours),
        consultation_type=ConsultationType.IN_PERSON,
        status=status,
        symptoms_description=symptoms,
        priority_level=priority,
        estimated_duration_minutes=duration,
        notes=None,
        created_at=utc_now(),
    )


def _make_patient(patient_id: str = "P-TEST001", name: str = "Jane Doe", age_years: int = 40) -> PatientProfile:
    dob = date(2025 - age_years, 1, 1)
    now = utc_now()
    return PatientProfile(
        patient_id=patient_id,
        full_name=name,
        date_of_birth=dob,
        gender="female",
        blood_group="O+",
        contact_email="jane@example.com",
        contact_phone="+1234567890",
        status=PatientStatus.ACTIVE,
        created_at=now,
        updated_at=now,
        metadata={},
    )


# ---------------------------------------------------------------------------
# In-memory fakes — mirror public service interfaces, no MongoDB needed
# ---------------------------------------------------------------------------

class FakePatientManager:
    """In-memory PatientManager for unit tests."""

    def __init__(self, profile: PatientProfile, logs: list[ConsultationLog] | None = None):
        self._profile = profile
        self._logs = logs or []

    async def get_patient(self, patient_id: str) -> PatientProfile:
        return self._profile

    async def get_patient_summary(self, patient_id: str) -> dict:
        return {
            "patient_id":          self._profile.patient_id,
            "full_name":           self._profile.full_name,
            "age":                 self._profile.age,
            "blood_group":         self._profile.blood_group,
            "status":              self._profile.status.value,
            "total_records":       3,
            "recent_diagnoses":    ["Hypertension"],
            "current_medications": ["Aspirin 75mg"],
            "last_visit":          "2024-01-15T10:00:00+00:00",
            "priority_level":      "moderate",
        }

    async def get_consultation_logs(self, patient_id: str, limit: int = 10) -> list[ConsultationLog]:
        return self._logs[:limit]


class FakeAppointmentSystem:
    """In-memory AppointmentSystem for unit tests."""

    def __init__(self, appointments: list[Appointment]):
        self._appointments = {a.appointment_id: a for a in appointments}

    async def get_doctor_queue(self, doctor_id: str, target_date: date) -> list[Appointment]:
        """Return appointments sorted CRITICAL → MODERATE → ROUTINE, ties by scheduled_at."""
        _SORT = {PriorityLevel.CRITICAL: 0, PriorityLevel.MODERATE: 1, PriorityLevel.ROUTINE: 2}
        active = [
            a for a in self._appointments.values()
            if a.doctor_id == doctor_id
            and a.status not in (AppointmentStatus.CANCELLED,)
        ]
        return sorted(active, key=lambda a: (_SORT.get(a.priority_level, 2), a.scheduled_at))

    async def get_appointment(self, appointment_id: str) -> Appointment:
        from medisync.core.errors import AppointmentNotFoundError
        appt = self._appointments.get(appointment_id)
        if appt is None:
            raise AppointmentNotFoundError(f"Appointment {appointment_id} not found")
        return appt


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def real_settings() -> Settings:
    """Settings with mocks DISABLED — exercises the real rule-based NLP engine."""
    return Settings(
        use_mock_ai=False,
        mongodb_url="mongodb://localhost:27017",
        jwt_secret_key="test-secret-key-32-characters-ok",
    )


@pytest.fixture
def mock_settings() -> Settings:
    """Settings with mocks ENABLED — fixed extraction output."""
    return Settings(
        use_mock_ai=True,
        mongodb_url="mongodb://localhost:27017",
        jwt_secret_key="test-secret-key-32-characters-ok",
    )


@pytest.fixture
def real_nlp(real_settings: Settings) -> NLPEngine:
    return NLPEngine(real_settings)


@pytest.fixture
def mock_nlp(mock_settings: Settings) -> NLPEngine:
    return NLPEngine(mock_settings)


@pytest.fixture
def real_priority(real_nlp: NLPEngine, real_settings: Settings) -> PriorityEngine:
    return PriorityEngine(real_nlp, real_settings)


@pytest.fixture
def mock_priority(mock_nlp: NLPEngine, mock_settings: Settings) -> PriorityEngine:
    return PriorityEngine(mock_nlp, mock_settings)


@pytest.fixture
def sample_patient() -> PatientProfile:
    return _make_patient("P-DASH001", "Alice Smith", 50)


@pytest.fixture
def mixed_appointments(sample_patient: PatientProfile) -> list[Appointment]:
    """Three appointments with different priorities for ordering tests."""
    return [
        _make_appointment("APT-1", sample_patient.patient_id, "DOC-1",
                          PriorityLevel.ROUTINE,   offset_hours=3),
        _make_appointment("APT-2", sample_patient.patient_id, "DOC-1",
                          PriorityLevel.CRITICAL,  offset_hours=2, symptoms="severe chest pain and dizziness",  duration=30),
        _make_appointment("APT-3", sample_patient.patient_id, "DOC-1",
                          PriorityLevel.MODERATE,  offset_hours=1, symptoms="persistent headache and fatigue", duration=20),
    ]


@pytest.fixture
def dashboard_real(sample_patient, mixed_appointments, real_nlp, real_priority) -> DoctorDashboard:
    """Dashboard wired to real NLP/priority engines with in-memory services."""
    return DoctorDashboard(
        patient_manager=FakePatientManager(sample_patient),
        appointment_system=FakeAppointmentSystem(mixed_appointments),
        nlp_engine=real_nlp,
        priority_engine=real_priority,
    )


@pytest.fixture
def dashboard_mock(sample_patient, mixed_appointments, mock_nlp, mock_priority) -> DoctorDashboard:
    """Dashboard wired to mock NLP/priority engines — deterministic output."""
    return DoctorDashboard(
        patient_manager=FakePatientManager(sample_patient),
        appointment_system=FakeAppointmentSystem(mixed_appointments),
        nlp_engine=mock_nlp,
        priority_engine=mock_priority,
    )


# ---------------------------------------------------------------------------
# Tests: get_patient_queue
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_patient_queue_critical_first(dashboard_real: DoctorDashboard):
    """CRITICAL appointments must appear before MODERATE and ROUTINE."""
    queue = await dashboard_real.get_patient_queue("DOC-1", utc_now().date())

    assert len(queue) == 3
    assert queue[0].priority_level == PriorityLevel.CRITICAL.value
    assert queue[1].priority_level == PriorityLevel.MODERATE.value
    assert queue[2].priority_level == PriorityLevel.ROUTINE.value


@pytest.mark.asyncio
async def test_patient_queue_positions_sequential(dashboard_real: DoctorDashboard):
    """queue_position must start at 1 and increment by 1."""
    queue = await dashboard_real.get_patient_queue("DOC-1", utc_now().date())
    positions = [item.queue_position for item in queue]
    assert positions == list(range(1, len(queue) + 1))


@pytest.mark.asyncio
async def test_patient_queue_badge_colors(dashboard_real: DoctorDashboard):
    """priority_badge_color must be 'red' | 'yellow' | 'green' per UX invariant."""
    queue = await dashboard_real.get_patient_queue("DOC-1", utc_now().date())
    color_map = {item.priority_level: item.priority_badge_color for item in queue}
    assert color_map[PriorityLevel.CRITICAL.value] == "red"
    assert color_map[PriorityLevel.MODERATE.value] == "yellow"
    assert color_map[PriorityLevel.ROUTINE.value]  == "green"


@pytest.mark.asyncio
async def test_patient_queue_symptoms_preview_truncated(real_settings):
    """symptoms_preview must be truncated to 100 chars + '...' per UX invariant."""
    long_symptom = "a" * 120
    appt = _make_appointment("APT-LONG", "P-001", "DOC-1", PriorityLevel.ROUTINE,
                              symptoms=long_symptom)
    patient = _make_patient("P-001")
    dashboard = DoctorDashboard(
        patient_manager=FakePatientManager(patient),
        appointment_system=FakeAppointmentSystem([appt]),
        nlp_engine=NLPEngine(real_settings),
        priority_engine=PriorityEngine(NLPEngine(real_settings), real_settings),
    )
    queue = await dashboard.get_patient_queue("DOC-1", utc_now().date())
    assert len(queue[0].symptoms_preview) == 103  # 100 chars + "..."
    assert queue[0].symptoms_preview.endswith("...")


@pytest.mark.asyncio
async def test_patient_queue_all_iso8601_datetimes(dashboard_real: DoctorDashboard):
    """All datetime fields in responses must be ISO 8601 strings."""
    queue = await dashboard_real.get_patient_queue("DOC-1", utc_now().date())
    for item in queue:
        # Should parse without error
        datetime.fromisoformat(item.scheduled_at)


@pytest.mark.asyncio
async def test_patient_queue_empty_when_no_appointments(sample_patient, real_settings):
    """Queue must be [] (not null) when no appointments exist."""
    dashboard = DoctorDashboard(
        patient_manager=FakePatientManager(sample_patient),
        appointment_system=FakeAppointmentSystem([]),
        nlp_engine=NLPEngine(real_settings),
        priority_engine=PriorityEngine(NLPEngine(real_settings), real_settings),
    )
    queue = await dashboard.get_patient_queue("DOC-1", utc_now().date())
    assert queue == []


# ---------------------------------------------------------------------------
# Tests: get_dashboard_overview
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_dashboard_overview_correct_counts(dashboard_real: DoctorDashboard):
    """DashboardOverview must reflect correct critical / moderate / routine counts."""
    overview = await dashboard_real.get_dashboard_overview("DOC-1", utc_now().date())

    assert isinstance(overview, DashboardOverview)
    assert overview.total_patients_today == 3
    assert overview.critical_count == 1
    assert overview.moderate_count == 1
    assert overview.routine_count  == 1


@pytest.mark.asyncio
async def test_dashboard_overview_priority_queue_ordered(dashboard_real: DoctorDashboard):
    """The embedded priority_queue must be ordered CRITICAL → MODERATE → ROUTINE."""
    overview = await dashboard_real.get_dashboard_overview("DOC-1", utc_now().date())
    levels = [item.priority_level for item in overview.priority_queue]
    assert levels[0] == PriorityLevel.CRITICAL.value


@pytest.mark.asyncio
async def test_dashboard_overview_date_is_iso(dashboard_real: DoctorDashboard):
    """The 'date' field must be an ISO date string."""
    today = utc_now().date()
    overview = await dashboard_real.get_dashboard_overview("DOC-1", today)
    assert overview.date == today.isoformat()


@pytest.mark.asyncio
async def test_dashboard_overview_recent_activity_is_list(dashboard_real: DoctorDashboard):
    """recent_activity must be a list (even if empty), never null."""
    overview = await dashboard_real.get_dashboard_overview("DOC-1", utc_now().date())
    assert isinstance(overview.recent_activity, list)


@pytest.mark.asyncio
async def test_dashboard_overview_estimated_hours_non_negative(dashboard_real: DoctorDashboard):
    """estimated_remaining_hours must be >= 0."""
    overview = await dashboard_real.get_dashboard_overview("DOC-1", utc_now().date())
    assert overview.estimated_remaining_hours >= 0.0


# ---------------------------------------------------------------------------
# Tests: get_patient_summary_card
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_patient_summary_card_fields(dashboard_real: DoctorDashboard, sample_patient: PatientProfile):
    """PatientSummaryCard must include all required spec fields."""
    card = await dashboard_real.get_patient_summary_card(sample_patient.patient_id)

    assert isinstance(card, PatientSummaryCard)
    assert card.patient_id    == sample_patient.patient_id
    assert card.full_name     == sample_patient.full_name
    assert card.age           == sample_patient.age
    assert card.blood_group   == "O+"
    assert card.status        == PatientStatus.ACTIVE.value
    assert isinstance(card.risk_indicators,             list)
    assert isinstance(card.recent_diagnoses,            list)
    assert isinstance(card.current_medications,         list)
    assert isinstance(card.consultation_history_preview, list)


@pytest.mark.asyncio
async def test_patient_summary_card_quick_actions(dashboard_real: DoctorDashboard, sample_patient: PatientProfile):
    """quick_actions must contain exactly the three stable identifiers from the spec."""
    card = await dashboard_real.get_patient_summary_card(sample_patient.patient_id)
    assert set(card.quick_actions) == {"start_consultation", "view_history", "add_record"}


@pytest.mark.asyncio
async def test_patient_summary_card_consultation_history_preview(
    sample_patient: PatientProfile,
    real_settings: Settings,
    real_nlp: NLPEngine,
    real_priority: PriorityEngine,
):
    """consultation_history_preview must include the last 3 logs."""
    log = ConsultationLog(
        consultation_id=generate_uuid(),
        patient_id=sample_patient.patient_id,
        doctor_id="DOC-1",
        appointment_id="APT-X",
        started_at=utc_now() - timedelta(days=5),
        ended_at=utc_now() - timedelta(days=5) + timedelta(minutes=20),
        raw_transcript="Patient has chest pain and fever.",
        notes="Routine check.",
        priority_level=PriorityLevel.MODERATE,
        extracted_symptoms=["chest pain"],
        extracted_medications=[],
        extracted_dosages={},
        estimated_duration_minutes=20,
    )
    dashboard = DoctorDashboard(
        patient_manager=FakePatientManager(sample_patient, logs=[log]),
        appointment_system=FakeAppointmentSystem([]),
        nlp_engine=real_nlp,
        priority_engine=real_priority,
    )
    card = await dashboard.get_patient_summary_card(sample_patient.patient_id)

    assert len(card.consultation_history_preview) == 1
    entry = card.consultation_history_preview[0]
    assert "date" in entry
    assert "priority_level" in entry
    assert "notes_preview" in entry


# ---------------------------------------------------------------------------
# Tests: process_consultation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_process_consultation_text_input(
    sample_patient: PatientProfile,
    real_settings: Settings,
    real_nlp: NLPEngine,
    real_priority: PriorityEngine,
):
    """process_consultation with text_input returns a valid ConsultationResult."""
    appt = _make_appointment(
        "APT-CONSULT", sample_patient.patient_id, "DOC-1",
        PriorityLevel.ROUTINE,
        symptoms="Patient reports chest pain and shortness of breath.",
        duration=20,
    )
    dashboard = DoctorDashboard(
        patient_manager=FakePatientManager(sample_patient),
        appointment_system=FakeAppointmentSystem([appt]),
        nlp_engine=real_nlp,
        priority_engine=real_priority,
    )
    result = await dashboard.process_consultation(
        appointment_id="APT-CONSULT",
        audio_data=None,
        text_input="Patient has severe chest pain and dizziness for two days.",
    )

    assert isinstance(result, ConsultationResult)
    assert result.patient_id       == sample_patient.patient_id
    assert result.doctor_id        == "DOC-1"
    assert result.consultation_id  # non-empty UUID
    assert result.transcript is None             # no audio provided
    assert result.consultation_summary           # non-empty string
    assert isinstance(result.extracted_data, dict)
    assert "symptoms" in result.extracted_data
    assert isinstance(result.structured_output, dict)
    # Verify structured output fields per spec
    assert result.structured_output["patient_id"] == sample_patient.patient_id
    assert "symptoms"          in result.structured_output
    assert "risk_level"        in result.structured_output
    assert "medications"       in result.structured_output
    assert "consultation_time" in result.structured_output
    assert "priority"          in result.structured_output


@pytest.mark.asyncio
async def test_process_consultation_audio_input(
    sample_patient: PatientProfile,
    mock_settings: Settings,
    mock_nlp: NLPEngine,
    mock_priority: PriorityEngine,
):
    """process_consultation with audio_data sets transcript (stub fallback acceptable)."""
    appt = _make_appointment("APT-AUDIO", sample_patient.patient_id, "DOC-1",
                              PriorityLevel.ROUTINE)
    dashboard = DoctorDashboard(
        patient_manager=FakePatientManager(sample_patient),
        appointment_system=FakeAppointmentSystem([appt]),
        nlp_engine=mock_nlp,
        priority_engine=mock_priority,
    )
    result = await dashboard.process_consultation(
        appointment_id="APT-AUDIO",
        audio_data=b"fake-audio-bytes",
        text_input=None,
    )

    assert isinstance(result, ConsultationResult)
    # transcript must be set (stub placeholder is acceptable)
    assert result.transcript is not None


@pytest.mark.asyncio
async def test_process_consultation_both_none_raises(
    sample_patient: PatientProfile,
    real_settings: Settings,
    real_nlp: NLPEngine,
    real_priority: PriorityEngine,
):
    """process_consultation with no audio AND no text MUST raise NLPExtractionError."""
    appt = _make_appointment("APT-EMPTY", sample_patient.patient_id, "DOC-1",
                              PriorityLevel.ROUTINE)
    dashboard = DoctorDashboard(
        patient_manager=FakePatientManager(sample_patient),
        appointment_system=FakeAppointmentSystem([appt]),
        nlp_engine=real_nlp,
        priority_engine=real_priority,
    )
    with pytest.raises(NLPExtractionError):
        await dashboard.process_consultation(
            appointment_id="APT-EMPTY",
            audio_data=None,
            text_input=None,
        )


@pytest.mark.asyncio
async def test_process_consultation_priority_level_is_string(
    sample_patient: PatientProfile,
    real_settings: Settings,
    real_nlp: NLPEngine,
    real_priority: PriorityEngine,
):
    """ConsultationResult.priority_level must be a lowercase string value."""
    appt = _make_appointment("APT-PRI", sample_patient.patient_id, "DOC-1",
                              PriorityLevel.ROUTINE, symptoms="mild cough for three days.")
    dashboard = DoctorDashboard(
        patient_manager=FakePatientManager(sample_patient),
        appointment_system=FakeAppointmentSystem([appt]),
        nlp_engine=real_nlp,
        priority_engine=real_priority,
    )
    result = await dashboard.process_consultation(
        appointment_id="APT-PRI",
        audio_data=None,
        text_input="Patient has mild cough for three days and no fever.",
    )
    valid_levels = {"critical", "moderate", "routine"}
    assert result.priority_level in valid_levels


# ---------------------------------------------------------------------------
# Tests: NLP caching (performance tuning)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_nlp_cache_hit(real_nlp: NLPEngine):
    """Second call with identical text must return the cached object (same identity)."""
    text = "Patient has severe chest pain and persistent coughing."
    result1 = await real_nlp.extract_from_text(text)
    result2 = await real_nlp.extract_from_text(text)
    assert result1 is result2   # identical object — cache hit


@pytest.mark.asyncio
async def test_nlp_cache_max_size_eviction(real_settings: Settings):
    """Cache must not grow beyond _NLP_CACHE_MAX_SIZE entries."""
    from medisync.ai_engine.nlp_engine import _NLP_CACHE_MAX_SIZE
    engine = NLPEngine(real_settings)
    # Fill cache with distinct texts (pad to ≥ 10 chars each)
    for i in range(_NLP_CACHE_MAX_SIZE + 5):
        text = f"patient reports symptom number {i:04d}"
        try:
            await engine.extract_from_text(text)
        except Exception:
            pass
    assert len(engine._cache) <= _NLP_CACHE_MAX_SIZE


@pytest.mark.asyncio
async def test_nlp_clear_cache(real_nlp: NLPEngine):
    """clear_cache() must empty the internal cache."""
    await real_nlp.extract_from_text("Patient has severe chest pain and fever.")
    assert len(real_nlp._cache) > 0
    real_nlp.clear_cache()
    assert len(real_nlp._cache) == 0


# ---------------------------------------------------------------------------
# Tests: UX invariants
# ---------------------------------------------------------------------------

def test_badge_color_mapping():
    """_badge_color must map priorities to CSS-compatible color strings."""
    from medisync.dashboard.dashboard import _badge_color
    assert _badge_color(PriorityLevel.CRITICAL) == "red"
    assert _badge_color(PriorityLevel.MODERATE)  == "yellow"
    assert _badge_color(PriorityLevel.ROUTINE)   == "green"


def test_symptoms_preview_exact_100_chars():
    """A 100-char string must NOT be truncated."""
    from medisync.dashboard.dashboard import _symptoms_preview
    text = "x" * 100
    assert _symptoms_preview(text) == text
    assert not _symptoms_preview(text).endswith("...")


def test_symptoms_preview_101_chars_truncated():
    """A 101-char string must be truncated to 100 + '...'."""
    from medisync.dashboard.dashboard import _symptoms_preview
    text = "y" * 101
    preview = _symptoms_preview(text)
    assert len(preview) == 103
    assert preview.endswith("...")

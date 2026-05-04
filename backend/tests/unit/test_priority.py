"""
tests/unit/test_priority.py
Unit tests for medisync.ai_engine.priority_engine — risk scoring,
priority level classification, duration estimation, and queue ordering.
"""
import pytest
from medisync.ai_engine.priority_engine import PriorityEngine, PriorityAssessment
from medisync.ai_engine.nlp_engine import NLPEngine
from medisync.core.types import PriorityLevel
from medisync.core.config import Settings


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def settings():
    return Settings(
        mongodb_url="mongodb://localhost:27017",
        jwt_secret_key="test-secret",
        use_mock_ai=False,
        critical_symptom_threshold=0.8,
        moderate_symptom_threshold=0.5,
        max_consultation_time_minutes=60,
        default_consultation_time_minutes=15,
    )

@pytest.fixture
def nlp(settings):
    return NLPEngine(settings)

@pytest.fixture
def engine(nlp, settings):
    return PriorityEngine(nlp, settings)


# ---------------------------------------------------------------------------
# predict_priority — PriorityLevel classification
# ---------------------------------------------------------------------------

class TestPriorityClassification:
    @pytest.mark.asyncio
    async def test_critical_symptoms_yield_critical_priority(self, engine):
        assessment = await engine.predict_priority(
            "Patient presents with severe chest pain and loss of consciousness"
        )
        assert assessment.priority_level == PriorityLevel.CRITICAL

    @pytest.mark.asyncio
    async def test_routine_symptoms_yield_routine_priority(self, engine):
        assessment = await engine.predict_priority(
            "Patient has mild headache and slight runny nose since this morning"
        )
        assert assessment.priority_level in (PriorityLevel.ROUTINE, PriorityLevel.MODERATE)

    @pytest.mark.asyncio
    async def test_returns_priority_assessment_dataclass(self, engine):
        result = await engine.predict_priority(
            "Patient complains of persistent fatigue and weakness for one week"
        )
        assert isinstance(result, PriorityAssessment)
        assert isinstance(result.priority_level, PriorityLevel)
        assert 0.0 <= result.risk_score <= 1.0

    @pytest.mark.asyncio
    async def test_loss_of_consciousness_is_critical(self, engine):
        assessment = await engine.predict_priority(
            "Patient experienced loss of consciousness and severe chest pain episode"
        )
        assert assessment.priority_level == PriorityLevel.CRITICAL

    @pytest.mark.asyncio
    async def test_high_age_increases_risk(self, engine):
        """Patients over 65 should have higher risk score than younger patients."""
        old_patient = {"age": 70}
        young_patient = {"age": 30}
        text = "Patient reports mild chest discomfort and some fatigue"
        a_old = await engine.predict_priority(text, old_patient)
        a_young = await engine.predict_priority(text, young_patient)
        assert a_old.risk_score >= a_young.risk_score

    @pytest.mark.asyncio
    async def test_cardiac_history_adds_risk_factor(self, engine):
        history = {"prior_cardiac_history": True}
        assessment = await engine.predict_priority(
            "Patient reports mild fatigue and occasional dizziness at rest",
            history,
        )
        assert "Prior cardiac history" in assessment.risk_factors

    @pytest.mark.asyncio
    async def test_confidence_is_positive(self, engine):
        result = await engine.predict_priority(
            "Patient has persistent cough and mild fever for several days"
        )
        assert result.confidence > 0.0

    @pytest.mark.asyncio
    async def test_risk_score_bounded_zero_to_one(self, engine):
        result = await engine.predict_priority(
            "Severe acute crushing chest pain radiating to left arm now"
        )
        assert 0.0 <= result.risk_score <= 1.0


# ---------------------------------------------------------------------------
# estimate_duration
# ---------------------------------------------------------------------------

class TestDurationEstimation:
    @pytest.mark.asyncio
    async def test_duration_is_positive_integer(self, engine):
        duration = await engine.estimate_duration(
            "Patient complains of mild headache and fatigue since morning"
        )
        assert isinstance(duration, int)
        assert duration > 0

    @pytest.mark.asyncio
    async def test_critical_case_longer_duration(self, engine):
        critical = await engine.estimate_duration(
            "Severe crushing chest pain with loss of consciousness emergency"
        )
        routine = await engine.estimate_duration(
            "Mild runny nose since this morning nothing serious at all"
        )
        assert critical >= routine

    @pytest.mark.asyncio
    async def test_duration_does_not_exceed_max(self, engine):
        duration = await engine.estimate_duration(
            "Severe acute crushing chest pain radiating to left arm"
        )
        assert duration <= 60  # max_consultation_time_minutes

    @pytest.mark.asyncio
    async def test_no_history_adds_new_patient_buffer(self, engine):
        with_history = await engine.estimate_duration(
            "Patient reports mild headache and slight dizziness now", {}
        )
        no_history = await engine.estimate_duration(
            "Patient reports mild headache and slight dizziness now", None
        )
        # No-history path adds +5 min buffer for new patients
        assert no_history >= with_history


# ---------------------------------------------------------------------------
# get_queue_order
# ---------------------------------------------------------------------------

class TestQueueOrdering:
    @pytest.mark.asyncio
    async def test_critical_appears_first(self, engine):
        patients = [
            {"patient_id": "P-1", "priority_level": PriorityLevel.ROUTINE,   "scheduled_at": "2026-05-03T09:00:00"},
            {"patient_id": "P-2", "priority_level": PriorityLevel.CRITICAL,  "scheduled_at": "2026-05-03T09:30:00"},
            {"patient_id": "P-3", "priority_level": PriorityLevel.MODERATE,  "scheduled_at": "2026-05-03T08:30:00"},
        ]
        ordered = await engine.get_queue_order(patients)
        assert ordered[0]["patient_id"] == "P-2"
        assert ordered[0]["queue_position"] == 1

    @pytest.mark.asyncio
    async def test_moderate_before_routine(self, engine):
        patients = [
            {"patient_id": "P-A", "priority_level": PriorityLevel.ROUTINE,   "scheduled_at": "2026-05-03T08:00:00"},
            {"patient_id": "P-B", "priority_level": PriorityLevel.MODERATE,  "scheduled_at": "2026-05-03T09:00:00"},
        ]
        ordered = await engine.get_queue_order(patients)
        assert ordered[0]["patient_id"] == "P-B"

    @pytest.mark.asyncio
    async def test_queue_positions_are_sequential(self, engine):
        patients = [
            {"patient_id": "P-X", "priority_level": PriorityLevel.ROUTINE,  "scheduled_at": "2026-05-03T10:00:00"},
            {"patient_id": "P-Y", "priority_level": PriorityLevel.CRITICAL, "scheduled_at": "2026-05-03T11:00:00"},
        ]
        ordered = await engine.get_queue_order(patients)
        positions = [p["queue_position"] for p in ordered]
        assert positions == list(range(1, len(patients) + 1))

    @pytest.mark.asyncio
    async def test_string_priority_levels_handled(self, engine):
        """Queue ordering must handle string priority values from MongoDB docs."""
        patients = [
            {"patient_id": "P-S1", "priority_level": "routine",  "scheduled_at": "2026-05-03T08:00:00"},
            {"patient_id": "P-S2", "priority_level": "critical", "scheduled_at": "2026-05-03T09:00:00"},
        ]
        ordered = await engine.get_queue_order(patients)
        assert ordered[0]["patient_id"] == "P-S2"

    @pytest.mark.asyncio
    async def test_empty_queue_returns_empty_list(self, engine):
        result = await engine.get_queue_order([])
        assert result == []

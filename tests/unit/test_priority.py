import pytest
from datetime import datetime, timezone
from medisync.core.types import PriorityLevel
from medisync.core.config import Settings
from medisync.ai_engine.nlp_engine import NLPEngine
from medisync.ai_engine.priority_engine import PriorityEngine

@pytest.fixture
def real_settings():
    return Settings(use_mock_ai=False, mongodb_url="mongodb://localhost", jwt_secret_key="secret")

@pytest.fixture
def engine(real_settings):
    nlp = NLPEngine(real_settings)
    return PriorityEngine(nlp, real_settings)

@pytest.mark.asyncio
async def test_critical_detection(engine):
    res = await engine.predict_priority("Patient has severe chest pain")
    assert res.priority_level == PriorityLevel.CRITICAL
    assert "chest pain" in res.urgent_flags

@pytest.mark.asyncio
async def test_routine_detection(engine):
    # Missing explicit severity, but has symptoms -> might be ROUTINE or MODERATE
    # Our simple logic sets symptom_score=0.3 if symptom exists but not severe
    # 0.6 * 0.3 = 0.18. Thresholds: critical=0.8, moderate=0.5 -> ROUTINE
    res = await engine.predict_priority("Patient has a mild headache", patient_history={})
    assert res.priority_level == PriorityLevel.ROUTINE

@pytest.mark.asyncio
async def test_history_boost(engine):
    # Symptom score for generic symptom = 0.3.
    # Patient has cardiac history (+0.30), prior stroke (+0.30), age>65 (+0.15) -> 0.75
    # Risk score = 0.6 * 0.3 + 0.4 * 0.75 = 0.18 + 0.30 = 0.48 -> ROUTINE or MODERATE depending on thresholds.
    # Let's give them more history to trigger CRITICAL (need 0.8)
    # Symptom score for "severe" without CRITICAL_SYMPTOM: 0.9.
    # 0.6 * 0.9 = 0.54. Need 0.26 from history (history_score >= 0.65).
    # Cardiac (0.3) + Stroke (0.3) + Diabetes (0.1) = 0.7.
    # 0.4 * 0.7 = 0.28. 0.54 + 0.28 = 0.82 -> CRITICAL.
    history = {
        "prior_cardiac_history": True,
        "prior_stroke": True,
        "diabetes": True
    }
    res = await engine.predict_priority("Patient has severe back pain", patient_history=history)
    assert res.priority_level == PriorityLevel.CRITICAL

@pytest.mark.asyncio
async def test_duration_estimate(engine):
    # 3 symptoms: "chest pain", "fever", "cough"
    # Base: 10 + (3 * 5) = 25
    # Critical flag (chest pain is critical) -> +15 = 40 min
    res = await engine.estimate_duration("Patient has chest pain, fever, and a cough", patient_history={})
    # Since "chest pain" triggers critical logic inside duration estimate
    assert res >= 40

@pytest.mark.asyncio
async def test_queue_ordering(engine):
    patients = [
        {"patient_id": "1", "priority_level": PriorityLevel.ROUTINE, "scheduled_at": datetime(2023, 1, 1, 10, 0, tzinfo=timezone.utc)},
        {"patient_id": "2", "priority_level": PriorityLevel.CRITICAL, "scheduled_at": datetime(2023, 1, 1, 11, 0, tzinfo=timezone.utc)},
        {"patient_id": "3", "priority_level": PriorityLevel.MODERATE, "scheduled_at": datetime(2023, 1, 1, 9, 0, tzinfo=timezone.utc)},
        {"patient_id": "4", "priority_level": PriorityLevel.CRITICAL, "scheduled_at": datetime(2023, 1, 1, 8, 0, tzinfo=timezone.utc)},
    ]
    
    sorted_queue = await engine.get_queue_order(patients)
    
    assert sorted_queue[0]["patient_id"] == "4" # CRITICAL, 8:00
    assert sorted_queue[1]["patient_id"] == "2" # CRITICAL, 11:00
    assert sorted_queue[2]["patient_id"] == "3" # MODERATE
    assert sorted_queue[3]["patient_id"] == "1" # ROUTINE
    assert sorted_queue[0]["queue_position"] == 1
    assert sorted_queue[3]["queue_position"] == 4

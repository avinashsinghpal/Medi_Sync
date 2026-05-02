import pytest
from medisync.core.errors import NLPExtractionError
from medisync.ai_engine.nlp_engine import NLPEngine
from medisync.core.config import Settings

@pytest.fixture
def mock_settings():
    return Settings(use_mock_ai=True, mongodb_url="mongodb://localhost", jwt_secret_key="secret")

@pytest.fixture
def real_settings():
    return Settings(use_mock_ai=False, mongodb_url="mongodb://localhost", jwt_secret_key="secret")

@pytest.mark.asyncio
async def test_extract_symptoms(real_settings):
    engine = NLPEngine(real_settings)
    res = await engine.extract_from_text("Patient has severe chest pain and fever")
    assert "chest pain" in res.symptoms
    assert "fever" in res.symptoms
    assert "severe" in res.severity_indicators

@pytest.mark.asyncio
async def test_extract_medication(real_settings):
    engine = NLPEngine(real_settings)
    res = await engine.extract_from_text("Give aspirin 75mg daily for the pain")
    assert "aspirin" in res.medications
    assert res.dosages.get("aspirin") == "75mg daily"

@pytest.mark.asyncio
async def test_extract_negation(real_settings):
    engine = NLPEngine(real_settings)
    res = await engine.extract_from_text("No fever, no cough reported")
    assert "fever" in res.negations
    assert "cough" in res.negations
    assert "fever" not in res.symptoms

@pytest.mark.asyncio
async def test_extract_vitals(real_settings):
    engine = NLPEngine(real_settings)
    res = await engine.extract_from_text("Patient BP 140/90 and feeling dizzy")
    assert res.vitals.get("BP") == "140/90"

@pytest.mark.asyncio
async def test_empty_text(real_settings):
    engine = NLPEngine(real_settings)
    with pytest.raises(NLPExtractionError):
        await engine.extract_from_text("")
    with pytest.raises(NLPExtractionError):
        await engine.extract_from_text("short")

@pytest.mark.asyncio
async def test_mock_behavior(mock_settings):
    engine = NLPEngine(mock_settings)
    res = await engine.extract_from_text("Doesn't matter what I type here, mock returns fixed.")
    assert res.symptoms == ["chest pain", "dizziness"]
    assert res.medications == ["aspirin"]
    assert res.confidence == 0.85

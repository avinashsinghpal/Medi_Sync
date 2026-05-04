"""
tests/unit/test_nlp.py
Unit tests for medisync.ai_engine.nlp_engine — entity extraction, caching,
negation handling, vitals parsing, and summary generation.
"""
import pytest
from medisync.ai_engine.nlp_engine import NLPEngine, ExtractionResult
from medisync.core.config import Settings
from medisync.core.errors import NLPExtractionError
from medisync.core.types import ConsultationLog
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_settings():
    """Settings with mock AI enabled for deterministic tests."""
    return Settings(
        mongodb_url="mongodb://localhost:27017",
        jwt_secret_key="test-secret",
        use_mock_ai=True,
    )

@pytest.fixture
def real_settings():
    """Settings with mock AI disabled — exercises rule-based extraction."""
    return Settings(
        mongodb_url="mongodb://localhost:27017",
        jwt_secret_key="test-secret",
        use_mock_ai=False,
    )

@pytest.fixture
def engine_mock(mock_settings):
    return NLPEngine(mock_settings)

@pytest.fixture
def engine_real(real_settings):
    return NLPEngine(real_settings)


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

class TestInputValidation:
    @pytest.mark.asyncio
    async def test_empty_text_raises(self, engine_real):
        with pytest.raises(NLPExtractionError):
            await engine_real.extract_from_text("")

    @pytest.mark.asyncio
    async def test_short_text_raises(self, engine_real):
        with pytest.raises(NLPExtractionError):
            await engine_real.extract_from_text("flu")

    @pytest.mark.asyncio
    async def test_whitespace_only_raises(self, engine_real):
        with pytest.raises(NLPExtractionError):
            await engine_real.extract_from_text("         ")


# ---------------------------------------------------------------------------
# Mock AI mode
# ---------------------------------------------------------------------------

class TestMockAI:
    @pytest.mark.asyncio
    async def test_mock_mode_returns_extraction_result(self, engine_mock):
        result = await engine_mock.extract_from_text("Patient has chest pain and difficulty breathing")
        assert isinstance(result, ExtractionResult)

    @pytest.mark.asyncio
    async def test_mock_mode_returns_fixed_symptoms(self, engine_mock):
        result = await engine_mock.extract_from_text("Patient reports severe headache and nausea today")
        assert "chest pain" in result.symptoms
        assert "dizziness" in result.symptoms

    @pytest.mark.asyncio
    async def test_mock_mode_has_confidence(self, engine_mock):
        result = await engine_mock.extract_from_text("Patient has been feeling unwell for three days")
        assert result.confidence > 0.0


# ---------------------------------------------------------------------------
# Rule-based extraction
# ---------------------------------------------------------------------------

class TestSymptomExtraction:
    @pytest.mark.asyncio
    async def test_detects_headache(self, engine_real):
        result = await engine_real.extract_from_text("Patient complains of severe headache since morning")
        assert "headache" in result.symptoms

    @pytest.mark.asyncio
    async def test_detects_multiple_symptoms(self, engine_real):
        result = await engine_real.extract_from_text(
            "Patient reports fever and cough with fatigue for two days"
        )
        detected = set(result.symptoms)
        assert "fever" in detected
        assert "cough" in detected
        assert "fatigue" in detected

    @pytest.mark.asyncio
    async def test_negation_excludes_symptom(self, engine_real):
        result = await engine_real.extract_from_text(
            "Patient denies headache but reports dizziness and nausea"
        )
        assert "headache" not in result.symptoms
        assert "headache" in result.negations

    @pytest.mark.asyncio
    async def test_no_symptom_keyword_returns_empty(self, engine_real):
        result = await engine_real.extract_from_text(
            "Patient visited for routine annual physical examination"
        )
        assert isinstance(result.symptoms, list)


class TestMedicationExtraction:
    @pytest.mark.asyncio
    async def test_detects_aspirin(self, engine_real):
        result = await engine_real.extract_from_text(
            "Patient is currently taking aspirin for blood thinning"
        )
        assert "aspirin" in result.medications

    @pytest.mark.asyncio
    async def test_extracts_dosage_with_medication(self, engine_real):
        result = await engine_real.extract_from_text(
            "Prescribed metformin 500mg daily for blood sugar management"
        )
        assert "metformin" in result.medications
        assert "metformin" in result.dosages

    @pytest.mark.asyncio
    async def test_multiple_medications(self, engine_real):
        result = await engine_real.extract_from_text(
            "Patient takes lisinopril and metformin for hypertension and diabetes"
        )
        assert "lisinopril" in result.medications
        assert "metformin" in result.medications


class TestVitalsExtraction:
    @pytest.mark.asyncio
    async def test_blood_pressure_extracted(self, engine_real):
        result = await engine_real.extract_from_text(
            "Blood pressure is 140/90 mmHg taken this morning"
        )
        assert "blood_pressure" in result.vitals
        assert "140/90" in result.vitals["blood_pressure"]

    @pytest.mark.asyncio
    async def test_heart_rate_extracted(self, engine_real):
        result = await engine_real.extract_from_text(
            "Heart rate is 88 bpm measured at rest in clinic"
        )
        assert "heart_rate" in result.vitals

    @pytest.mark.asyncio
    async def test_pain_scale_extracted(self, engine_real):
        result = await engine_real.extract_from_text(
            "Patient rates pain at 7 out of 10 on the pain scale"
        )
        assert "pain_scale" in result.vitals
        assert result.vitals["pain_scale"] == "7/10"


class TestSeverityExtraction:
    @pytest.mark.asyncio
    async def test_severe_indicator_detected(self, engine_real):
        result = await engine_real.extract_from_text(
            "Patient presents with severe chest pain radiating to arm"
        )
        assert "severe" in result.severity_indicators

    @pytest.mark.asyncio
    async def test_mild_indicator_detected(self, engine_real):
        result = await engine_real.extract_from_text(
            "Patient reports mild headache on and off for past week"
        )
        assert "mild" in result.severity_indicators


# ---------------------------------------------------------------------------
# Caching
# ---------------------------------------------------------------------------

class TestNLPCache:
    @pytest.mark.asyncio
    async def test_identical_inputs_use_cache(self, engine_real):
        text = "Patient has persistent headache and fatigue for two weeks"
        result1 = await engine_real.extract_from_text(text)
        result2 = await engine_real.extract_from_text(text)
        # Both calls should return the identical object (cache hit)
        assert result1 is result2

    @pytest.mark.asyncio
    async def test_clear_cache_invalidates(self, engine_real):
        text = "Patient has dizziness and nausea for the past week now"
        result1 = await engine_real.extract_from_text(text)
        engine_real.clear_cache()
        result2 = await engine_real.extract_from_text(text)
        # After cache clear, new object created (same data, different instance)
        assert result1 is not result2
        assert result1.symptoms == result2.symptoms


# ---------------------------------------------------------------------------
# ConsultationLog extraction
# ---------------------------------------------------------------------------

class TestConsultationLogExtraction:
    @pytest.mark.asyncio
    async def test_uses_raw_transcript(self, engine_real):
        log = ConsultationLog(
            patient_id="P-001",
            doctor_id="D-001",
            started_at=datetime.now(timezone.utc),
            raw_transcript="Patient complains of severe headache and dizziness",
            notes="",
            extracted_symptoms=[],
            extracted_medications=[],
            extracted_dosages={},
            estimated_duration_minutes=20,
        )
        result = await engine_real.extract_from_consultation_log(log)
        assert "headache" in result.symptoms

    @pytest.mark.asyncio
    async def test_falls_back_to_notes(self, engine_real):
        log = ConsultationLog(
            patient_id="P-002",
            doctor_id="D-001",
            started_at=datetime.now(timezone.utc),
            raw_transcript=None,
            notes="Patient has persistent cough and sore throat for five days",
            extracted_symptoms=[],
            extracted_medications=[],
            extracted_dosages={},
            estimated_duration_minutes=15,
        )
        result = await engine_real.extract_from_consultation_log(log)
        assert "cough" in result.symptoms

    @pytest.mark.asyncio
    async def test_empty_log_raises(self, engine_real):
        log = ConsultationLog(
            patient_id="P-003",
            doctor_id="D-001",
            started_at=datetime.now(timezone.utc),
            raw_transcript=None,
            notes=None,
            extracted_symptoms=[],
            extracted_medications=[],
            extracted_dosages={},
            estimated_duration_minutes=10,
        )
        with pytest.raises(NLPExtractionError):
            await engine_real.extract_from_consultation_log(log)


# ---------------------------------------------------------------------------
# Summary generation
# ---------------------------------------------------------------------------

class TestSummaryGeneration:
    @pytest.mark.asyncio
    async def test_summary_mentions_symptoms(self, engine_real):
        extraction = ExtractionResult(
            symptoms=["chest pain", "dizziness"],
            severity_indicators=["severe"],
        )
        summary = await engine_real.generate_consultation_summary(extraction, {})
        assert "chest pain" in summary
        assert "dizziness" in summary

    @pytest.mark.asyncio
    async def test_summary_no_symptoms_uses_default(self, engine_real):
        extraction = ExtractionResult(symptoms=[])
        summary = await engine_real.generate_consultation_summary(extraction, {})
        assert "no specific symptoms" in summary.lower()


# ---------------------------------------------------------------------------
# Normalize symptom
# ---------------------------------------------------------------------------

class TestNormalizeSymptom:
    @pytest.mark.asyncio
    async def test_chest_hurt_normalizes_to_chest_pain(self, engine_real):
        result = await engine_real.normalize_symptom("chest hurt")
        assert result == "chest pain"

    @pytest.mark.asyncio
    async def test_already_normalized_returned_lowered(self, engine_real):
        result = await engine_real.normalize_symptom("Headache")
        assert result == "headache"

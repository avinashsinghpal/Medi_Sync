## Purpose
NLP Engine — extracts structured clinical entities from doctor speech transcripts.
Identifies symptoms, medicines, dosages, severity indicators, and medical terms.

## File Location
`medisync/ai_engine/nlp_engine.py`

## Dependencies
- `medisync/core/types.py`, `medisync/core/errors.py`, `medisync/core/config.py`
- `spacy`, `transformers` or `openai`/`groq`

---

## `ExtractionResult` (Dataclass)

```python
@dataclass
class ExtractionResult:
    symptoms: list[str]
    medications: list[str]
    dosages: dict[str, str]        # {medication_name: dosage_string}
    diagnoses: list[str]
    severity_indicators: list[str]
    medical_terms: list[str]
    negations: list[str]           # Symptoms explicitly denied
    vitals: dict[str, str]         # {"BP": "140/90", "HR": "90 bpm"}
    summary: str                   # Human-readable 1-2 sentence summary
    confidence: float              # 0.0–1.0
```

---

## Class: `NLPEngine`

### `async extract_from_text(text: str) -> ExtractionResult`
1. Pre-process: expand abbreviations (SOB→"shortness of breath", BP, HR, etc.)
2. Run spaCy NER
3. Apply medical entity ruler from `data/medical_terms.json`
4. Detect negations via dependency parsing
5. Extract vitals via regex (e.g. "BP 140/90")
6. LLM-enhance if API key configured
7. Generate human-readable summary

**Raises:** `NLPExtractionError` if text is empty or < 10 chars

### `async extract_from_consultation_log(log: ConsultationLog) -> ExtractionResult`
- Uses `log.raw_transcript` or falls back to `log.notes`
- Raises `NLPExtractionError` if both are empty

### `async generate_consultation_summary(extraction: ExtractionResult, patient_context: dict) -> str`
- Produces: "Patient reports [symptoms]. [Risk context]."
- LLM-based if key available, else rule-based template

### `async normalize_symptom(symptom: str) -> str`
- Canonical normalization: "chest hurt" → "chest pain"

---

## Severity Classification

| Severity | Keywords |
|---|---|
| CRITICAL | "severe", "acute", "crushing", "loss of consciousness" |
| HIGH | "significant", "persistent", "worsening" |
| MODERATE | "moderate", "intermittent" |
| LOW | "mild", "slight", "occasional" |

---

## Mock Implementation (use_mock_ai=True)

Returns fixed result: symptoms=["chest pain", "dizziness"], medications=["aspirin"], dosages={"aspirin":"75mg daily"}, confidence=0.85

---

## Expected Test Outcomes

| Test | Input | Expected Output |
|---|---|---|
| extract symptoms | "severe chest pain and fever" | symptoms includes both |
| extract medication | "Give aspirin 75mg daily" | medications=["aspirin"] |
| extract negation | "No fever, no cough" | negations=["fever","cough"] |
| extract vitals | "BP 140/90" | vitals={"BP":"140/90"} |
| empty text | "" | `NLPExtractionError` |

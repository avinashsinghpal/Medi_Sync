## Purpose
Patient Prioritization Engine — classifies patients into CRITICAL / MODERATE / ROUTINE
and estimates consultation time based on symptom severity and historical risk.

## File Location
`medisync/ai_engine/priority_engine.py`

## Dependencies
- `medisync/core/types.py` → `PriorityLevel`
- `medisync/core/config.py` → `Settings`
- `medisync/ai_engine/nlp_engine.py` → `ExtractionResult`

---

## `PriorityAssessment` (Dataclass)

```python
@dataclass
class PriorityAssessment:
    priority_level: PriorityLevel       # CRITICAL | MODERATE | ROUTINE
    risk_score: float                   # 0.0–1.0 composite risk
    estimated_duration_minutes: int     # Predicted consultation time
    risk_factors: list[str]             # Reasons for priority assignment
    urgent_flags: list[str]             # Symptoms that triggered CRITICAL flag
    recommendation: str                 # One-sentence doctor guidance
    confidence: float                   # Prediction confidence (0.0–1.0)
```

---

## Class: `PriorityEngine`

```python
class PriorityEngine:
    def __init__(self, nlp_engine: NLPEngine, settings: Settings):
        ...
```

### `async predict_priority(symptoms_text: str, patient_history: Optional[dict] = None) -> PriorityAssessment`
**Algorithm:**
1. Run `nlp_engine.extract_from_text(symptoms_text)` to get structured data
2. Calculate `symptom_severity_score` (weighted sum of severity indicators)
3. Calculate `history_risk_score` from patient_history (chronic conditions, age, etc.)
4. Combine: `risk_score = 0.6 * symptom_score + 0.4 * history_risk_score`
5. Apply priority thresholds from settings:
   - `risk_score >= critical_symptom_threshold` → CRITICAL
   - `risk_score >= moderate_symptom_threshold` → MODERATE
   - else → ROUTINE
6. Check for absolute critical symptoms (see table below)
7. Estimate duration using `estimate_duration()`
8. Build and return `PriorityAssessment`

### `async estimate_duration(symptoms_text: str, patient_history: Optional[dict] = None) -> int`
**Estimation logic (heuristic):**
- Base: 10 minutes
- +5 min per unique symptom cluster
- +10 min if patient has 3+ chronic conditions
- +15 min if CRITICAL priority
- +5 min if elderly patient (age > 65)
- +5 min for first-time patient (no history)
- Cap at `settings.max_consultation_time_minutes`
- Returns integer minutes

### `async get_queue_order(patients: list[dict]) -> list[dict]`
- Input: list of dicts with `patient_id`, `priority_level`, `scheduled_at`
- Sort order: CRITICAL → MODERATE → ROUTINE, then by `scheduled_at` ASC within each tier
- Returns sorted list with added `queue_position` field

---

## Absolute Critical Symptoms (Emergency Flags)

These symptoms ALWAYS trigger CRITICAL priority regardless of risk score:

```python
CRITICAL_SYMPTOMS = [
    "chest pain",
    "heart attack",
    "cardiac arrest",
    "stroke",
    "loss of consciousness",
    "difficulty breathing",
    "anaphylaxis",
    "severe bleeding",
    "seizure",
    "suicidal ideation",
    "overdose",
]
```

---

## History Risk Factors Scoring

| Factor | Risk Score Contribution |
|---|---|
| Age > 65 | +0.15 |
| Prior cardiac history | +0.30 |
| Prior stroke | +0.30 |
| Diabetes | +0.10 |
| Hypertension | +0.10 |
| Active cancer | +0.25 |
| Immunocompromised | +0.20 |
| Prior hospitalization in last 30 days | +0.20 |

---

## Expected Test Outcomes

| Test | Input | Expected Output |
|---|---|---|
| CRITICAL detection | "severe chest pain" | PriorityLevel.CRITICAL |
| ROUTINE detection | "mild headache for 2 days" | PriorityLevel.ROUTINE |
| History boost | cardiac history + moderate symptoms | CRITICAL |
| Duration estimate basic | 3 symptoms | 25 minutes |
| Queue ordering | Mix of priorities | CRITICAL patients first |
| Empty symptoms | "" | `NLPExtractionError` propagated |

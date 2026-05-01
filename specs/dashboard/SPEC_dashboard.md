## Purpose
Doctor Dashboard Service — aggregates patient summaries, priority queues,
real-time consultation data, and analytics for the doctor's daily workflow.

**Fast readability. Clear visual hierarchy. One-click access.**

## File Location
`medisync/dashboard/dashboard.py`

## Dependencies
- `medisync/patient/patient_management.py` → `PatientManager`
- `medisync/appointment/appointment_system.py` → `AppointmentSystem`
- `medisync/ai_engine/nlp_engine.py` → `NLPEngine`
- `medisync/ai_engine/priority_engine.py` → `PriorityEngine`
- `medisync/core/types.py`

---

## Class: `DoctorDashboard`

```python
class DoctorDashboard:
    def __init__(
        self,
        patient_manager: PatientManager,
        appointment_system: AppointmentSystem,
        nlp_engine: NLPEngine,
        priority_engine: PriorityEngine,
    ):
        ...
```

---

## Methods to Implement

### `async get_dashboard_overview(doctor_id: str, date: date) -> DashboardOverview`

```python
@dataclass
class DashboardOverview:
    doctor_id: str
    date: str                           # ISO date
    total_patients_today: int
    critical_count: int                 # 🔴
    moderate_count: int                 # 🟡
    routine_count: int                  # 🟢
    completed_consultations: int
    pending_consultations: int
    estimated_remaining_hours: float
    priority_queue: list[PatientQueueItem]  # Ordered by priority
    recent_activity: list[dict]         # Last 5 actions/events
```

### `async get_patient_queue(doctor_id: str, date: date) -> list[PatientQueueItem]`

```python
@dataclass
class PatientQueueItem:
    queue_position: int
    patient_id: str
    patient_name: str
    age: int
    appointment_id: str
    scheduled_at: str
    priority_level: str                 # "critical" | "moderate" | "routine"
    priority_badge_color: str           # "red" | "yellow" | "green"
    symptoms_preview: str              # First 100 chars of symptoms
    estimated_duration_minutes: int
    status: str                        # appointment status
    risk_flags: list[str]              # Urgent flags for doctor attention
```

### `async get_patient_summary_card(patient_id: str) -> PatientSummaryCard`

```python
@dataclass
class PatientSummaryCard:
    patient_id: str
    full_name: str
    age: int
    blood_group: Optional[str]
    status: str
    priority_level: str
    risk_indicators: list[str]          # Highlighted risk factors
    recent_diagnoses: list[str]         # Last 3 diagnoses (expandable)
    current_medications: list[str]      # Active medications
    last_visit_date: Optional[str]
    total_visits: int
    consultation_history_preview: list[dict]  # Last 3 consultations (collapsed)
    quick_actions: list[str]            # ["start_consultation", "view_history", "add_record"]
```

### `async process_consultation(appointment_id: str, audio_data: Optional[bytes], text_input: Optional[str]) -> ConsultationResult`

Full consultation processing pipeline:

```python
@dataclass
class ConsultationResult:
    consultation_id: str
    patient_id: str
    doctor_id: str
    transcript: Optional[str]
    extracted_data: dict               # From NLPEngine
    consultation_summary: str
    priority_level: str
    prescription_text: Optional[str]
    recommended_follow_up: Optional[str]
    structured_output: dict            # Machine-readable JSON (see below)
```

Structured output format:
```json
{
  "patient_id": "P-XXXXXXXX",
  "symptoms": ["chest pain", "dizziness"],
  "risk_level": "High",
  "medications": ["aspirin 75mg"],
  "consultation_time": "20 minutes",
  "priority": "Critical"
}
```

### `async get_analytics(doctor_id: str, date_from: date, date_to: date) -> dict`

```python
{
  "total_consultations": int,
  "avg_consultation_duration_minutes": float,
  "priority_breakdown": {"critical": int, "moderate": int, "routine": int},
  "most_common_symptoms": list[str],  # Top 5
  "patient_satisfaction_avg": float,  # 0–5 if collected
  "busiest_day": str,                # ISO date
}
```

---

## UX Invariants (CRITICAL for frontend spec alignment)

- `priority_badge_color` MUST always be "red", "yellow", or "green" (CSS class compatible)
- `symptoms_preview` MUST be truncated to 100 characters with "..." if longer
- `quick_actions` list items MUST be stable identifiers (no display strings)
- All datetime fields in responses MUST be ISO 8601 strings
- Empty lists MUST be returned as `[]` (never `null`)

---

## Expected Test Outcomes

| Test | Input | Expected Output |
|---|---|---|
| get_dashboard_overview | Valid doctor_id and date | DashboardOverview with correct counts |
| get_patient_queue ordering | Mix of priorities | CRITICAL first in queue |
| get_patient_summary_card | Valid patient_id | PatientSummaryCard with all fields |
| process_consultation audio | Valid audio bytes | ConsultationResult with transcript |
| process_consultation text | Text input | ConsultationResult with extracted data |
| process_consultation both None | No audio, no text | `NLPExtractionError` |

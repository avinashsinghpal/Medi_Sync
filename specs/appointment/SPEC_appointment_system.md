## Purpose
Smart Appointment System — handles patient appointment booking, scheduling,
slot management, status transitions, and queue management for doctors.

**Guided input. Minimal steps. AI-predicted wait times.**

## File Location
`medisync/appointment/appointment_system.py`

## Dependencies
- `medisync/core/types.py` → `Appointment`, `AppointmentStatus`, `ConsultationType`
- `medisync/core/errors.py` → `AppointmentNotFoundError`, `AppointmentConflictError`, etc.
- `medisync/patient/patient_management.py` → `PatientManager` (for existence checks)
- `medisync/ai_engine/priority_engine.py` → `PriorityEngine` (for AI priority prediction)
- `medisync/storage/` → `AppointmentRepository`

---

## Class: `AppointmentSystem`

```python
class AppointmentSystem:
    def __init__(
        self,
        repository: AppointmentRepository,
        patient_manager: PatientManager,
        priority_engine: PriorityEngine,
        settings: Settings
    ):
        ...
```

---

## Methods to Implement

### `async book_appointment(request: BookAppointmentRequest) -> Appointment`
**Flow:**
1. Validate patient exists via `patient_manager.get_patient()`
2. Validate `scheduled_at` is in the future
3. Check for slot conflicts via `_check_slot_availability()`
4. Call `priority_engine.predict_priority(symptoms_description)` for AI priority
5. Call `priority_engine.estimate_duration(symptoms_description, patient_history)` for time
6. Create `Appointment` with auto-generated ID
7. Persist and return

**Raises:**
- `PatientNotFoundError` if patient doesn't exist
- `AppointmentConflictError` if slot is taken (same doctor, overlapping time)
- `InvalidPatientDataError` if symptoms_description is empty

### `async get_appointment(appointment_id: str) -> Appointment`
- Raises `AppointmentNotFoundError` if not found

### `async get_patient_appointments(patient_id: str, status_filter: Optional[AppointmentStatus] = None) -> list[Appointment]`
- Returns all appointments for a patient, ordered by `scheduled_at` ascending
- If `status_filter` provided, only return appointments with that status
- Raises `PatientNotFoundError` if patient doesn't exist

### `async get_doctor_queue(doctor_id: str, date: date) -> list[Appointment]`
- Returns all appointments for a doctor on a given date
- Ordered by: priority level DESC (CRITICAL first), then `scheduled_at` ASC
- Priority sort order: CRITICAL → MODERATE → ROUTINE
- Only returns CONFIRMED and IN_SESSION appointments

### `async confirm_appointment(appointment_id: str, doctor_id: str) -> Appointment`
- Transitions status: PENDING → CONFIRMED
- Assigns `doctor_id` if not already set
- Raises `InvalidAppointmentStateError` if appointment is not in PENDING state

### `async start_consultation(appointment_id: str) -> Appointment`
- Transitions status: CONFIRMED → IN_SESSION
- Raises `InvalidAppointmentStateError` if appointment is not CONFIRMED

### `async complete_consultation(appointment_id: str, consultation_id: str) -> Appointment`
- Transitions status: IN_SESSION → COMPLETED
- Links `consultation_id` to the appointment record
- Raises `InvalidAppointmentStateError` if appointment is not IN_SESSION

### `async cancel_appointment(appointment_id: str, reason: Optional[str] = None) -> Appointment`
- Allowed from: PENDING or CONFIRMED only
- Raises `InvalidAppointmentStateError` if already COMPLETED, CANCELLED, or IN_SESSION
- Stores cancellation reason in `notes` field

### `async get_available_slots(doctor_id: str, date: date, duration_minutes: int = 15) -> list[datetime]`
- Returns list of available appointment start times for a doctor on a given day
- Assumes working hours: 09:00–17:00 in local time
- Slots are non-overlapping with existing CONFIRMED/IN_SESSION appointments
- Returns empty list if no slots available

### `async get_today_summary(doctor_id: str) -> dict`
- Returns structured daily summary for the doctor dashboard:
```python
{
  "date": str,              # ISO date string
  "total_appointments": int,
  "completed": int,
  "pending": int,
  "critical_count": int,
  "estimated_hours": float,  # Sum of estimated durations
  "queue": list[dict]        # Ordered queue with patient summaries
}
```

---

## State Transition Rules

```
PENDING → CONFIRMED (by doctor or system)
PENDING → CANCELLED (by patient or admin)
CONFIRMED → IN_SESSION (when consultation starts)
CONFIRMED → CANCELLED (by doctor or admin only)
CONFIRMED → NO_SHOW (if patient doesn't arrive within 30 min of scheduled time)
IN_SESSION → COMPLETED (when consultation ends)
COMPLETED → [terminal, no further transitions]
CANCELLED → [terminal, no further transitions]
NO_SHOW → [terminal, no further transitions]
```

---

## Internal Helper: `_check_slot_availability`

```python
async def _check_slot_availability(
    doctor_id: str,
    start_time: datetime,
    duration_minutes: int
) -> bool:
    """
    Returns True if the slot is available.
    A slot conflicts if any existing PENDING/CONFIRMED/IN_SESSION appointment
    for the same doctor overlaps with [start_time, start_time + duration_minutes].
    """
    ...
```

---

## Edge Case Handling

| Scenario | Expected Behavior |
|---|---|
| Book appointment in the past | `InvalidPatientDataError` with clear message |
| Book when doctor already busy | `AppointmentConflictError` with next available slot hint |
| Cancel a COMPLETED appointment | `InvalidAppointmentStateError` |
| Start consultation on PENDING appointment | `InvalidAppointmentStateError` |
| `get_available_slots` on weekend | Return empty list (no working hours) |
| `get_doctor_queue` with no appointments | Return empty list |

---

## Expected Test Outcomes (from `tests/unit/test_appointment.py`)

| Test | Input | Expected Output |
|---|---|---|
| book_appointment success | Valid data | Appointment with auto-generated ID and AI priority |
| book_appointment past date | scheduled_at=yesterday | `InvalidPatientDataError` |
| book_appointment conflict | Same doctor, overlapping slot | `AppointmentConflictError` |
| confirm_appointment bad state | Already CONFIRMED → confirm again | `InvalidAppointmentStateError` |
| get_doctor_queue ordering | Mix of priorities | CRITICAL first, then MODERATE, then ROUTINE |
| get_available_slots | Full day | List of 30-min slots from 09:00–17:00 |
| cancel completed appointment | COMPLETED status | `InvalidAppointmentStateError` |

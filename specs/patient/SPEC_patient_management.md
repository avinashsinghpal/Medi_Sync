## Purpose
Unified Patient Profile System — the central module for creating, retrieving,
updating, and searching patient medical records.

**One patient → one intelligent record.**
This module is the authoritative source for all patient data operations.
NO business logic lives in the API layer — only here.

## File Location
`medisync/patient/patient_management.py`

## Dependencies
- `medisync/core/types.py` → `PatientProfile`, `MedicalRecord`, `ConsultationLog`
- `medisync/core/errors.py` → `PatientNotFoundError`, `DuplicatePatientError`, etc.
- `medisync/storage/` → `PatientRepository`
- Python stdlib: `uuid`, `datetime`, `typing`

---

## Class: `PatientManager`

The single service class responsible for all patient data operations.
Must be instantiated once at startup and injected via FastAPI dependency.

```python
class PatientManager:
    def __init__(self, repository: PatientRepository, settings: Settings):
        self.repository = repository
        self.settings = settings
```

---

## Methods to Implement

### `async create_patient(data: CreatePatientRequest) -> PatientProfile`
- Generates unique `patient_id` in format `"P-{uuid4[:8].upper()}"`
- Checks for duplicate by email — raises `DuplicatePatientError` if found
- Validates all required fields — raises `InvalidPatientDataError` with descriptive message
- Sets `created_at` and `updated_at` to `datetime.utcnow()`
- Sets `status` to `PatientStatus.ACTIVE`
- Persists to database via `repository.create()`
- Returns the created `PatientProfile`

### `async get_patient(patient_id: str) -> PatientProfile`
- Retrieves patient by ID
- Raises `PatientNotFoundError` if not found
- Increments access counter in background (non-blocking)

### `async get_patient_by_email(email: str) -> PatientProfile`
- Case-insensitive email lookup
- Raises `PatientNotFoundError` if not found

### `async update_patient(patient_id: str, updates: UpdatePatientRequest) -> PatientProfile`
- Applies partial updates (only provided fields are changed)
- Sets `updated_at` to current UTC time
- Raises `PatientNotFoundError` if patient does not exist
- Raises `InvalidPatientDataError` if updates violate constraints
- Returns updated `PatientProfile`

### `async deactivate_patient(patient_id: str) -> PatientProfile`
- Sets `status` to `PatientStatus.INACTIVE`
- Raises `PatientNotFoundError` if not found

### `async get_patient_history(patient_id: str, limit: int = 20, offset: int = 0) -> list[MedicalRecord]`
- Returns paginated list of medical records for the patient
- Ordered by `recorded_at` descending (most recent first)
- Raises `PatientNotFoundError` if patient does not exist

### `async add_medical_record(patient_id: str, record: CreateMedicalRecordRequest) -> MedicalRecord`
- Validates patient exists (raises `PatientNotFoundError`)
- Creates `MedicalRecord` with auto-generated `record_id`
- Links to `consultation_id` if provided
- Persists and returns the new record

### `async get_consultation_logs(patient_id: str, limit: int = 10) -> list[ConsultationLog]`
- Returns recent consultation logs for the patient
- Ordered by `started_at` descending
- Raises `PatientNotFoundError` if patient does not exist

### `async search_patients(query: str, limit: int = 20) -> list[PatientProfile]`
- Full-text search across: `full_name`, `contact_email`, `patient_id`
- Returns best matches ordered by relevance
- Returns empty list (never raises) if no matches found
- `query` MUST be at least 2 characters long

### `async get_patient_summary(patient_id: str) -> dict`
- Returns a structured quick-summary dict for the dashboard:
```python
{
  "patient_id": str,
  "full_name": str,
  "age": int,
  "blood_group": str,
  "status": str,
  "total_records": int,
  "recent_diagnoses": list[str],   # Last 3 diagnoses
  "current_medications": list[str], # From most recent prescription
  "last_visit": str,               # ISO datetime or "Never"
  "priority_level": str            # Latest AI-assigned priority
}
```

---

## Edge Case Handling

| Scenario | Expected Behavior |
|---|---|
| `create_patient` with duplicate email | Raise `DuplicatePatientError` |
| `get_patient` with invalid ID format | Raise `PatientNotFoundError` |
| `search_patients` with 1-char query | Raise `InvalidPatientDataError` |
| `add_medical_record` for non-existent patient | Raise `PatientNotFoundError` |
| `get_patient_history` with limit=0 | Return empty list |
| `update_patient` with no fields provided | Return unchanged profile |

---

## Expected Test Outcomes (from `tests/unit/test_patient.py`)

| Test | Input | Expected Output |
|---|---|---|
| create_patient success | Valid data | PatientProfile with auto-generated ID |
| create_patient duplicate email | Same email twice | `DuplicatePatientError` on second call |
| create_patient empty name | full_name="" | `InvalidPatientDataError` |
| get_patient not found | Unknown ID | `PatientNotFoundError` |
| update_patient partial | Only update phone | Only phone changed, rest unchanged |
| get_patient_summary | Valid patient_id | Dict with all required keys |
| search_patients empty result | query="zzz" | Empty list, no exception |
| add_medical_record bad type | record_type="xray" | `InvalidPatientDataError` |

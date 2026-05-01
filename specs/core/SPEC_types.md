## Purpose
Central domain type definitions. The single source of truth for every data shape in the system.
Zero external dependencies. Every other module imports FROM here.

## File Location
`medisync/core/types.py`

## Dependencies
- Python stdlib only: `dataclasses`, `enum`, `typing`, `datetime`, `uuid`
- NO imports from any other `medisync/` module

---

### `PatientStatus` (Enum)
**What it is:** Lifecycle state of a patient record in the system.

```python
class PatientStatus(str, Enum):
    ACTIVE      = "active"       # Patient has active records and appointments
    INACTIVE    = "inactive"     # No recent activity (> 6 months)
    DISCHARGED  = "discharged"   # Formally discharged from ongoing care
    CRITICAL    = "critical"     # Flagged by priority engine as urgent
```

**Constraints:**
- MUST be `str` mixin so it serializes cleanly to/from JSON and MongoDB
- MUST have exactly these four values

---

### `PriorityLevel` (Enum)
**What it is:** AI-assigned priority classification for patient consultations.

```python
class PriorityLevel(str, Enum):
    CRITICAL = "critical"  # 🔴 Immediate attention required
    MODERATE = "moderate"  # 🟡 Scheduled within 24h
    ROUTINE  = "routine"   # 🟢 Standard scheduling applies
```

**Constraints:**
- MUST be `str` mixin
- Visual mapping: CRITICAL → red badge, MODERATE → yellow badge, ROUTINE → green badge

---

### `AppointmentStatus` (Enum)
**What it is:** Lifecycle state of an appointment booking.

```python
class AppointmentStatus(str, Enum):
    PENDING    = "pending"     # Booked, awaiting confirmation
    CONFIRMED  = "confirmed"   # Doctor confirmed the appointment
    IN_SESSION = "in_session"  # Consultation currently active
    COMPLETED  = "completed"   # Consultation finished, records saved
    CANCELLED  = "cancelled"   # Cancelled by patient or doctor
    NO_SHOW    = "no_show"     # Patient did not attend
```

---

### `ConsultationType` (Enum)
**What it is:** Mode of consultation delivery.

```python
class ConsultationType(str, Enum):
    IN_PERSON = "in_person"   # Physical hospital visit
    TELECONSULT = "teleconsult"  # Video/phone consultation
    FOLLOW_UP   = "follow_up"    # Follow-up to prior consultation
    EMERGENCY   = "emergency"    # Walk-in emergency
```

---

### `PatientProfile` (Dataclass)
**What it is:** The core unified patient record. One patient → one profile.
All history, prescriptions, and consultation logs reference this via `patient_id`.

```python
@dataclass
class PatientProfile:
    patient_id: str              # UUID string, auto-generated (format: "P-{uuid4[:8]}")
    full_name: str               # Full legal name
    date_of_birth: date          # For age calculation
    gender: str                  # "male" | "female" | "other" | "prefer_not_to_say"
    blood_group: Optional[str]   # "A+" | "A-" | "B+" | "B-" | "O+" | "O-" | "AB+" | "AB-"
    contact_email: str           # Primary contact email
    contact_phone: str           # E.164 format preferred (+91XXXXXXXXXX)
    address: Optional[str]       # Free text address
    emergency_contact: Optional[str]  # Name and phone
    status: PatientStatus        # Defaults to ACTIVE
    created_at: datetime         # UTC, auto-set
    updated_at: datetime         # UTC, auto-updated
    metadata: dict               # Flexible extra fields (e.g. insurance_id, hospital_id)
```

**Constraints:**
- `patient_id` MUST be auto-generated if not provided
- `full_name` MUST NOT be empty
- `gender` MUST be one of the four accepted values
- `status` defaults to `PatientStatus.ACTIVE`
- `metadata` defaults to empty dict (never None)

**Computed Property:**
```python
@property
def age(self) -> int:
    """Return current age in years based on date_of_birth."""
    ...
```

---

### `MedicalRecord` (Dataclass)
**What it is:** A single timestamped medical event for a patient.
Includes diagnoses, prescriptions, and test results.

```python
@dataclass
class MedicalRecord:
    record_id: str               # UUID string, auto-generated
    patient_id: str              # FK → PatientProfile.patient_id
    consultation_id: Optional[str]  # FK → ConsultationLog.consultation_id
    record_type: str             # "diagnosis" | "prescription" | "lab_result" | "imaging" | "note"
    title: str                   # Short descriptive title
    content: str                 # Full record content (structured text or JSON string)
    doctor_id: Optional[str]     # ID of the attending doctor
    hospital_id: Optional[str]   # ID of the issuing hospital
    recorded_at: datetime        # UTC timestamp of the medical event
    tags: list[str]              # Medical keywords for search (e.g. ["cardiac", "hypertension"])
    attachments: list[str]       # File paths or URLs to attached documents
```

**Constraints:**
- `record_type` MUST be one of the six accepted values
- `content` MUST NOT be empty
- `tags` defaults to empty list
- `attachments` defaults to empty list

---

### `ConsultationLog` (Dataclass)
**What it is:** A complete record of a single doctor-patient consultation session.
Includes AI-extracted structured data from speech.

```python
@dataclass
class ConsultationLog:
    consultation_id: str         # UUID string, auto-generated
    patient_id: str              # FK → PatientProfile
    doctor_id: str               # Doctor's identifier
    appointment_id: Optional[str]  # FK → Appointment
    started_at: datetime         # UTC start time
    ended_at: Optional[datetime] # UTC end time (None if in progress)
    raw_transcript: Optional[str]  # Raw speech-to-text output
    extracted_symptoms: list[str]  # NLP-extracted symptom list
    extracted_medications: list[str]  # NLP-extracted medication list
    extracted_dosages: dict      # {medication: dosage_string}
    diagnosis: Optional[str]     # Final diagnosis summary
    prescription_text: Optional[str]  # Full prescription as text
    priority_level: PriorityLevel  # AI-assigned priority
    consultation_summary: Optional[str]  # Human-readable AI summary
    estimated_duration_minutes: int  # AI-predicted (or actual) duration
    notes: str                   # Doctor's additional notes
```

**Constraints:**
- `consultation_id` MUST be auto-generated UUID
- `ended_at` MUST be after `started_at` if not None
- `priority_level` defaults to `PriorityLevel.ROUTINE`
- `estimated_duration_minutes` MUST be > 0

---

### `Appointment` (Dataclass)
**What it is:** A scheduled consultation booking made by a patient.

```python
@dataclass
class Appointment:
    appointment_id: str          # UUID string, auto-generated
    patient_id: str              # FK → PatientProfile
    doctor_id: Optional[str]     # Assigned doctor (may be None until confirmed)
    scheduled_at: datetime       # UTC datetime of the appointment
    consultation_type: ConsultationType
    status: AppointmentStatus    # Defaults to PENDING
    symptoms_description: str    # Patient's self-reported symptoms
    priority_level: PriorityLevel  # AI-predicted priority from symptoms
    estimated_duration_minutes: int  # AI-predicted consultation time
    notes: Optional[str]         # Additional notes by patient or staff
    created_at: datetime         # UTC, auto-set
```

**Constraints:**
- `appointment_id` MUST be auto-generated UUID
- `symptoms_description` MUST NOT be empty (minimum 10 characters)
- `scheduled_at` MUST be in the future at time of creation
- `status` defaults to `AppointmentStatus.PENDING`
- `priority_level` defaults to `PriorityLevel.ROUTINE` (overwritten by AI)

---

## Validation Helpers

```python
def validate_patient_profile(patient: PatientProfile) -> None:
    """Raise ValueError with descriptive message for any invalid PatientProfile field."""
    ...

def validate_appointment(appointment: Appointment) -> None:
    """Raise ValueError for any invalid Appointment field."""
    ...

def validate_medical_record(record: MedicalRecord) -> None:
    """Raise ValueError for any invalid MedicalRecord field."""
    ...
```

---

## Expected Test Outcomes (from `tests/unit/test_types.py`)

| Test | Input | Expected Output |
|---|---|---|
| PatientProfile auto-id | No patient_id provided | "P-XXXXXXXX" format UUID |
| PatientProfile empty name | full_name="" | `ValueError` raised |
| PatientProfile age | dob=1990-01-01 | Integer ≥ 34 |
| Appointment past date | scheduled_at=yesterday | `ValueError` raised |
| Appointment empty symptoms | symptoms_description="" | `ValueError` raised |
| MedicalRecord bad type | record_type="xray" | `ValueError` ("unknown record_type") |
| PriorityLevel serialization | PriorityLevel.CRITICAL | "critical" string in JSON |
| ConsultationLog end before start | ended_at < started_at | `ValueError` |

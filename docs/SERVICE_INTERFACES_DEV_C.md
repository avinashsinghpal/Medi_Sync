# Service Interfaces Handoff (Dev B → Dev C)

This document describes the public interfaces for the `PatientManager` and `AppointmentSystem` services. Dev C can use these definitions to wire up the FastAPI routers in `medisync/api/`.

## 1. PatientManager

Location: `medisync/patient/patient_management.py`
Instantiate with: `PatientManager(repository=PatientRepository(db), settings=Settings())`

### Public Methods

- `async def create_patient(self, data: PatientProfile) -> PatientProfile`
  Creates a new patient profile.
  **Raises:** `DuplicatePatientError`, `InvalidPatientDataError`

- `async def get_patient(self, patient_id: str) -> PatientProfile`
  Retrieves a patient by their `patient_id`.
  **Raises:** `PatientNotFoundError`

- `async def get_patient_by_email(self, email: str) -> PatientProfile`
  Retrieves a patient by their email (case-insensitive).
  **Raises:** `PatientNotFoundError`

- `async def update_patient(self, patient_id: str, updates: dict) -> PatientProfile`
  Applies partial updates to a patient profile.
  **Raises:** `PatientNotFoundError`, `InvalidPatientDataError`

- `async def deactivate_patient(self, patient_id: str) -> PatientProfile`
  Sets a patient's status to `PatientStatus.INACTIVE`.
  **Raises:** `PatientNotFoundError`

- `async def get_patient_history(self, patient_id: str, limit: int = 20, offset: int = 0) -> list[MedicalRecord]`
  Returns a paginated list of medical records for the patient, newest first.
  **Raises:** `PatientNotFoundError`

- `async def add_medical_record(self, patient_id: str, record: MedicalRecord) -> MedicalRecord`
  Adds a new medical record for the patient.
  **Raises:** `PatientNotFoundError`, `InvalidPatientDataError`

- `async def get_consultation_logs(self, patient_id: str, limit: int = 10) -> list[ConsultationLog]`
  Returns recent consultation logs for the patient, newest first.
  **Raises:** `PatientNotFoundError`

- `async def search_patients(self, query: str, limit: int = 20) -> list[PatientProfile]`
  Full-text search across `full_name`, `contact_email`, and `patient_id`. Returns empty list if no matches.
  **Raises:** `InvalidPatientDataError` (if query length < 2)

- `async def get_patient_summary(self, patient_id: str) -> dict`
  Returns a quick-summary dictionary for the dashboard view.
  **Raises:** `PatientNotFoundError`


## 2. AppointmentSystem

Location: `medisync/appointment/appointment_system.py`
Instantiate with: `AppointmentSystem(repository=AppointmentRepository(db), patient_manager=PatientManager(...), priority_engine=PriorityEngine(...), settings=Settings())`

### Public Methods

- `async def book_appointment(self, request: Appointment) -> Appointment`
  Books a new appointment, auto-calculates AI priority and estimated duration based on `symptoms_description`.
  **Raises:** `PatientNotFoundError`, `AppointmentConflictError`, `InvalidPatientDataError`

- `async def get_appointment(self, appointment_id: str) -> Appointment`
  Retrieves an appointment by its ID.
  **Raises:** `AppointmentNotFoundError`

- `async def get_patient_appointments(self, patient_id: str, status_filter: Optional[AppointmentStatus] = None) -> list[Appointment]`
  Returns all appointments for a given patient.
  **Raises:** `PatientNotFoundError`

- `async def get_doctor_queue(self, doctor_id: str, date: date) -> list[Appointment]`
  Returns today's appointments for the given doctor, ordered by priority (`CRITICAL` first), then time.

- `async def confirm_appointment(self, appointment_id: str, doctor_id: str) -> Appointment`
  Transitions state from `PENDING` to `CONFIRMED` and assigns the doctor.
  **Raises:** `AppointmentNotFoundError`, `InvalidAppointmentStateError`

- `async def start_consultation(self, appointment_id: str) -> Appointment`
  Transitions state from `CONFIRMED` to `IN_SESSION`.
  **Raises:** `AppointmentNotFoundError`, `InvalidAppointmentStateError`

- `async def complete_consultation(self, appointment_id: str, consultation_id: str) -> Appointment`
  Transitions state from `IN_SESSION` to `COMPLETED` and links the consultation ID.
  **Raises:** `AppointmentNotFoundError`, `InvalidAppointmentStateError`

- `async def cancel_appointment(self, appointment_id: str, reason: Optional[str] = None) -> Appointment`
  Transitions state to `CANCELLED` from either `PENDING` or `CONFIRMED`.
  **Raises:** `AppointmentNotFoundError`, `InvalidAppointmentStateError`

- `async def get_available_slots(self, doctor_id: str, date: date, duration_minutes: int = 15) -> list[datetime]`
  Returns a list of available (non-overlapping) start times for the doctor between 09:00 and 17:00.

- `async def get_today_summary(self, doctor_id: str) -> dict`
  Returns a structured dashboard summary for the given doctor, including metrics and the patient queue.

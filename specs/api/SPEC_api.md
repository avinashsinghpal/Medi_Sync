## Purpose
FastAPI HTTP layer — thin wrapper translating HTTP requests to service calls.
Zero business logic lives here. All logic is in service modules.

## File Location
`medisync/api/app.py`, `medisync/api/routers/`, `medisync/api/schemas/`

## Dependencies
- All service modules (via DI from `app.state`)
- `fastapi`, `pydantic`

---

## Application Factory

### `create_app() -> FastAPI`

```python
def create_app() -> FastAPI:
    app = FastAPI(
        title="MediSync AI",
        description="Unified Intelligent Patient History System",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )
    # CORS middleware
    # Error handlers
    # Register routers
    # Lifespan
    return app
```

---

## Lifespan (Startup / Shutdown)

**On startup:**
1. Load `Settings`
2. Connect to MongoDB (`motor`)
3. Initialize `PatientManager`, `AppointmentSystem`, `NLPEngine`, `SpeechProcessor`, `PriorityEngine`, `DoctorDashboard`
4. Store all services in `app.state`

**On shutdown:**
1. Close MongoDB connections
2. Unload AI models from memory

---

## Routers

### `POST /api/patients` — Create patient
- Request: `CreatePatientRequest`
- Response: `PatientResponse` (201)
- Auth: DOCTOR or ADMIN role required

### `GET /api/patients/{patient_id}` — Get patient
- Response: `PatientResponse`
- Auth: PATIENT (own only), DOCTOR, ADMIN, NURSE

### `GET /api/patients/{patient_id}/history` — Get medical history
- Query params: `limit=20&offset=0`
- Response: `MedicalHistoryResponse`
- Auth: DOCTOR, ADMIN, NURSE (read-only)

### `POST /api/patients/{patient_id}/records` — Add medical record
- Request: `CreateMedicalRecordRequest`
- Response: `MedicalRecordResponse` (201)
- Auth: DOCTOR, ADMIN

### `GET /api/patients/search` — Search patients
- Query: `q=<search_term>&limit=20`
- Response: `PatientListResponse`
- Auth: DOCTOR, ADMIN, NURSE

### `POST /api/appointments` — Book appointment
- Request: `BookAppointmentRequest`
- Response: `AppointmentResponse` (201)
- Auth: PATIENT (own), DOCTOR, ADMIN

### `GET /api/appointments/{appointment_id}` — Get appointment
- Response: `AppointmentResponse`
- Auth: All authenticated roles

### `PATCH /api/appointments/{appointment_id}/confirm` — Confirm appointment
- Auth: DOCTOR, ADMIN

### `PATCH /api/appointments/{appointment_id}/start` — Start consultation
- Auth: DOCTOR

### `PATCH /api/appointments/{appointment_id}/complete` — Complete consultation
- Request: `CompleteConsultationRequest` (includes consultation_id)
- Auth: DOCTOR

### `PATCH /api/appointments/{appointment_id}/cancel` — Cancel appointment
- Request: `CancelAppointmentRequest`
- Auth: PATIENT (own), DOCTOR, ADMIN

### `GET /api/doctor/{doctor_id}/queue` — Get doctor queue for today
- Response: `DoctorQueueResponse`
- Auth: DOCTOR (own), ADMIN

### `GET /api/dashboard/overview` — Dashboard overview
- Query: `doctor_id=<id>&date=<YYYY-MM-DD>`
- Response: `DashboardOverviewResponse`
- Auth: DOCTOR, ADMIN

### `POST /api/consultation/process` — Process consultation
- Request: `multipart/form-data` with optional `audio` + `text_input` + `appointment_id`
- Response: `ConsultationResultResponse`
- Auth: DOCTOR

### `GET /api/health` — Health check
- No auth required
- Response: `{"status": "ok", "version": "1.0.0", "db_connected": bool}`

---

## CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Error Handlers

```python
@app.exception_handler(PatientNotFoundError)     → 404
@app.exception_handler(AppointmentNotFoundError) → 404
@app.exception_handler(DuplicatePatientError)    → 409
@app.exception_handler(AppointmentConflictError) → 409
@app.exception_handler(InvalidTokenError)        → 401
@app.exception_handler(InsufficientPermissionsError) → 403
@app.exception_handler(NLPExtractionError)       → 422
@app.exception_handler(SpeechProcessingError)    → 422
@app.exception_handler(AIServiceUnavailableError) → 503
```

All error responses MUST use the standard format from `core/errors.py`.

---

## Key Pydantic Schemas

### `CreatePatientRequest`
```python
class CreatePatientRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=200)
    date_of_birth: date
    gender: str = Field(..., pattern="^(male|female|other|prefer_not_to_say)$")
    contact_email: EmailStr
    contact_phone: str = Field(..., min_length=7)
    blood_group: Optional[str] = None
    address: Optional[str] = None
```

### `BookAppointmentRequest`
```python
class BookAppointmentRequest(BaseModel):
    patient_id: str
    scheduled_at: datetime
    consultation_type: str
    symptoms_description: str = Field(..., min_length=10, max_length=2000)
    doctor_id: Optional[str] = None
    notes: Optional[str] = None
```

### `ConsultationResultResponse`
```python
class ConsultationResultResponse(BaseModel):
    consultation_id: str
    patient_id: str
    transcript: Optional[str]
    consultation_summary: str
    priority_level: str
    structured_output: dict
    prescription_text: Optional[str]
```

---

## Expected Test Outcomes (from `tests/integration/test_api.py`)

| Test | Endpoint | Expected |
|---|---|---|
| Create patient | POST /api/patients | 201 + PatientResponse |
| Duplicate patient | POST /api/patients (same email) | 409 |
| Get unknown patient | GET /api/patients/UNKNOWN | 404 |
| Book appointment | POST /api/appointments | 201 + AppointmentResponse |
| Process consultation text | POST /api/consultation/process | 200 + ConsultationResult |
| Health check | GET /api/health | 200 + status:ok |
| Unauthorized access | GET /api/patients without token | 401 |

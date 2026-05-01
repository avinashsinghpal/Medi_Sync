## Purpose
Domain-specific exception hierarchy for MediSync AI.
All custom exceptions are defined here and map cleanly to HTTP status codes.
Modules MUST raise these exceptions rather than generic Python exceptions.

## File Location
`medisync/core/errors.py`

## Dependencies
- Python stdlib only
- NO imports from any other `medisync/` module

---

## Exception Hierarchy

```python
# ── Base ─────────────────────────────────────────────────────
class MediSyncError(Exception):
    """Base class for all MediSync domain errors."""
    http_status: int = 500
    error_code: str = "INTERNAL_ERROR"

# ── Patient Errors ────────────────────────────────────────────
class PatientNotFoundError(MediSyncError):
    """Patient ID does not exist in the database."""
    http_status = 404
    error_code = "PATIENT_NOT_FOUND"

class DuplicatePatientError(MediSyncError):
    """A patient with the same identifier already exists."""
    http_status = 409
    error_code = "DUPLICATE_PATIENT"

class InvalidPatientDataError(MediSyncError):
    """Patient data failed validation (e.g. missing required fields)."""
    http_status = 422
    error_code = "INVALID_PATIENT_DATA"

# ── Appointment Errors ────────────────────────────────────────
class AppointmentNotFoundError(MediSyncError):
    """Appointment ID does not exist."""
    http_status = 404
    error_code = "APPOINTMENT_NOT_FOUND"

class AppointmentConflictError(MediSyncError):
    """Time slot already booked or doctor unavailable."""
    http_status = 409
    error_code = "APPOINTMENT_CONFLICT"

class InvalidAppointmentStateError(MediSyncError):
    """Attempted state transition is not allowed (e.g. cancelling a completed appointment)."""
    http_status = 422
    error_code = "INVALID_APPOINTMENT_STATE"

# ── Medical Record Errors ─────────────────────────────────────
class RecordNotFoundError(MediSyncError):
    """Medical record ID does not exist."""
    http_status = 404
    error_code = "RECORD_NOT_FOUND"

class RecordAccessDeniedError(MediSyncError):
    """Caller does not have permission to access this record."""
    http_status = 403
    error_code = "RECORD_ACCESS_DENIED"

# ── AI Engine Errors ──────────────────────────────────────────
class SpeechProcessingError(MediSyncError):
    """Speech-to-text conversion failed or produced unusable output."""
    http_status = 422
    error_code = "SPEECH_PROCESSING_FAILED"

class NLPExtractionError(MediSyncError):
    """NLP entity extraction failed or returned empty results."""
    http_status = 422
    error_code = "NLP_EXTRACTION_FAILED"

class AIServiceUnavailableError(MediSyncError):
    """External AI service (OpenAI, Groq, etc.) is unreachable."""
    http_status = 503
    error_code = "AI_SERVICE_UNAVAILABLE"

# ── Auth Errors ───────────────────────────────────────────────
class InvalidTokenError(MediSyncError):
    """JWT token is invalid, expired, or tampered."""
    http_status = 401
    error_code = "INVALID_TOKEN"

class InsufficientPermissionsError(MediSyncError):
    """User does not have the required role for this action."""
    http_status = 403
    error_code = "INSUFFICIENT_PERMISSIONS"

# ── Database Errors ───────────────────────────────────────────
class DatabaseConnectionError(MediSyncError):
    """Cannot connect to the database."""
    http_status = 503
    error_code = "DB_CONNECTION_FAILED"

class DatabaseOperationError(MediSyncError):
    """A database read/write operation failed."""
    http_status = 500
    error_code = "DB_OPERATION_FAILED"
```

---

## Error Response Format

All errors MUST serialize to this JSON shape when caught by the API error handlers:

```json
{
  "error_code": "PATIENT_NOT_FOUND",
  "message": "Patient with ID P-1234abcd does not exist",
  "http_status": 404,
  "details": {}
}
```

## Helper Function

```python
def format_error(exc: MediSyncError, details: dict = None) -> dict:
    """Convert a MediSyncError to the standard API error response dict."""
    ...
```

---

## Constraints

- Every module MUST catch generic exceptions and re-raise as appropriate `MediSyncError` subclass
- The `message` field MUST NOT expose internal system paths, stack traces, or raw DB errors in production
- `details` field CAN be empty dict `{}`
- Error codes MUST be SCREAMING_SNAKE_CASE

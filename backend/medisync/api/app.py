from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from medisync.core.config import get_settings
from contextlib import asynccontextmanager

from medisync.api.routers import patients, appointments, dashboard, consultation, health
from medisync.core.errors import (
    MediSyncError,
    PatientNotFoundError,
    AppointmentNotFoundError,
    DuplicatePatientError,
    AppointmentConflictError,
    InvalidTokenError,
    InsufficientPermissionsError,
    NLPExtractionError,
    SpeechProcessingError,
    AIServiceUnavailableError,
    format_error,
)
from medisync.dashboard.dashboard import DoctorDashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan: startup wires all services into app.state.

    Full wiring (production) requires live MongoDB + AI engines.
    In tests, app.state is overridden by fixtures before each test.
    """
    # Default all state slots to None — overridden in production startup
    # and in integration test fixtures.
    app.state.patient_manager = None
    app.state.appointment_system = None
    app.state.doctor_dashboard = None
    app.state.nlp_engine = None
    app.state.priority_engine = None
    app.state.speech_processor = None

    # Production startup would look like:
    #   settings = get_settings()
    #   client = AsyncIOMotorClient(settings.mongodb_url)
    #   db = client[settings.mongodb_db_name]
    #   patient_repo = PatientRepository(db)
    #   appt_repo    = AppointmentRepository(db)
    #   ...
    #   app.state.patient_manager    = PatientManager(patient_repo, settings)
    #   app.state.appointment_system = AppointmentSystem(appt_repo, patient_manager, priority_engine, settings)
    #   app.state.doctor_dashboard   = DoctorDashboard(patient_manager, appointment_system, nlp_engine, priority_engine)

    yield

    # Shutdown: close DB connections, unload AI models
    pass

_TAGS_METADATA = [
    {
        "name": "health",
        "description": "System health and liveness checks.",
    },
    {
        "name": "patients",
        "description": "Patient registration, profile management, and medical record storage.",
    },
    {
        "name": "appointments",
        "description": "Appointment booking, confirmation, and the consultation state-machine (PENDING → CONFIRMED → IN_SESSION → COMPLETED).",
    },
    {
        "name": "consultation",
        "description": "AI-powered consultation processing — accepts audio and/or text, runs NLP extraction, and returns a structured `ConsultationResult`.",
    },
    {
        "name": "dashboard",
        "description": "Doctor-facing dashboard endpoints: priority queue, daily overview, and patient summary cards.",
    },
]


def create_app() -> FastAPI:
    app = FastAPI(
        title="MediSync AI",
        description=(
            "**MediSync AI** — Unified Intelligent Patient History System.\n\n"
            "Provides a RESTful API for patient management, appointment scheduling, "
            "AI-driven consultation processing, and doctor dashboard analytics.\n\n"
            "All endpoints (except `/api/health`) require a valid **Bearer JWT** token."
        ),
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_tags=_TAGS_METADATA,
        contact={
            "name": "MediSync AI Team",
            "email": "dev@medisync.ai",
        },
        license_info={"name": "MIT"},
        lifespan=lifespan,
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_settings().allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(health.router)
    app.include_router(patients.router)
    app.include_router(appointments.router)
    app.include_router(dashboard.router)
    app.include_router(consultation.router)

    from fastapi import Request
    from fastapi.responses import JSONResponse
    from medisync.core.errors import (
        PatientNotFoundError, AppointmentNotFoundError,
        DuplicatePatientError, AppointmentConflictError,
        InvalidAppointmentStateError, InvalidPatientDataError,
        InvalidTokenError, InsufficientPermissionsError,
        NLPExtractionError, SpeechProcessingError,
        AIServiceUnavailableError, MediSyncError,
    )

    @app.exception_handler(PatientNotFoundError)
    @app.exception_handler(AppointmentNotFoundError)
    async def not_found_handler(request: Request, exc):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(DuplicatePatientError)
    @app.exception_handler(AppointmentConflictError)
    async def conflict_handler(request: Request, exc):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(InvalidPatientDataError)
    @app.exception_handler(InvalidAppointmentStateError)
    async def bad_request_handler(request: Request, exc):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(InvalidTokenError)
    async def unauthorized_handler(request: Request, exc):
        return JSONResponse(status_code=401, content={"detail": str(exc)})

    @app.exception_handler(InsufficientPermissionsError)
    async def forbidden_handler(request: Request, exc):
        return JSONResponse(status_code=403, content={"detail": str(exc)})

    @app.exception_handler(NLPExtractionError)
    @app.exception_handler(SpeechProcessingError)
    @app.exception_handler(AIServiceUnavailableError)
    async def ai_error_handler(request: Request, exc):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(MediSyncError)
    async def generic_medisync_handler(request: Request, exc):
        return JSONResponse(status_code=500, content={"detail": str(exc)})

    return app

app = create_app()

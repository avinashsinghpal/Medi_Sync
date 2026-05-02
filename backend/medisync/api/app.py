from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from medisync.api.routers import (
    appointments,
    auth,
    consultation,
    dashboard,
    doctors,
    health,
    patients,
)
from medisync.core.config import get_settings
from medisync.core.errors import (
    AIServiceUnavailableError,
    AppointmentConflictError,
    AppointmentNotFoundError,
    DuplicatePatientError,
    InsufficientPermissionsError,
    InvalidTokenError,
    MediSyncError,
    NLPExtractionError,
    PatientNotFoundError,
    SpeechProcessingError,
)
from medisync.dashboard.dashboard import DoctorDashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan: startup wires all services into app.state.
    """
    from medisync.ai_engine.nlp_engine import NLPEngine
    from medisync.ai_engine.priority_engine import PriorityEngine
    from medisync.ai_engine.speech_to_text import SpeechProcessor
    from medisync.appointment.appointment_system import AppointmentSystem
    from medisync.patient.patient_management import PatientManager
    from medisync.storage.appointment_repository import AppointmentRepository
    from medisync.storage.patient_repository import PatientRepository

    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.mongodb_db_name]

    patient_repo = PatientRepository(db)
    await patient_repo.setup_indexes()

    appt_repo = AppointmentRepository(db)
    await appt_repo.setup_indexes()

    nlp_engine = NLPEngine(settings)
    priority_engine = PriorityEngine(nlp_engine, settings)
    speech_processor = SpeechProcessor(settings)

    patient_manager = PatientManager(patient_repo, settings)
    appointment_system = AppointmentSystem(appt_repo, patient_manager, priority_engine, settings)
    doctor_dashboard = DoctorDashboard(patient_manager, appointment_system, nlp_engine, priority_engine)

    app.state.db = db
    app.state.patient_manager = patient_manager
    app.state.appointment_system = appointment_system
    app.state.doctor_dashboard = doctor_dashboard
    app.state.nlp_engine = nlp_engine
    app.state.priority_engine = priority_engine
    app.state.speech_processor = speech_processor

    yield

    client.close()

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
    app.include_router(auth.router)
    app.include_router(doctors.router)
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

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from medisync.core.config import get_settings

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
    format_error
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize services
    # Connect to MongoDB
    # Initialize Service objects and store in app.state
    app.state.patient_manager = None
    app.state.appointment_system = None
    app.state.doctor_dashboard = None
    app.state.nlp_engine = None
    app.state.priority_engine = None
    app.state.speech_processor = None
    yield
    # Shutdown: Clean up connections
    pass

def create_app() -> FastAPI:
    app = FastAPI(
        title="MediSync AI",
        description="Unified Intelligent Patient History System",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        lifespan=lifespan
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_settings().allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(health.router)
    app.include_router(patients.router)
    app.include_router(appointments.router)
    app.include_router(dashboard.router)
    app.include_router(consultation.router)

    # Error handlers
    async def custom_exception_handler(request: Request, exc: MediSyncError):
        return JSONResponse(
            status_code=exc.http_status,
            content=format_error(exc)
        )

    # Apply handler to all subclasses of MediSyncError
    app.add_exception_handler(MediSyncError, custom_exception_handler)

    return app

app = create_app()

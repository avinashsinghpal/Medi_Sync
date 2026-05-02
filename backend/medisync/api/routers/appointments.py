from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from medisync.api.schemas.appointments import (
    BookAppointmentRequest as ApiBookAppointmentRequest,
    AppointmentResponse,
    CompleteConsultationRequest,
    CancelAppointmentRequest,
)
from medisync.api.dependencies import get_appointment_system
from medisync.core.security import require_role, get_current_user, TokenData, UserRole
from medisync.appointment.appointment_system import AppointmentSystem, BookAppointmentRequest
from medisync.core.types import ConsultationType, Appointment

router = APIRouter(prefix="/api/appointments", tags=["appointments"])

class EstimateRequest(BaseModel):
    symptoms: List[str]

class EstimateResponse(BaseModel):
    priority: str
    estimatedWaitMinutes: int

def _make_response(app: Appointment) -> AppointmentResponse:
    def _v(field):
        return field.value if hasattr(field, "value") else field
    return AppointmentResponse(
        appointment_id=app.appointment_id,
        patient_id=app.patient_id,
        scheduled_at=app.scheduled_at,
        consultation_type=_v(app.consultation_type),
        symptoms_description=app.symptoms_description,
        estimated_duration_minutes=app.estimated_duration_minutes,
        doctor_id=app.doctor_id,
        status=_v(app.status),
        priority_level=_v(app.priority_level),
        notes=app.notes,
        created_at=app.created_at
    )

@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def book_appointment(
    request: ApiBookAppointmentRequest,
    raw_request: Request,
    system: AppointmentSystem = Depends(get_appointment_system),
    user: TokenData = Depends(get_current_user)
):
    if user.role == UserRole.PATIENT and request.patient_id != user.user_id:
        raise HTTPException(status_code=403, detail="Patients can only book for themselves")
    if not request.doctor_id:
        raise HTTPException(status_code=400, detail="doctor_id is required for booking")
    doctor = await raw_request.app.state.db["doctors"].find_one({"doctor_id": request.doctor_id})
    if not doctor:
        raise HTTPException(status_code=404, detail="Selected doctor not found")

    req_data = BookAppointmentRequest(
        patient_id=request.patient_id,
        scheduled_at=request.scheduled_at,
        consultation_type=ConsultationType(request.consultation_type),
        symptoms_description=request.symptoms_description,
        doctor_id=request.doctor_id,
        notes=request.notes
    )
    app = await system.book_appointment(req_data)
    return _make_response(app)

@router.post("/estimate", response_model=EstimateResponse)
async def estimate_priority(
    request: EstimateRequest,
    system: AppointmentSystem = Depends(get_appointment_system),
    user: TokenData = Depends(get_current_user)
):
    text = " ".join(request.symptoms)
    try:
        assessment = await system.priority_engine.predict_priority(text, {})
        priority = assessment.priority_level.value
        duration = assessment.estimated_duration_minutes
    except Exception:
        # Fallback
        is_critical = any(k in text.lower() for k in ["chest pain", "breathing", "bleeding"])
        priority = "critical" if is_critical else "routine"
        duration = 5 if is_critical else 45

    return EstimateResponse(
        priority=priority,
        estimatedWaitMinutes=duration
    )

@router.get("/patient/{patient_id}", response_model=List[AppointmentResponse])
async def get_patient_appointments(
    patient_id: str,
    system: AppointmentSystem = Depends(get_appointment_system),
    user: TokenData = Depends(get_current_user)
):
    if user.role == UserRole.PATIENT and patient_id != user.user_id:
        raise HTTPException(status_code=403, detail="Cannot access others' appointments")
        
    apps = await system.get_patient_appointments(patient_id)
    return [_make_response(app) for app in apps]

@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: str,
    system: AppointmentSystem = Depends(get_appointment_system),
    user: TokenData = Depends(get_current_user)
):
    app = await system.get_appointment(appointment_id)
    if user.role == UserRole.PATIENT and app.patient_id != user.user_id:
        raise HTTPException(status_code=403, detail="Cannot access others' appointments")
        
    return _make_response(app)

@router.patch("/{appointment_id}/confirm", response_model=AppointmentResponse)
async def confirm_appointment(
    appointment_id: str,
    system: AppointmentSystem = Depends(get_appointment_system),
    user: TokenData = Depends(require_role(UserRole.DOCTOR, UserRole.ADMIN))
):
    # Pass user_id as doctor_id for confirmation if needed
    app = await system.confirm_appointment(appointment_id, doctor_id=user.user_id)
    return _make_response(app)

@router.patch("/{appointment_id}/start", response_model=AppointmentResponse)
async def start_consultation(
    appointment_id: str,
    system: AppointmentSystem = Depends(get_appointment_system),
    user: TokenData = Depends(require_role(UserRole.DOCTOR))
):
    app = await system.start_consultation(appointment_id)
    return _make_response(app)

@router.patch("/{appointment_id}/complete", response_model=AppointmentResponse)
async def complete_consultation(
    appointment_id: str, 
    request: CompleteConsultationRequest,
    system: AppointmentSystem = Depends(get_appointment_system),
    user: TokenData = Depends(require_role(UserRole.DOCTOR))
):
    app = await system.complete_consultation(appointment_id, request.consultation_id, request.summary)
    return _make_response(app)

@router.patch("/{appointment_id}/cancel", response_model=AppointmentResponse)
async def cancel_appointment(
    appointment_id: str, 
    request: CancelAppointmentRequest,
    system: AppointmentSystem = Depends(get_appointment_system),
    user: TokenData = Depends(get_current_user)
):
    app = await system.cancel_appointment(appointment_id, request.reason)
    return _make_response(app)

from fastapi import APIRouter, Depends, HTTPException, status
from medisync.api.schemas.appointments import (
    BookAppointmentRequest,
    AppointmentResponse,
    CompleteConsultationRequest,
    CancelAppointmentRequest,
)

router = APIRouter(prefix="/api/appointments", tags=["appointments"])

@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def book_appointment(request: BookAppointmentRequest):
    raise HTTPException(status_code=501, detail="Not implemented")

@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(appointment_id: str):
    raise HTTPException(status_code=501, detail="Not implemented")

@router.patch("/{appointment_id}/confirm")
async def confirm_appointment(appointment_id: str):
    raise HTTPException(status_code=501, detail="Not implemented")

@router.patch("/{appointment_id}/start")
async def start_consultation(appointment_id: str):
    raise HTTPException(status_code=501, detail="Not implemented")

@router.patch("/{appointment_id}/complete")
async def complete_consultation(appointment_id: str, request: CompleteConsultationRequest):
    raise HTTPException(status_code=501, detail="Not implemented")

@router.patch("/{appointment_id}/cancel")
async def cancel_appointment(appointment_id: str, request: CancelAppointmentRequest):
    raise HTTPException(status_code=501, detail="Not implemented")

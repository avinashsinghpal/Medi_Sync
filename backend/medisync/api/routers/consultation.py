"""Consultation router — wired to DoctorDashboard.process_consultation."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional

from medisync.api.schemas.consultations import ConsultationResultResponse
from medisync.core.security import require_role, TokenData, UserRole
from medisync.dashboard.dashboard import DoctorDashboard

router = APIRouter(prefix="/api/consultation", tags=["consultation"])


async def _get_dashboard(request: "Request") -> DoctorDashboard:
    return request.app.state.doctor_dashboard


from fastapi import Request


@router.post("/process", response_model=ConsultationResultResponse)
async def process_consultation(
    appointment_id: str = Form(...),
    text_input: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None),
    request: Request = None,
    user: TokenData = Depends(require_role(UserRole.DOCTOR)),
):
    """
    Process a consultation: accepts optional audio upload and/or text input,
    runs the full NLP pipeline, and returns a structured ConsultationResult.
    Auth: DOCTOR only.
    """
    audio_data: Optional[bytes] = None
    if audio is not None:
        audio_data = await audio.read()

    dashboard: DoctorDashboard = await _get_dashboard(request)
    result = await dashboard.process_consultation(
        appointment_id=appointment_id,
        audio_data=audio_data,
        text_input=text_input,
    )

    return ConsultationResultResponse(
        consultation_id=result.consultation_id,
        patient_id=result.patient_id,
        transcript=result.transcript,
        consultation_summary=result.consultation_summary,
        priority_level=result.priority_level,
        structured_output=result.structured_output,
        prescription_text=result.prescription_text,
        recommended_follow_up=result.recommended_follow_up,
    )

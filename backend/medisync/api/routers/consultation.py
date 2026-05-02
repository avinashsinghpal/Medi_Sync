from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional
from medisync.api.schemas.consultations import ConsultationResultResponse

router = APIRouter(prefix="/api/consultation", tags=["consultation"])

@router.post("/process", response_model=ConsultationResultResponse)
async def process_consultation(
    appointment_id: Optional[str] = Form(None),
    text_input: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None)
):
    raise HTTPException(status_code=501, detail="Not implemented")

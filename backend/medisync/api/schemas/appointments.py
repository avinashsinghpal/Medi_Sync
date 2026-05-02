from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class BookAppointmentRequest(BaseModel):
    patient_id: str
    scheduled_at: datetime
    consultation_type: str
    symptoms_description: str = Field(..., min_length=10, max_length=2000)
    doctor_id: Optional[str] = None
    notes: Optional[str] = None

class AppointmentResponse(BaseModel):
    appointment_id: str
    patient_id: str
    scheduled_at: datetime
    consultation_type: str
    symptoms_description: str
    estimated_duration_minutes: int
    doctor_id: Optional[str] = None
    status: str
    priority_level: str
    notes: Optional[str] = None
    created_at: datetime

class CompleteConsultationRequest(BaseModel):
    consultation_id: str
    summary: Optional[str] = None

class CancelAppointmentRequest(BaseModel):
    reason: Optional[str] = None

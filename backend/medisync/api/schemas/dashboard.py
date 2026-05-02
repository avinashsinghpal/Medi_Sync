from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .appointments import AppointmentResponse

class DoctorQueueItem(BaseModel):
    appointment: AppointmentResponse
    status: str
    priority: str

class DoctorQueueResponse(BaseModel):
    doctor_id: str
    date: datetime
    queue: List[DoctorQueueItem]

class DashboardOverviewResponse(BaseModel):
    total_patients: int
    pending_appointments: int
    critical_cases: int
    recent_activities: List[dict] = []

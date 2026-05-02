"""Pydantic response schemas for dashboard and doctor-queue endpoints."""
from __future__ import annotations

from pydantic import BaseModel
from typing import List, Optional
from datetime import date as DateType


class PatientQueueItemResponse(BaseModel):
    queue_position: int
    patient_id: str
    patient_name: str
    age: int
    appointment_id: str
    scheduled_at: str
    priority_level: str
    priority_badge_color: str
    symptoms_preview: str
    estimated_duration_minutes: int
    status: str
    risk_flags: List[str] = []


class DoctorQueueResponse(BaseModel):
    doctor_id: str
    date: str
    queue: List[PatientQueueItemResponse]


class DashboardOverviewResponse(BaseModel):
    doctor_id: str
    date: str
    total_patients_today: int
    critical_count: int
    moderate_count: int
    routine_count: int
    completed_consultations: int
    pending_consultations: int
    estimated_remaining_hours: float
    priority_queue: List[PatientQueueItemResponse]
    recent_activity: List[dict] = []


class PatientSummaryCardResponse(BaseModel):
    patient_id: str
    full_name: str
    age: int
    blood_group: Optional[str] = None
    status: str
    priority_level: str
    risk_indicators: List[str] = []
    recent_diagnoses: List[str] = []
    current_medications: List[str] = []
    last_visit_date: Optional[str] = None
    total_visits: int
    consultation_history_preview: List[dict] = []
    quick_actions: List[str] = []

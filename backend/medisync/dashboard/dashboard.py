from datetime import date, datetime
from dataclasses import dataclass, field
from typing import Optional, List
import uuid

from medisync.core.types import PriorityLevel, AppointmentStatus, ConsultationLog, utc_now, generate_uuid
from medisync.core.errors import NLPExtractionError
from medisync.patient.patient_management import PatientManager
from medisync.appointment.appointment_system import AppointmentSystem
from medisync.ai_engine.nlp_engine import NLPEngine
from medisync.ai_engine.priority_engine import PriorityEngine

@dataclass
class PatientQueueItem:
    queue_position: int
    patient_id: str
    patient_name: str
    age: int
    appointment_id: str
    scheduled_at: str
    priority_level: str                 # "critical" | "moderate" | "routine"
    priority_badge_color: str           # "red" | "yellow" | "green"
    symptoms_preview: str              # First 100 chars of symptoms
    estimated_duration_minutes: int
    status: str                        # appointment status
    risk_flags: list[str]

@dataclass
class DashboardOverview:
    doctor_id: str
    date: str                           # ISO date
    total_patients_today: int
    critical_count: int
    moderate_count: int
    routine_count: int
    completed_consultations: int
    pending_consultations: int
    estimated_remaining_hours: float
    priority_queue: list[PatientQueueItem]
    recent_activity: list[dict]

@dataclass
class PatientSummaryCard:
    patient_id: str
    full_name: str
    age: int
    blood_group: Optional[str]
    status: str
    priority_level: str
    risk_indicators: list[str]
    recent_diagnoses: list[str]
    current_medications: list[str]
    last_visit_date: Optional[str]
    total_visits: int
    consultation_history_preview: list[dict]
    quick_actions: list[str]

@dataclass
class ConsultationResult:
    consultation_id: str
    patient_id: str
    doctor_id: str
    transcript: Optional[str]
    extracted_data: dict
    consultation_summary: str
    priority_level: str
    prescription_text: Optional[str]
    recommended_follow_up: Optional[str]
    structured_output: dict

class DoctorDashboard:
    def __init__(
        self,
        patient_manager: PatientManager,
        appointment_system: AppointmentSystem,
        nlp_engine: NLPEngine,
        priority_engine: PriorityEngine,
    ):
        self.patient_manager = patient_manager
        self.appointment_system = appointment_system
        self.nlp_engine = nlp_engine
        self.priority_engine = priority_engine

    def _get_badge_color(self, priority: PriorityLevel) -> str:
        if priority == PriorityLevel.CRITICAL:
            return "red"
        elif priority == PriorityLevel.MODERATE:
            return "yellow"
        return "green"

    async def get_patient_queue(self, doctor_id: str, query_date: date) -> List[PatientQueueItem]:
        appointments = await self.appointment_system.get_doctor_queue(doctor_id, query_date)
        queue = []
        for idx, app in enumerate(appointments):
            patient = await self.patient_manager.get_patient(app.patient_id)
            
            symptoms = app.symptoms_description or ""
            preview = symptoms[:97] + "..." if len(symptoms) > 100 else symptoms
            
            # Predict priority specifically for queue visualization to get risk flags
            risk_res = await self.priority_engine.predict_priority(symptoms, {})
            risk_flags = risk_res.urgent_flags if risk_res else []

            item = PatientQueueItem(
                queue_position=idx + 1,
                patient_id=app.patient_id,
                patient_name=patient.full_name,
                age=patient.age,
                appointment_id=app.appointment_id,
                scheduled_at=app.scheduled_at.isoformat(),
                priority_level=app.priority_level.value,
                priority_badge_color=self._get_badge_color(app.priority_level),
                symptoms_preview=preview,
                estimated_duration_minutes=app.estimated_duration_minutes,
                status=app.status.value,
                risk_flags=risk_flags
            )
            queue.append(item)
        return queue

    async def get_dashboard_overview(self, doctor_id: str, query_date: date) -> DashboardOverview:
        queue = await self.get_patient_queue(doctor_id, query_date)
        
        appointments = await self.appointment_system.repository.get_by_doctor_and_date(doctor_id, query_date)
        
        critical_count = sum(1 for a in appointments if a.priority_level == PriorityLevel.CRITICAL)
        moderate_count = sum(1 for a in appointments if a.priority_level == PriorityLevel.MODERATE)
        routine_count = sum(1 for a in appointments if a.priority_level == PriorityLevel.ROUTINE)
        
        completed = sum(1 for a in appointments if a.status == AppointmentStatus.COMPLETED)
        pending = sum(1 for a in appointments if a.status == AppointmentStatus.PENDING)
        est_hours = sum(a.estimated_duration_minutes for a in appointments if a.status != AppointmentStatus.COMPLETED) / 60.0
        
        recent_activity = [] # Placeholder for now

        return DashboardOverview(
            doctor_id=doctor_id,
            date=query_date.isoformat(),
            total_patients_today=len(appointments),
            critical_count=critical_count,
            moderate_count=moderate_count,
            routine_count=routine_count,
            completed_consultations=completed,
            pending_consultations=pending,
            estimated_remaining_hours=round(est_hours, 2),
            priority_queue=queue,
            recent_activity=recent_activity
        )

    async def get_patient_summary_card(self, patient_id: str) -> PatientSummaryCard:
        patient_summary = await self.patient_manager.get_patient_summary(patient_id)
        profile = await self.patient_manager.get_patient(patient_id)
        history = await self.patient_manager.get_consultation_logs(patient_id, limit=3)
        
        history_preview = [{"date": h.started_at.isoformat(), "notes": h.notes} for h in history]
        
        risk_indicators = []
        if profile.age > 65:
            risk_indicators.append("Elderly")
            
        last_visit_str = None
        if history:
            last_visit_str = history[0].started_at.isoformat()

        return PatientSummaryCard(
            patient_id=patient_id,
            full_name=profile.full_name,
            age=profile.age,
            blood_group=profile.blood_group,
            status=profile.status.value,
            priority_level=patient_summary.get("priority_level", "routine"),
            risk_indicators=risk_indicators,
            recent_diagnoses=patient_summary.get("recent_diagnoses", []),
            current_medications=patient_summary.get("current_medications", []),
            last_visit_date=last_visit_str,
            total_visits=patient_summary.get("total_records", 0),
            consultation_history_preview=history_preview,
            quick_actions=["start_consultation", "view_history", "add_record"]
        )

    async def process_consultation(self, appointment_id: str, audio_data: Optional[bytes], text_input: Optional[str]) -> ConsultationResult:
        appointment = await self.appointment_system.get_appointment(appointment_id)
        
        if not audio_data and not text_input:
            raise NLPExtractionError("Must provide either audio or text input for consultation processing.")
            
        transcript = text_input or "Transcript from audio..."
        
        extracted = await self.nlp_engine.extract_from_text(transcript)
        
        summary = extracted.summary
        
        priority_res = await self.priority_engine.predict_priority(transcript, {})
        
        consultation_id = generate_uuid()
        
        structured_out = {
            "patient_id": appointment.patient_id,
            "symptoms": extracted.symptoms,
            "risk_level": priority_res.priority_level.value,
            "medications": extracted.medications,
            "consultation_time": "15 minutes",
            "priority": priority_res.priority_level.value.capitalize()
        }
        
        return ConsultationResult(
            consultation_id=consultation_id,
            patient_id=appointment.patient_id,
            doctor_id=appointment.doctor_id or "UNKNOWN",
            transcript=transcript,
            extracted_data={
                "symptoms": extracted.symptoms,
                "medications": extracted.medications,
                "vitals": extracted.vitals
            },
            consultation_summary=summary,
            priority_level=priority_res.priority_level.value,
            prescription_text=None,
            recommended_follow_up=None,
            structured_output=structured_out
        )

    async def get_analytics(self, doctor_id: str, date_from: date, date_to: date) -> dict:
        return {
            "total_consultations": 0,
            "avg_consultation_duration_minutes": 0.0,
            "priority_breakdown": {"critical": 0, "moderate": 0, "routine": 0},
            "most_common_symptoms": [],
            "patient_satisfaction_avg": 0.0,
            "busiest_day": date_from.isoformat()
        }

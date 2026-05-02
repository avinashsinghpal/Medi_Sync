from datetime import datetime, date, timedelta, timezone
from dataclasses import dataclass
from typing import Optional, List

from medisync.core.types import Appointment, AppointmentStatus, ConsultationType, PriorityLevel, generate_uuid, utc_now
from medisync.core.errors import InvalidPatientDataError, AppointmentConflictError, InvalidAppointmentStateError, AppointmentNotFoundError
from medisync.core.config import Settings
from medisync.storage.appointment_repository import AppointmentRepository
from medisync.patient.patient_management import PatientManager

# Mocking PriorityEngine for type hinting if it's not implemented yet
try:
    from medisync.ai_engine.priority_engine import PriorityEngine
except ImportError:
    class PriorityEngine:
        async def predict_priority(self, symptoms_description: str) -> PriorityLevel: ...
        async def estimate_duration(self, symptoms_description: str, patient_history: list) -> int: ...

@dataclass
class BookAppointmentRequest:
    patient_id: str
    scheduled_at: datetime
    consultation_type: ConsultationType
    symptoms_description: str
    doctor_id: Optional[str] = None
    notes: Optional[str] = None

class AppointmentSystem:
    def __init__(
        self,
        repository: AppointmentRepository,
        patient_manager: PatientManager,
        priority_engine: PriorityEngine,
        settings: Settings
    ):
        self.repository = repository
        self.patient_manager = patient_manager
        self.priority_engine = priority_engine
        self.settings = settings

    async def book_appointment(self, request: BookAppointmentRequest) -> Appointment:
        # 1. Validate patient exists
        await self.patient_manager.get_patient(request.patient_id)
        
        # 2. Validate scheduled_at is in the future
        if request.scheduled_at < utc_now():
            raise InvalidPatientDataError("scheduled_at MUST be in the future")
            
        # 3. Validate symptoms_description
        if not request.symptoms_description or len(request.symptoms_description.strip()) < 10:
            raise InvalidPatientDataError("symptoms_description MUST NOT be empty (minimum 10 characters)")

        # 4. Predict priority and duration
        priority = await self.priority_engine.predict_priority(request.symptoms_description)
        # Getting history for duration estimate
        history = await self.patient_manager.get_patient_history(request.patient_id)
        duration = await self.priority_engine.estimate_duration(request.symptoms_description, history)
        
        # 5. Check for slot conflicts if doctor is assigned
        if request.doctor_id:
            is_available = await self._check_slot_availability(request.doctor_id, request.scheduled_at, duration)
            if not is_available:
                raise AppointmentConflictError("Time slot already booked or doctor unavailable")

        # 6. Create Appointment
        app = Appointment(
            appointment_id=generate_uuid(),
            patient_id=request.patient_id,
            doctor_id=request.doctor_id,
            scheduled_at=request.scheduled_at,
            consultation_type=request.consultation_type,
            status=AppointmentStatus.PENDING,
            symptoms_description=request.symptoms_description,
            priority_level=priority,
            estimated_duration_minutes=duration,
            notes=request.notes,
            created_at=utc_now()
        )
        
        # 7. Persist and return
        await self.repository.create(app)
        return app

    async def get_appointment(self, appointment_id: str) -> Appointment:
        app = await self.repository.get_by_id(appointment_id)
        if not app:
            raise AppointmentNotFoundError(f"Appointment {appointment_id} not found")
        return app

    async def get_patient_appointments(self, patient_id: str, status_filter: Optional[AppointmentStatus] = None) -> List[Appointment]:
        await self.patient_manager.get_patient(patient_id)
        return await self.repository.get_by_patient_id(patient_id, status_filter)

    async def get_doctor_queue(self, doctor_id: str, d: date) -> List[Appointment]:
        apps = await self.repository.get_by_doctor_and_date(doctor_id, d)
        
        def sort_key(app):
            # Sort by priority level DESC, then scheduled_at ASC
            # Priority values: CRITICAL, MODERATE, ROUTINE
            priority_score = {
                PriorityLevel.CRITICAL: 1,
                PriorityLevel.MODERATE: 2,
                PriorityLevel.ROUTINE: 3
            }.get(app.priority_level, 3)
            return (priority_score, app.scheduled_at)
            
        return sorted(apps, key=sort_key)

    async def confirm_appointment(self, appointment_id: str, doctor_id: str) -> Appointment:
        app = await self.get_appointment(appointment_id)
        if app.status != AppointmentStatus.PENDING:
            raise InvalidAppointmentStateError(f"Cannot confirm appointment in state {app.status}")
            
        app.status = AppointmentStatus.CONFIRMED
        if not app.doctor_id:
            app.doctor_id = doctor_id
            
        await self.repository.update(app)
        return app

    async def start_consultation(self, appointment_id: str) -> Appointment:
        app = await self.get_appointment(appointment_id)
        if app.status != AppointmentStatus.CONFIRMED:
            raise InvalidAppointmentStateError(f"Cannot start consultation for appointment in state {app.status}")
            
        app.status = AppointmentStatus.IN_SESSION
        await self.repository.update(app)
        return app

    async def complete_consultation(self, appointment_id: str, consultation_id: str) -> Appointment:
        app = await self.get_appointment(appointment_id)
        if app.status != AppointmentStatus.IN_SESSION:
            raise InvalidAppointmentStateError(f"Cannot complete consultation for appointment in state {app.status}")
            
        app.status = AppointmentStatus.COMPLETED
        # link consultation_id could be added to notes or we need to update ConsultationLog directly.
        if app.notes:
            app.notes += f"\nConsultation ID: {consultation_id}"
        else:
            app.notes = f"Consultation ID: {consultation_id}"
            
        await self.repository.update(app)
        return app

    async def cancel_appointment(self, appointment_id: str, reason: Optional[str] = None) -> Appointment:
        app = await self.get_appointment(appointment_id)
        if app.status not in [AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]:
            raise InvalidAppointmentStateError(f"Cannot cancel appointment in state {app.status}")
            
        app.status = AppointmentStatus.CANCELLED
        if reason:
            if app.notes:
                app.notes += f"\nCancellation reason: {reason}"
            else:
                app.notes = f"Cancellation reason: {reason}"
                
        await self.repository.update(app)
        return app

    async def get_available_slots(self, doctor_id: str, target_date: date, duration_minutes: int = 15) -> List[datetime]:
        if target_date.weekday() >= 5: # Saturday or Sunday
            return []
            
        # 09:00 to 17:00
        start_time = datetime(target_date.year, target_date.month, target_date.day, 9, 0, tzinfo=timezone.utc)
        end_time = datetime(target_date.year, target_date.month, target_date.day, 17, 0, tzinfo=timezone.utc)
        
        apps = await self.repository.get_by_doctor_and_date(doctor_id, target_date)
        
        slots = []
        current_time = start_time
        while current_time + timedelta(minutes=duration_minutes) <= end_time:
            slot_end = current_time + timedelta(minutes=duration_minutes)
            
            # Check overlap with any existing appointment
            conflict = False
            for app in apps:
                app_start = app.scheduled_at
                app_end = app_start + timedelta(minutes=app.estimated_duration_minutes)
                
                if current_time < app_end and slot_end > app_start:
                    conflict = True
                    break
                    
            if not conflict:
                slots.append(current_time)
                
            current_time += timedelta(minutes=duration_minutes)
            
        return slots

    async def get_today_summary(self, doctor_id: str) -> dict:
        today = utc_now().date()
        apps = await self.repository.get_by_doctor_and_date(doctor_id, today)
        
        completed = sum(1 for a in apps if a.status == AppointmentStatus.COMPLETED)
        pending = sum(1 for a in apps if a.status == AppointmentStatus.PENDING)
        critical = sum(1 for a in apps if a.priority_level == PriorityLevel.CRITICAL)
        est_hours = sum(a.estimated_duration_minutes for a in apps) / 60.0
        
        queue = await self.get_doctor_queue(doctor_id, today)
        queue_data = [{"appointment_id": a.appointment_id, "patient_id": a.patient_id, "priority": a.priority_level.value} for a in queue]
        
        return {
            "date": today.isoformat(),
            "total_appointments": len(apps),
            "completed": completed,
            "pending": pending,
            "critical_count": critical,
            "estimated_hours": round(est_hours, 2),
            "queue": queue_data
        }

    async def _check_slot_availability(self, doctor_id: str, start_time: datetime, duration_minutes: int) -> bool:
        end_time = start_time + timedelta(minutes=duration_minutes)
        overlapping = await self.repository.get_overlapping(doctor_id, start_time, end_time)
        return len(overlapping) == 0

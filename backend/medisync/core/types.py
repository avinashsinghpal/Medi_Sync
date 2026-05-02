import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional


class PatientStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCHARGED = "discharged"
    CRITICAL = "critical"


class PriorityLevel(str, Enum):
    CRITICAL = "critical"
    MODERATE = "moderate"
    ROUTINE = "routine"


class AppointmentStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_SESSION = "in_session"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class ConsultationType(str, Enum):
    IN_PERSON = "in_person"
    TELECONSULT = "teleconsult"
    FOLLOW_UP = "follow_up"
    EMERGENCY = "emergency"


def generate_patient_id() -> str:
    return f"P-{str(uuid.uuid4())[:8]}"


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class PatientProfile:
    full_name: str
    date_of_birth: date
    gender: str
    contact_email: str
    contact_phone: str
    patient_id: str = field(default_factory=generate_patient_id)
    blood_group: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    status: PatientStatus = PatientStatus.ACTIVE
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)
    metadata: dict = field(default_factory=dict)

    @property
    def age(self) -> int:
        """Return current age in years based on date_of_birth."""
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )


@dataclass
class MedicalRecord:
    patient_id: str
    record_type: str
    title: str
    content: str
    record_id: str = field(default_factory=generate_uuid)
    consultation_id: Optional[str] = None
    doctor_id: Optional[str] = None
    hospital_id: Optional[str] = None
    recorded_at: datetime = field(default_factory=utc_now)
    tags: list[str] = field(default_factory=list)
    attachments: list[str] = field(default_factory=list)


@dataclass
class ConsultationLog:
    patient_id: str
    doctor_id: str
    started_at: datetime
    extracted_symptoms: list[str]
    extracted_medications: list[str]
    extracted_dosages: dict
    estimated_duration_minutes: int
    notes: str
    consultation_id: str = field(default_factory=generate_uuid)
    appointment_id: Optional[str] = None
    ended_at: Optional[datetime] = None
    raw_transcript: Optional[str] = None
    diagnosis: Optional[str] = None
    prescription_text: Optional[str] = None
    priority_level: PriorityLevel = PriorityLevel.ROUTINE
    consultation_summary: Optional[str] = None


@dataclass
class Appointment:
    patient_id: str
    scheduled_at: datetime
    consultation_type: ConsultationType
    symptoms_description: str
    estimated_duration_minutes: int
    appointment_id: str = field(default_factory=generate_uuid)
    doctor_id: Optional[str] = None
    status: AppointmentStatus = AppointmentStatus.PENDING
    priority_level: PriorityLevel = PriorityLevel.ROUTINE
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=utc_now)


def validate_patient_profile(patient: PatientProfile) -> None:
    """Raise ValueError with descriptive message for any invalid PatientProfile field."""
    if not patient.full_name or not patient.full_name.strip():
        raise ValueError("full_name MUST NOT be empty")
    valid_genders = {"male", "female", "other", "prefer_not_to_say"}
    if patient.gender not in valid_genders:
        raise ValueError(f"gender MUST be one of {valid_genders}")


def validate_appointment(appointment: Appointment) -> None:
    """Raise ValueError for any invalid Appointment field."""
    if not appointment.symptoms_description or len(appointment.symptoms_description.strip()) < 10:
        raise ValueError("symptoms_description MUST NOT be empty (minimum 10 characters)")
    
    # Check if scheduled_at is in the future. We compare with UTC now.
    # Note: the spec says "MUST be in the future at time of creation". We'll do a simple comparison.
    if appointment.scheduled_at < datetime.now(appointment.scheduled_at.tzinfo or timezone.utc):
        raise ValueError("scheduled_at MUST be in the future at time of creation")


def validate_medical_record(record: MedicalRecord) -> None:
    """Raise ValueError for any invalid MedicalRecord field."""
    valid_record_types = {"diagnosis", "prescription", "lab_result", "imaging", "note"}
    if record.record_type not in valid_record_types:
        raise ValueError("unknown record_type")
    if not record.content or not record.content.strip():
        raise ValueError("content MUST NOT be empty")


def validate_consultation_log(log: ConsultationLog) -> None:
    """Raise ValueError for any invalid ConsultationLog field."""
    if log.ended_at is not None and log.ended_at < log.started_at:
        raise ValueError("ended_at MUST be after started_at")

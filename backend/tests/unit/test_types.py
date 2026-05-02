import pytest
from datetime import datetime, date, timezone
from medisync.core.types import (
    PatientProfile, 
    Appointment, 
    AppointmentStatus, 
    ConsultationType, 
    PriorityLevel,
    ConsultationLog,
    MedicalRecord
)

def test_patient_profile_validation():
    """Test PatientProfile creation and defaults."""
    patient = PatientProfile(
        patient_id="P-123",
        full_name="John Doe",
        date_of_birth=date(1990, 1, 1),
        gender="male",
        contact_email="john@example.com",
        contact_phone="+1234567890"
    )
    assert patient.patient_id == "P-123"
    assert patient.full_name == "John Doe"
    assert patient.blood_group is None
    assert isinstance(patient.created_at, datetime)

def test_appointment_defaults():
    """Test Appointment creation and status defaults."""
    now = datetime.now(timezone.utc)
    app = Appointment(
        patient_id="P-123",
        scheduled_at=now,
        consultation_type=ConsultationType.IN_PERSON,
        symptoms_description="Headache",
        estimated_duration_minutes=15
    )
    assert app.status == AppointmentStatus.PENDING
    assert app.priority_level == PriorityLevel.ROUTINE
    assert app.scheduled_at == now

def test_priority_level_enum():
    """Test PriorityLevel values."""
    assert PriorityLevel.CRITICAL.value == "critical"
    assert PriorityLevel.MODERATE.value == "moderate"
    assert PriorityLevel.ROUTINE.value == "routine"

def test_consultation_log_creation():
    """Test ConsultationLog metadata."""
    log = ConsultationLog(
        patient_id="P-123",
        doctor_id="D-1",
        started_at=datetime.now(timezone.utc),
        extracted_symptoms=["cough", "fever"],
        extracted_medications=["paracetamol"],
        extracted_dosages={"paracetamol": "500mg"},
        estimated_duration_minutes=15,
        notes="Rest advised",
        appointment_id="A-1"
    )
    assert "paracetamol" in log.extracted_medications
    # Consultation ID is a plain UUID from generate_uuid()
    assert len(log.consultation_id) >= 32

def test_medical_record_types():
    """Test MedicalRecord structure."""
    record = MedicalRecord(
        patient_id="P-123",
        record_type="note",
        title="Checkup",
        content="Normal results",
        record_id="REC-1",
        doctor_id="D-1",
        recorded_at=datetime.now(timezone.utc)
    )
    assert record.record_type == "note"
    assert isinstance(record.tags, list)

import json
import pytest
from datetime import date, datetime, timedelta, timezone
from medisync.core.types import (
    PatientProfile,
    PatientStatus,
    PriorityLevel,
    AppointmentStatus,
    ConsultationType,
    Appointment,
    MedicalRecord,
    ConsultationLog,
    validate_patient_profile,
    validate_appointment,
    validate_medical_record,
    validate_consultation_log,
)


def test_patient_profile_auto_id():
    # No patient_id provided -> "P-XXXXXXXX" format UUID
    patient = PatientProfile(
        full_name="John Doe",
        date_of_birth=date(1980, 1, 1),
        gender="male",
        contact_email="john@example.com",
        contact_phone="+1234567890",
    )
    assert patient.patient_id.startswith("P-")
    assert len(patient.patient_id) == 10  # 'P-' + 8 chars


def test_patient_profile_empty_name():
    patient = PatientProfile(
        full_name="   ",
        date_of_birth=date(1980, 1, 1),
        gender="male",
        contact_email="john@example.com",
        contact_phone="+1234567890",
    )
    with pytest.raises(ValueError, match="full_name MUST NOT be empty"):
        validate_patient_profile(patient)


def test_patient_profile_age():
    # dob=1990-01-01 -> Integer >= 34
    patient = PatientProfile(
        full_name="Jane Doe",
        date_of_birth=date(1990, 1, 1),
        gender="female",
        contact_email="jane@example.com",
        contact_phone="+1234567890",
    )
    assert isinstance(patient.age, int)
    assert patient.age >= 34


def test_appointment_past_date():
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    appointment = Appointment(
        patient_id="P-12345678",
        scheduled_at=yesterday,
        consultation_type=ConsultationType.IN_PERSON,
        symptoms_description="Severe headache and fever",
        estimated_duration_minutes=30,
    )
    with pytest.raises(ValueError, match="scheduled_at MUST be in the future at time of creation"):
        validate_appointment(appointment)


def test_appointment_empty_symptoms():
    future_date = datetime.now(timezone.utc) + timedelta(days=1)
    appointment = Appointment(
        patient_id="P-12345678",
        scheduled_at=future_date,
        consultation_type=ConsultationType.IN_PERSON,
        symptoms_description="short",  # Less than 10 characters
        estimated_duration_minutes=30,
    )
    with pytest.raises(ValueError, match="symptoms_description MUST NOT be empty \\(minimum 10 characters\\)"):
        validate_appointment(appointment)


def test_medical_record_bad_type():
    record = MedicalRecord(
        patient_id="P-12345678",
        record_type="xray",
        title="Chest X-Ray",
        content="Clear",
    )
    with pytest.raises(ValueError, match="unknown record_type"):
        validate_medical_record(record)


def test_priority_level_serialization():
    # PriorityLevel.CRITICAL -> "critical" string in JSON
    data = {"priority": PriorityLevel.CRITICAL}
    json_str = json.dumps(data)
    assert '"critical"' in json_str


def test_consultation_log_end_before_start():
    start_time = datetime.now(timezone.utc)
    end_time = start_time - timedelta(minutes=10)
    log = ConsultationLog(
        patient_id="P-12345678",
        doctor_id="D-123",
        started_at=start_time,
        ended_at=end_time,
        extracted_symptoms=[],
        extracted_medications=[],
        extracted_dosages={},
        estimated_duration_minutes=15,
        notes="Patient left early",
    )
    with pytest.raises(ValueError, match="ended_at MUST be after started_at"):
        validate_consultation_log(log)

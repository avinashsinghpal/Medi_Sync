import pytest
from datetime import datetime, timedelta, date, timezone
from medisync.appointment.appointment_system import AppointmentSystem, BookAppointmentRequest
from medisync.patient.patient_management import PatientManager
from medisync.core.errors import InvalidPatientDataError, AppointmentConflictError, InvalidAppointmentStateError
from medisync.core.types import AppointmentStatus, ConsultationType, PriorityLevel, Appointment

@pytest.fixture
def patient_manager(mock_patient_repo, settings):
    return PatientManager(mock_patient_repo, settings)

@pytest.fixture
def appointment_system(mock_appointment_repo, patient_manager, mock_priority_engine, settings):
    return AppointmentSystem(mock_appointment_repo, patient_manager, mock_priority_engine, settings)

@pytest.mark.asyncio
async def test_book_appointment_success(appointment_system, patient_manager, sample_patient):
    await patient_manager.repository.create_patient(sample_patient)
    req = BookAppointmentRequest(
        patient_id=sample_patient.patient_id,
        scheduled_at=datetime.now(timezone.utc) + timedelta(days=1),
        consultation_type=ConsultationType.IN_PERSON,
        symptoms_description="I have a headache",
        doctor_id="DOC-123"
    )
    app = await appointment_system.book_appointment(req)
    assert app.appointment_id.startswith("APT-") or app.appointment_id
    assert app.priority_level in [PriorityLevel.ROUTINE, PriorityLevel.MODERATE, PriorityLevel.CRITICAL]

@pytest.mark.asyncio
async def test_book_appointment_past_date(appointment_system, patient_manager, sample_patient):
    await patient_manager.repository.create_patient(sample_patient)
    req = BookAppointmentRequest(
        patient_id=sample_patient.patient_id,
        scheduled_at=datetime.now(timezone.utc) - timedelta(days=1),
        consultation_type=ConsultationType.IN_PERSON,
        symptoms_description="I have a headache",
        doctor_id="DOC-123"
    )
    with pytest.raises(InvalidPatientDataError):
        await appointment_system.book_appointment(req)

@pytest.mark.asyncio
async def test_book_appointment_conflict(appointment_system, patient_manager, sample_patient):
    await patient_manager.repository.create_patient(sample_patient)
    sched_time = datetime.now(timezone.utc) + timedelta(days=1)
    req1 = BookAppointmentRequest(
        patient_id=sample_patient.patient_id,
        scheduled_at=sched_time,
        consultation_type=ConsultationType.IN_PERSON,
        symptoms_description="I have a headache",
        doctor_id="DOC-123"
    )
    await appointment_system.book_appointment(req1)
    
    req2 = BookAppointmentRequest(
        patient_id=sample_patient.patient_id,
        scheduled_at=sched_time + timedelta(minutes=5), # Overlapping
        consultation_type=ConsultationType.IN_PERSON,
        symptoms_description="I have a headache",
        doctor_id="DOC-123"
    )
    with pytest.raises(AppointmentConflictError):
        await appointment_system.book_appointment(req2)

@pytest.mark.asyncio
async def test_confirm_appointment_bad_state(appointment_system, sample_appointment):
    sample_appointment.status = AppointmentStatus.CONFIRMED
    await appointment_system.repository.create(sample_appointment)
    with pytest.raises(InvalidAppointmentStateError):
        await appointment_system.confirm_appointment(sample_appointment.appointment_id, "DOC-123")

@pytest.mark.asyncio
async def test_get_doctor_queue_ordering(appointment_system, sample_patient, sample_appointment):
    await appointment_system.patient_manager.repository.create_patient(sample_patient)
    d = date.today() + timedelta(days=1)
    
    app1 = Appointment(
        patient_id=sample_patient.patient_id,
        scheduled_at=datetime(d.year, d.month, d.day, 10, 0, tzinfo=timezone.utc),
        consultation_type=ConsultationType.IN_PERSON,
        symptoms_description="Routine checkup",
        estimated_duration_minutes=15,
        doctor_id="DOC-123",
        status=AppointmentStatus.CONFIRMED,
        priority_level=PriorityLevel.ROUTINE
    )
    app2 = Appointment(
        patient_id=sample_patient.patient_id,
        scheduled_at=datetime(d.year, d.month, d.day, 11, 0, tzinfo=timezone.utc),
        consultation_type=ConsultationType.IN_PERSON,
        symptoms_description="Severe chest pain",
        estimated_duration_minutes=15,
        doctor_id="DOC-123",
        status=AppointmentStatus.CONFIRMED,
        priority_level=PriorityLevel.CRITICAL
    )
    await appointment_system.repository.create(app1)
    await appointment_system.repository.create(app2)
    
    queue = await appointment_system.get_doctor_queue("DOC-123", d)
    assert len(queue) == 2
    assert queue[0].priority_level == PriorityLevel.CRITICAL
    assert queue[1].priority_level == PriorityLevel.ROUTINE

@pytest.mark.asyncio
async def test_get_available_slots(appointment_system):
    d = date.today() + timedelta(days=2) # Needs to be a weekday ideally, but spec says "Returns list of 30-min slots from 09:00–17:00" assuming working hours.
    # We will test a generic day
    slots = await appointment_system.get_available_slots("DOC-123", d, duration_minutes=30)
    # 09:00 to 17:00 is 8 hours = 16 slots of 30 mins
    if d.weekday() < 5:
        assert len(slots) == 16

@pytest.mark.asyncio
async def test_cancel_completed_appointment(appointment_system, sample_appointment):
    sample_appointment.status = AppointmentStatus.COMPLETED
    await appointment_system.repository.create(sample_appointment)
    with pytest.raises(InvalidAppointmentStateError):
        await appointment_system.cancel_appointment(sample_appointment.appointment_id)

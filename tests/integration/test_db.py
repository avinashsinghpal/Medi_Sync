import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, date, timezone
from medisync.storage.patient_repository import PatientRepository
from medisync.storage.appointment_repository import AppointmentRepository
from medisync.core.types import PatientProfile, PatientStatus, Appointment, AppointmentStatus, ConsultationType, PriorityLevel

@pytest_asyncio.fixture
async def db():
    client = AsyncIOMotorClient("mongodb://localhost:27017/")
    db = client["medisync_test_db"]
    # cleanup before test
    await db.patients.delete_many({})
    await db.medical_records.delete_many({})
    await db.consultation_logs.delete_many({})
    await db.appointments.delete_many({})
    yield db
    # cleanup after test
    await db.patients.delete_many({})
    await db.medical_records.delete_many({})
    await db.consultation_logs.delete_many({})
    await db.appointments.delete_many({})
    client.close()

@pytest.mark.asyncio
async def test_patient_repository(db):
    repo = PatientRepository(db)
    await repo.setup_indexes()

    # Test Create
    p = PatientProfile(
        patient_id="P-DB-001",
        full_name="Integration Test",
        date_of_birth=date(1990, 1, 1),
        gender="male",
        contact_email="testdb@example.com",
        contact_phone="1234567890",
        status=PatientStatus.ACTIVE,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        metadata={}
    )
    await repo.create_patient(p)

    # Test Get
    fetched = await repo.get_patient_by_id("P-DB-001")
    assert fetched is not None
    assert fetched.full_name == "Integration Test"
    assert fetched.date_of_birth == date(1990, 1, 1)

    # Test Update
    fetched.full_name = "Updated Name"
    await repo.update_patient(fetched)
    fetched_updated = await repo.get_patient_by_email("testdb@example.com")
    assert fetched_updated.full_name == "Updated Name"

@pytest.mark.asyncio
async def test_appointment_repository(db):
    repo = AppointmentRepository(db)
    await repo.setup_indexes()

    # Test Create
    a = Appointment(
        appointment_id="APT-DB-001",
        patient_id="P-DB-001",
        scheduled_at=datetime.now(timezone.utc),
        consultation_type=ConsultationType.IN_PERSON,
        status=AppointmentStatus.PENDING,
        symptoms_description="test symptoms",
        priority_level=PriorityLevel.ROUTINE,
        estimated_duration_minutes=15,
        created_at=datetime.now(timezone.utc)
    )
    await repo.create(a)

    # Test Get
    fetched = await repo.get_by_id("APT-DB-001")
    assert fetched is not None
    assert fetched.patient_id == "P-DB-001"

    # Test Update
    fetched.status = AppointmentStatus.CONFIRMED
    await repo.update(fetched)
    fetched_updated = await repo.get_by_id("APT-DB-001")
    assert fetched_updated.status == AppointmentStatus.CONFIRMED

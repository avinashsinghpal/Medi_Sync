import pytest
from medisync.patient.patient_management import PatientManager, CreatePatientRequest, UpdatePatientRequest, CreateMedicalRecordRequest
from medisync.core.errors import DuplicatePatientError, InvalidPatientDataError, PatientNotFoundError
from medisync.core.types import PatientProfile, PatientStatus

@pytest.fixture
def patient_manager(mock_patient_repo, settings):
    return PatientManager(mock_patient_repo, settings)

@pytest.mark.asyncio
async def test_create_patient_success(patient_manager):
    req = CreatePatientRequest(
        full_name="John Doe",
        date_of_birth="1990-01-01",
        gender="male",
        contact_email="john@example.com",
        contact_phone="+1234567890"
    )
    profile = await patient_manager.create_patient(req)
    assert profile.patient_id.startswith("P-")
    assert profile.full_name == "John Doe"
    assert profile.status == PatientStatus.ACTIVE

@pytest.mark.asyncio
async def test_create_patient_duplicate_email(patient_manager):
    req = CreatePatientRequest(
        full_name="John Doe",
        date_of_birth="1990-01-01",
        gender="male",
        contact_email="john@example.com",
        contact_phone="+1234567890"
    )
    await patient_manager.create_patient(req)
    with pytest.raises(DuplicatePatientError):
        await patient_manager.create_patient(req)

@pytest.mark.asyncio
async def test_create_patient_empty_name(patient_manager):
    req = CreatePatientRequest(
        full_name="",
        date_of_birth="1990-01-01",
        gender="male",
        contact_email="john2@example.com",
        contact_phone="+1234567890"
    )
    with pytest.raises(InvalidPatientDataError):
        await patient_manager.create_patient(req)

@pytest.mark.asyncio
async def test_get_patient_not_found(patient_manager):
    with pytest.raises(PatientNotFoundError):
        await patient_manager.get_patient("P-UNKNOWN")

@pytest.mark.asyncio
async def test_update_patient_partial(patient_manager):
    req = CreatePatientRequest(
        full_name="Jane Doe",
        date_of_birth="1995-01-01",
        gender="female",
        contact_email="jane@example.com",
        contact_phone="+1111111111"
    )
    profile = await patient_manager.create_patient(req)
    
    update_req = UpdatePatientRequest(contact_phone="+2222222222")
    updated_profile = await patient_manager.update_patient(profile.patient_id, update_req)
    
    assert updated_profile.contact_phone == "+2222222222"
    assert updated_profile.full_name == "Jane Doe"

@pytest.mark.asyncio
async def test_get_patient_summary(patient_manager, sample_patient):
    # Need to put sample_patient in repo first
    await patient_manager.repository.create_patient(sample_patient)
    summary = await patient_manager.get_patient_summary(sample_patient.patient_id)
    assert "patient_id" in summary
    assert "full_name" in summary
    assert "age" in summary
    assert "blood_group" in summary
    assert "status" in summary
    assert "total_records" in summary
    assert "recent_diagnoses" in summary
    assert "current_medications" in summary
    assert "last_visit" in summary
    assert "priority_level" in summary

@pytest.mark.asyncio
async def test_search_patients_empty_result(patient_manager):
    results = await patient_manager.search_patients("zzz")
    assert results == []

@pytest.mark.asyncio
async def test_add_medical_record_bad_type(patient_manager, sample_patient):
    await patient_manager.repository.create_patient(sample_patient)
    req = CreateMedicalRecordRequest(
        record_type="xray", # Invalid type
        title="Chest Xray",
        content="Clear"
    )
    with pytest.raises(InvalidPatientDataError):
        await patient_manager.add_medical_record(sample_patient.patient_id, req)

import uuid
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional, List

from medisync.core.types import PatientProfile, MedicalRecord, ConsultationLog, PatientStatus, generate_patient_id, generate_uuid, utc_now
from medisync.core.errors import PatientNotFoundError, DuplicatePatientError, InvalidPatientDataError
from medisync.core.config import Settings
from medisync.storage.patient_repository import PatientRepository

@dataclass
class CreatePatientRequest:
    full_name: str
    date_of_birth: str
    gender: str
    contact_email: str
    contact_phone: str
    blood_group: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None

@dataclass
class UpdatePatientRequest:
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    blood_group: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    status: Optional[PatientStatus] = None

@dataclass
class CreateMedicalRecordRequest:
    record_type: str
    title: str
    content: str
    consultation_id: Optional[str] = None
    doctor_id: Optional[str] = None
    hospital_id: Optional[str] = None
    tags: Optional[List[str]] = None
    attachments: Optional[List[str]] = None

class PatientManager:
    def __init__(self, repository: PatientRepository, settings: Settings):
        self.repository = repository
        self.settings = settings

    async def create_patient(self, data: CreatePatientRequest, patient_id_override: Optional[str] = None) -> PatientProfile:
        if not data.full_name or not data.full_name.strip():
            raise InvalidPatientDataError("full_name MUST NOT be empty")
        valid_genders = {"male", "female", "other", "prefer_not_to_say"}
        if data.gender not in valid_genders:
            raise InvalidPatientDataError(f"gender MUST be one of {valid_genders}")
        
        existing = await self.repository.get_patient_by_email(data.contact_email)
        if existing:
            raise DuplicatePatientError(f"Patient with email {data.contact_email} already exists")

        from datetime import date
        try:
            dob = datetime.strptime(data.date_of_birth, "%Y-%m-%d").date()
        except ValueError:
            raise InvalidPatientDataError("date_of_birth must be YYYY-MM-DD")

        patient_id = patient_id_override or generate_patient_id()
        now = utc_now()
        
        profile = PatientProfile(
            patient_id=patient_id,
            full_name=data.full_name,
            date_of_birth=dob,
            gender=data.gender,
            blood_group=data.blood_group,
            contact_email=data.contact_email,
            contact_phone=data.contact_phone,
            address=data.address,
            emergency_contact=data.emergency_contact,
            status=PatientStatus.ACTIVE,
            created_at=now,
            updated_at=now,
            metadata={}
        )
        await self.repository.create_patient(profile)
        return profile

    async def get_patient(self, patient_id: str) -> PatientProfile:
        if not patient_id.startswith("P-"):
            raise PatientNotFoundError(f"Invalid patient_id format: {patient_id}")
        profile = await self.repository.get_patient_by_id(patient_id)
        if not profile:
            raise PatientNotFoundError(f"Patient {patient_id} not found")
        # In background: increment access counter, not blocking here
        return profile

    async def get_patient_by_email(self, email: str) -> PatientProfile:
        profile = await self.repository.get_patient_by_email(email)
        if not profile:
            raise PatientNotFoundError(f"Patient with email {email} not found")
        return profile

    async def update_patient(self, patient_id: str, updates: UpdatePatientRequest) -> PatientProfile:
        profile = await self.get_patient(patient_id)
        
        has_changes = False
        import dataclasses
        for field in dataclasses.fields(updates):
            val = getattr(updates, field.name)
            if val is not None:
                if field.name == "date_of_birth":
                    try:
                        val = datetime.strptime(val, "%Y-%m-%d").date()
                    except ValueError:
                        raise InvalidPatientDataError("date_of_birth must be YYYY-MM-DD")
                setattr(profile, field.name, val)
                has_changes = True
                
        if has_changes:
            profile.updated_at = utc_now()
            # Revalidate
            if not profile.full_name or not profile.full_name.strip():
                raise InvalidPatientDataError("full_name MUST NOT be empty")
            valid_genders = {"male", "female", "other", "prefer_not_to_say"}
            if profile.gender not in valid_genders:
                raise InvalidPatientDataError(f"gender MUST be one of {valid_genders}")
                
            await self.repository.update_patient(profile)
            
        return profile

    async def deactivate_patient(self, patient_id: str) -> PatientProfile:
        profile = await self.get_patient(patient_id)
        profile.status = PatientStatus.INACTIVE
        profile.updated_at = utc_now()
        await self.repository.update_patient(profile)
        return profile

    async def get_patient_history(self, patient_id: str, limit: int = 20, offset: int = 0) -> List[MedicalRecord]:
        await self.get_patient(patient_id)
        if limit == 0:
            return []
        return await self.repository.get_medical_records(patient_id, limit, offset)

    async def add_medical_record(self, patient_id: str, record: CreateMedicalRecordRequest) -> MedicalRecord:
        await self.get_patient(patient_id)
        
        valid_record_types = {"diagnosis", "prescription", "lab_result", "imaging", "note"}
        if record.record_type not in valid_record_types:
            raise InvalidPatientDataError(f"unknown record_type. Must be one of {valid_record_types}")
        if not record.content or not record.content.strip():
            raise InvalidPatientDataError("content MUST NOT be empty")

        new_record = MedicalRecord(
            record_id=generate_uuid(),
            patient_id=patient_id,
            consultation_id=record.consultation_id,
            record_type=record.record_type,
            title=record.title,
            content=record.content,
            doctor_id=record.doctor_id,
            hospital_id=record.hospital_id,
            recorded_at=utc_now(),
            tags=record.tags or [],
            attachments=record.attachments or []
        )
        await self.repository.create_medical_record(new_record)
        return new_record

    async def get_consultation_logs(self, patient_id: str, limit: int = 10) -> List[ConsultationLog]:
        await self.get_patient(patient_id)
        return await self.repository.get_consultation_logs(patient_id, limit)

    async def search_patients(self, query: str, limit: int = 20) -> List[PatientProfile]:
        if not query or len(query) < 2:
            return await self.repository.list_patients(limit)
        return await self.repository.search_patients(query, limit)

    async def list_patients(self, limit: int = 50, offset: int = 0) -> List[PatientProfile]:
        return await self.repository.list_patients(limit, offset)

    async def get_patient_summary(self, patient_id: str) -> dict:
        profile = await self.get_patient(patient_id)
        records = await self.repository.get_medical_records(patient_id, limit=100)
        logs = await self.repository.get_consultation_logs(patient_id, limit=1)
        
        recent_diagnoses = [r.title for r in records if r.record_type == "diagnosis"][:3]
        prescriptions = [r for r in records if r.record_type == "prescription"]
        current_medications = []
        if prescriptions:
            # simple mock extraction from latest prescription
            current_medications = [prescriptions[0].title] 
            
        last_visit = logs[0].started_at.isoformat() if logs else "Never"
        priority_level = logs[0].priority_level.value if logs else "routine"

        return {
            "patient_id": profile.patient_id,
            "full_name": profile.full_name,
            "age": profile.age,
            "blood_group": profile.blood_group or "Unknown",
            "status": profile.status.value,
            "total_records": len(records),
            "recent_diagnoses": recent_diagnoses,
            "current_medications": current_medications,
            "last_visit": last_visit,
            "priority_level": priority_level
        }

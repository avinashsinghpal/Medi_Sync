from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import Optional, List

class CreatePatientRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=200)
    date_of_birth: date
    gender: str = Field(..., pattern="^(male|female|other|prefer_not_to_say)$")
    contact_email: EmailStr
    contact_phone: str = Field(..., min_length=7)
    blood_group: Optional[str] = None
    address: Optional[str] = None

class PatientResponse(BaseModel):
    patient_id: str
    full_name: str
    date_of_birth: date
    gender: str
    contact_email: str
    contact_phone: str
    blood_group: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    metadata: dict = {}
    age: int

class MedicalRecordResponse(BaseModel):
    record_id: str
    patient_id: str
    record_type: str
    title: str
    content: str
    consultation_id: Optional[str] = None
    doctor_id: Optional[str] = None
    hospital_id: Optional[str] = None
    recorded_at: datetime
    tags: List[str] = []
    attachments: List[str] = []

class CreateMedicalRecordRequest(BaseModel):
    record_type: str
    title: str
    content: str
    consultation_id: Optional[str] = None
    doctor_id: Optional[str] = None
    hospital_id: Optional[str] = None
    tags: List[str] = []
    attachments: List[str] = []

class MedicalHistoryResponse(BaseModel):
    patient_id: str
    records: List[MedicalRecordResponse]

class PatientListResponse(BaseModel):
    patients: List[PatientResponse]
    total: int

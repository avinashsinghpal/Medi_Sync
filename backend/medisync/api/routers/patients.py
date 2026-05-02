from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from medisync.api.schemas.patients import (
    CreatePatientRequest as ApiCreatePatientRequest,
    PatientResponse,
    MedicalHistoryResponse,
    PatientListResponse,
    CreateMedicalRecordRequest as ApiCreateMedicalRecordRequest,
    MedicalRecordResponse,
)
from medisync.api.dependencies import get_patient_manager
from medisync.core.security import require_role, get_current_user, TokenData, UserRole, sanitize_patient_data
from medisync.patient.patient_management import PatientManager, CreatePatientRequest, CreateMedicalRecordRequest

router = APIRouter(prefix="/api/patients", tags=["patients"])

@router.get("", response_model=PatientListResponse)
async def list_patients(
    limit: int = 50,
    offset: int = 0,
    manager: PatientManager = Depends(get_patient_manager),
    user: TokenData = Depends(require_role(UserRole.DOCTOR, UserRole.ADMIN, UserRole.NURSE))
):
    profiles = await manager.list_patients(limit, offset)
    results = []
    for profile in profiles:
        sanitized = sanitize_patient_data(profile.__dict__, user.role)
        sanitized["age"] = profile.age
        sanitized["status"] = profile.status.value
        results.append(sanitized)
    return {"patients": results, "total": len(results)}

@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    request: ApiCreatePatientRequest,
    manager: PatientManager = Depends(get_patient_manager),
    user: TokenData = Depends(require_role(UserRole.DOCTOR, UserRole.ADMIN))
):
    req_data = CreatePatientRequest(
        full_name=request.full_name,
        date_of_birth=request.date_of_birth.isoformat(),
        gender=request.gender,
        contact_email=request.contact_email,
        contact_phone=request.contact_phone,
        blood_group=request.blood_group,
        address=request.address,
        emergency_contact=None # Missing from Api schema but needed for dataclass
    )
    profile = await manager.create_patient(req_data)
    
    # We must sanitize before returning, but since it's create_patient we know it's full data
    # and DOCTOR/ADMIN can see it, but we follow spec to always sanitize
    sanitized = sanitize_patient_data(profile.__dict__, user.role)
    sanitized["age"] = profile.age
    sanitized["status"] = profile.status.value
    return sanitized

@router.get("/search", response_model=PatientListResponse)
async def search_patients(
    q: str, 
    limit: int = 20,
    manager: PatientManager = Depends(get_patient_manager),
    user: TokenData = Depends(require_role(UserRole.DOCTOR, UserRole.ADMIN, UserRole.NURSE))
):
    profiles = await manager.search_patients(q, limit)
    
    results = []
    for profile in profiles:
        sanitized = sanitize_patient_data(profile.__dict__, user.role)
        sanitized["age"] = profile.age
        sanitized["status"] = profile.status.value
        results.append(sanitized)
        
    return {"patients": results, "total": len(results)}

@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    manager: PatientManager = Depends(get_patient_manager),
    user: TokenData = Depends(get_current_user)
):
    # PATIENT (own only), DOCTOR, ADMIN, NURSE
    if user.role == UserRole.PATIENT:
        if patient_id != user.user_id:
            raise HTTPException(status_code=403, detail="Can only access own data")

    profile = await manager.get_patient(patient_id)
    sanitized = sanitize_patient_data(profile.__dict__, user.role)
    sanitized["age"] = profile.age
    sanitized["status"] = profile.status.value
    return sanitized

@router.patch("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: str,
    request: ApiCreatePatientRequest, # Reusing for simplicity or create a partial schema
    manager: PatientManager = Depends(get_patient_manager),
    user: TokenData = Depends(get_current_user)
):
    if user.role == UserRole.PATIENT and patient_id != user.user_id:
        raise HTTPException(status_code=403, detail="Can only update own data")
    
    from medisync.patient.patient_management import UpdatePatientRequest
    updates = UpdatePatientRequest(
        full_name=request.full_name,
        date_of_birth=request.date_of_birth.isoformat(),
        gender=request.gender,
        contact_email=request.contact_email,
        contact_phone=request.contact_phone,
        blood_group=request.blood_group,
        address=request.address
    )
    profile = await manager.update_patient(patient_id, updates)
    sanitized = sanitize_patient_data(profile.__dict__, user.role)
    sanitized["age"] = profile.age
    sanitized["status"] = profile.status.value
    return sanitized

@router.get("/{patient_id}/history", response_model=MedicalHistoryResponse)
async def get_medical_history(
    patient_id: str, 
    limit: int = 20, 
    offset: int = 0,
    manager: PatientManager = Depends(get_patient_manager),
    user: TokenData = Depends(require_role(UserRole.DOCTOR, UserRole.ADMIN, UserRole.NURSE))
):
    records = await manager.get_patient_history(patient_id, limit, offset)
    # Convert to response
    record_responses = []
    for r in records:
        record_responses.append(MedicalRecordResponse(
            record_id=r.record_id,
            patient_id=r.patient_id,
            record_type=r.record_type,
            title=r.title,
            content=r.content,
            consultation_id=r.consultation_id,
            doctor_id=r.doctor_id,
            hospital_id=r.hospital_id,
            recorded_at=r.recorded_at,
            tags=r.tags,
            attachments=r.attachments
        ))
    return {"patient_id": patient_id, "records": record_responses}

@router.post("/{patient_id}/records", response_model=MedicalRecordResponse, status_code=status.HTTP_201_CREATED)
async def add_medical_record(
    patient_id: str, 
    request: ApiCreateMedicalRecordRequest,
    manager: PatientManager = Depends(get_patient_manager),
    user: TokenData = Depends(require_role(UserRole.DOCTOR, UserRole.ADMIN))
):
    req_data = CreateMedicalRecordRequest(
        record_type=request.record_type,
        title=request.title,
        content=request.content,
        consultation_id=request.consultation_id,
        doctor_id=request.doctor_id,
        hospital_id=request.hospital_id,
        tags=request.tags,
        attachments=request.attachments
    )
    r = await manager.add_medical_record(patient_id, req_data)
    return MedicalRecordResponse(
        record_id=r.record_id,
        patient_id=r.patient_id,
        record_type=r.record_type,
        title=r.title,
        content=r.content,
        consultation_id=r.consultation_id,
        doctor_id=r.doctor_id,
        hospital_id=r.hospital_id,
        recorded_at=r.recorded_at,
        tags=r.tags,
        attachments=r.attachments
    )

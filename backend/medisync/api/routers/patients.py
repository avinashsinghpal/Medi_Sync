from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from medisync.api.schemas.patients import (
    CreatePatientRequest,
    PatientResponse,
    MedicalHistoryResponse,
    PatientListResponse,
    CreateMedicalRecordRequest,
    MedicalRecordResponse,
)

router = APIRouter(prefix="/api/patients", tags=["patients"])

@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(request: CreatePatientRequest):
    raise HTTPException(status_code=501, detail="Not implemented")

@router.get("/search", response_model=PatientListResponse)
async def search_patients(q: str, limit: int = 20):
    raise HTTPException(status_code=501, detail="Not implemented")

@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: str):
    raise HTTPException(status_code=501, detail="Not implemented")

@router.get("/{patient_id}/history", response_model=MedicalHistoryResponse)
async def get_medical_history(patient_id: str, limit: int = 20, offset: int = 0):
    raise HTTPException(status_code=501, detail="Not implemented")

@router.post("/{patient_id}/records", response_model=MedicalRecordResponse, status_code=status.HTTP_201_CREATED)
async def add_medical_record(patient_id: str, request: CreateMedicalRecordRequest):
    raise HTTPException(status_code=501, detail="Not implemented")

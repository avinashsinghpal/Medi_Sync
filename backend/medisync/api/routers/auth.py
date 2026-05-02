from datetime import date

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field

from medisync.core.security import (
    UserRole,
    create_access_token,
    hash_password,
    verify_password,
)
from medisync.patient.patient_management import CreatePatientRequest

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterPatientRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=6)
    date_of_birth: date = date(1990, 1, 1)
    gender: str = "other"
    contact_phone: str = "+91-0000000000"


async def _ensure_default_users(req: Request) -> None:
    """
    Bootstrap minimal real users/doctors in an empty DB.
    """
    users = req.app.state.db["users"]
    doctors = req.app.state.db["doctors"]
    if await users.count_documents({}) > 0:
        return

    await users.create_index("email", unique=True)
    await users.create_index("user_id", unique=True)
    await doctors.create_index("doctor_id", unique=True)
    await doctors.create_index("email", unique=True)

    doctor_id = "D-DEMO01"
    patient_id = "P-DEMO01"

    await doctors.update_one(
        {"doctor_id": doctor_id},
        {
            "$set": {
                "doctor_id": doctor_id,
                "name": "Dr. Demo",
                "email": "doctor@medisync.com",
                "specialization": "General Medicine",
                "experience_years": 8,
            }
        },
        upsert=True,
    )

    patient_manager = req.app.state.patient_manager
    try:
        await patient_manager.get_patient(patient_id)
    except Exception:
        await patient_manager.create_patient(
            CreatePatientRequest(
                full_name="Patient Demo",
                date_of_birth=date(1990, 1, 1).isoformat(),
                gender="other",
                contact_email="patient@medisync.com",
                contact_phone="+91-0000000000",
                blood_group="O+",
                address="Demo Address",
                emergency_contact=None,
            ),
            patient_id_override=patient_id,
        )

    await users.insert_many(
        [
            {
                "user_id": doctor_id,
                "email": "doctor@medisync.com",
                "password_hash": hash_password("doctor123"),
                "role": UserRole.DOCTOR.value,
                "name": "Dr. Demo",
            },
            {
                "user_id": patient_id,
                "email": "patient@medisync.com",
                "password_hash": hash_password("patient123"),
                "role": UserRole.PATIENT.value,
                "name": "Patient Demo",
            },
        ]
    )


@router.post("/login")
async def login(request: LoginRequest, req: Request):
    await _ensure_default_users(req)
    users = req.app.state.db["users"]
    user = await users.find_one({"email": request.email.lower()})
    if not user or not verify_password(request.password, user.get("password_hash", "")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    role = UserRole(user["role"])
    token = create_access_token(user_id=user["user_id"], role=role, email=user["email"])
    return {
        "token": token,
        "user": {
            "id": user["user_id"],
            "email": user["email"],
            "role": role.value.upper(),
            "name": user.get("name", "User"),
        },
    }


@router.post("/register/patient")
async def register_patient(request: RegisterPatientRequest, req: Request):
    await _ensure_default_users(req)
    users = req.app.state.db["users"]
    existing_user = await users.find_one({"email": request.email.lower()})
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    patient_manager = req.app.state.patient_manager
    created_patient = await patient_manager.create_patient(
        CreatePatientRequest(
            full_name=request.full_name,
            date_of_birth=request.date_of_birth.isoformat(),
            gender=request.gender,
            contact_email=request.email.lower(),
            contact_phone=request.contact_phone,
            blood_group=None,
            address=None,
            emergency_contact=None,
        )
    )

    await users.insert_one(
        {
            "user_id": created_patient.patient_id,
            "email": request.email.lower(),
            "password_hash": hash_password(request.password),
            "role": UserRole.PATIENT.value,
            "name": request.full_name,
        }
    )

    token = create_access_token(
        user_id=created_patient.patient_id,
        role=UserRole.PATIENT,
        email=request.email.lower(),
    )
    return {
        "token": token,
        "user": {
            "id": created_patient.patient_id,
            "email": request.email.lower(),
            "role": UserRole.PATIENT.value.upper(),
            "name": request.full_name,
        },
    }

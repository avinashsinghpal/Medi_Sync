from datetime import date

from fastapi import APIRouter, Depends, Query, Request

from medisync.core.security import TokenData, UserRole, get_current_user, require_role

router = APIRouter(prefix="/api/doctors", tags=["doctors"])


@router.get("")
async def list_doctors(
    request: Request,
    user: TokenData = Depends(get_current_user),
):
    """
    Return registered doctors for booking and doctor workflows.
    """
    doctors = await request.app.state.db["doctors"].find({}, {"_id": 0}).to_list(length=500)
    return {"doctors": doctors, "total": len(doctors)}


@router.get("/{doctor_id}/appointments")
async def doctor_appointments_with_patient_history(
    doctor_id: str,
    d: date = Query(default_factory=date.today),
    request: Request = None,
    user: TokenData = Depends(require_role(UserRole.DOCTOR, UserRole.ADMIN)),
):
    """
    Return each booked appointment with relevant patient summary/history fields.
    """
    appointment_system = request.app.state.appointment_system
    patient_manager = request.app.state.patient_manager
    appointments = await appointment_system.get_doctor_queue(doctor_id, d)
    results = []
    for app in appointments:
        profile = await patient_manager.get_patient(app.patient_id)
        summary = await patient_manager.get_patient_summary(app.patient_id)
        results.append(
            {
                "appointment_id": app.appointment_id,
                "scheduled_at": app.scheduled_at.isoformat(),
                "status": app.status.value if hasattr(app.status, "value") else str(app.status),
                "priority_level": app.priority_level.value if hasattr(app.priority_level, "value") else str(app.priority_level),
                "consultation_type": app.consultation_type.value if hasattr(app.consultation_type, "value") else str(app.consultation_type),
                "symptoms_description": app.symptoms_description,
                "patient": {
                    "patient_id": profile.patient_id,
                    "full_name": profile.full_name,
                    "age": profile.age,
                    "blood_group": profile.blood_group,
                    "contact_email": profile.contact_email,
                    "status": profile.status.value if hasattr(profile.status, "value") else str(profile.status),
                },
                "history": {
                    "recent_diagnoses": summary.get("recent_diagnoses", []),
                    "current_medications": summary.get("current_medications", []),
                    "last_visit": summary.get("last_visit"),
                    "total_records": summary.get("total_records", 0),
                },
            }
        )
    return {"doctor_id": doctor_id, "date": d.isoformat(), "appointments": results, "total": len(results)}

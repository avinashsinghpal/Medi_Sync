"""Dashboard router — wired to DoctorDashboard service."""
from __future__ import annotations

from datetime import date
from typing import List

from fastapi import APIRouter, Depends, Query, Request

from medisync.api.schemas.dashboard import (
    DoctorQueueResponse,
    DashboardOverviewResponse,
    PatientQueueItemResponse,
    PatientSummaryCardResponse,
)
from medisync.core.security import require_role, TokenData, UserRole
from medisync.dashboard.dashboard import DoctorDashboard, PatientQueueItem

router = APIRouter(prefix="/api", tags=["dashboard"])


async def _get_dashboard(request: Request) -> DoctorDashboard:
    return request.app.state.doctor_dashboard


def _map_queue_item(item: PatientQueueItem) -> PatientQueueItemResponse:
    return PatientQueueItemResponse(
        queue_position=item.queue_position,
        patient_id=item.patient_id,
        patient_name=item.patient_name,
        age=item.age,
        appointment_id=item.appointment_id,
        scheduled_at=item.scheduled_at,
        priority_level=item.priority_level,
        priority_badge_color=item.priority_badge_color,
        symptoms_preview=item.symptoms_preview,
        estimated_duration_minutes=item.estimated_duration_minutes,
        status=item.status,
        risk_flags=item.risk_flags,
    )


@router.get("/doctor/{doctor_id}/queue", response_model=DoctorQueueResponse)
async def get_doctor_queue(
    doctor_id: str,
    d: date = Query(default_factory=date.today),
    request: Request = None,
    user: TokenData = Depends(require_role(UserRole.DOCTOR, UserRole.ADMIN)),
):
    """
    Get the priority-sorted appointment queue for *doctor_id* on date *d*.
    Auth: DOCTOR (own queue), ADMIN.
    """
    dashboard: DoctorDashboard = await _get_dashboard(request)
    queue = await dashboard.get_patient_queue(doctor_id, d)

    return DoctorQueueResponse(
        doctor_id=doctor_id,
        date=d.isoformat(),
        queue=[_map_queue_item(item) for item in queue],
    )


@router.get("/dashboard/overview", response_model=DashboardOverviewResponse)
async def get_dashboard_overview(
    doctor_id: str = Query(...),
    d: date = Query(default_factory=date.today),
    request: Request = None,
    user: TokenData = Depends(require_role(UserRole.DOCTOR, UserRole.ADMIN)),
):
    """
    Full daily overview: counts, queue, recent activity.
    Auth: DOCTOR, ADMIN.
    """
    dashboard: DoctorDashboard = await _get_dashboard(request)
    overview = await dashboard.get_dashboard_overview(doctor_id, d)

    return DashboardOverviewResponse(
        doctor_id=overview.doctor_id,
        date=overview.date,
        total_patients_today=overview.total_patients_today,
        critical_count=overview.critical_count,
        moderate_count=overview.moderate_count,
        routine_count=overview.routine_count,
        completed_consultations=overview.completed_consultations,
        pending_consultations=overview.pending_consultations,
        estimated_remaining_hours=overview.estimated_remaining_hours,
        priority_queue=[_map_queue_item(item) for item in overview.priority_queue],
        recent_activity=overview.recent_activity,
    )


@router.get("/patients/{patient_id}/summary-card", response_model=PatientSummaryCardResponse)
async def get_patient_summary_card(
    patient_id: str,
    request: Request = None,
    user: TokenData = Depends(require_role(UserRole.DOCTOR, UserRole.ADMIN, UserRole.NURSE)),
):
    """
    Rich patient summary card for in-session doctor view.
    Auth: DOCTOR, ADMIN, NURSE.
    """
    dashboard: DoctorDashboard = await _get_dashboard(request)
    card = await dashboard.get_patient_summary_card(patient_id)

    return PatientSummaryCardResponse(
        patient_id=card.patient_id,
        full_name=card.full_name,
        age=card.age,
        blood_group=card.blood_group,
        status=card.status,
        priority_level=card.priority_level,
        risk_indicators=card.risk_indicators,
        recent_diagnoses=card.recent_diagnoses,
        current_medications=card.current_medications,
        last_visit_date=card.last_visit_date,
        total_visits=card.total_visits,
        consultation_history_preview=card.consultation_history_preview,
        quick_actions=card.quick_actions,
    )

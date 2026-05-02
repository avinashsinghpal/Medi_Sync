from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import date
from medisync.api.schemas.dashboard import DoctorQueueResponse, DashboardOverviewResponse

router = APIRouter(prefix="/api", tags=["dashboard"])

@router.get("/doctor/{doctor_id}/queue", response_model=DoctorQueueResponse)
async def get_doctor_queue(doctor_id: str):
    raise HTTPException(status_code=501, detail="Not implemented")

@router.get("/dashboard/overview", response_model=DashboardOverviewResponse)
async def get_dashboard_overview(doctor_id: str, date: date = Query(...)):
    raise HTTPException(status_code=501, detail="Not implemented")

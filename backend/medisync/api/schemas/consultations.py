"""Pydantic schema for consultation processing response."""
from __future__ import annotations

from pydantic import BaseModel
from typing import Optional


class ConsultationResultResponse(BaseModel):
    """Response for POST /api/consultation/process."""
    consultation_id: str
    patient_id: str
    transcript: Optional[str] = None
    consultation_summary: str
    priority_level: str
    structured_output: dict
    prescription_text: Optional[str] = None
    recommended_follow_up: Optional[str] = None

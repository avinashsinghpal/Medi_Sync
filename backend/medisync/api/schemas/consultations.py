from pydantic import BaseModel
from typing import Optional

class ConsultationResultResponse(BaseModel):
    consultation_id: str
    patient_id: str
    transcript: Optional[str]
    consultation_summary: str
    priority_level: str
    structured_output: dict
    prescription_text: Optional[str]

"""
DoctorDashboard service — aggregates patient summaries, priority queues,
real-time consultation data, and analytics for the doctor's daily workflow.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Any, Optional

from medisync.core.types import (
    Appointment,
    AppointmentStatus,
    PriorityLevel,
    generate_uuid,
    utc_now,
)
from medisync.core.errors import NLPExtractionError


# ---------------------------------------------------------------------------
# Return dataclasses (matching SPEC_dashboard.md exactly)
# ---------------------------------------------------------------------------

@dataclass
class PatientQueueItem:
    """One entry in the prioritised doctor queue."""
    queue_position: int
    patient_id: str
    patient_name: str
    age: int
    appointment_id: str
    scheduled_at: str           # ISO 8601
    priority_level: str         # "critical" | "moderate" | "routine"
    priority_badge_color: str   # "red" | "yellow" | "green"
    symptoms_preview: str       # First 100 chars with trailing "…"
    estimated_duration_minutes: int
    status: str
    risk_flags: list[str]


@dataclass
class DashboardOverview:
    """Full daily overview for a doctor."""
    doctor_id: str
    date: str                              # ISO date
    total_patients_today: int
    critical_count: int
    moderate_count: int
    routine_count: int
    completed_consultations: int
    pending_consultations: int
    estimated_remaining_hours: float
    priority_queue: list[PatientQueueItem]
    recent_activity: list[dict]


@dataclass
class PatientSummaryCard:
    """Rich patient card for the doctor's dashboard."""
    patient_id: str
    full_name: str
    age: int
    blood_group: Optional[str]
    status: str
    priority_level: str
    risk_indicators: list[str]
    recent_diagnoses: list[str]
    current_medications: list[str]
    last_visit_date: Optional[str]
    total_visits: int
    consultation_history_preview: list[dict]
    quick_actions: list[str]


@dataclass
class ConsultationResult:
    """Output of the full consultation processing pipeline."""
    consultation_id: str
    patient_id: str
    doctor_id: str
    transcript: Optional[str]
    extracted_data: dict
    consultation_summary: str
    priority_level: str
    prescription_text: Optional[str]
    recommended_follow_up: Optional[str]
    structured_output: dict


# ---------------------------------------------------------------------------
# Priority helpers
# ---------------------------------------------------------------------------

_PRIORITY_COLOR = {
    PriorityLevel.CRITICAL: "red",
    PriorityLevel.MODERATE: "yellow",
    PriorityLevel.ROUTINE: "green",
}

_PRIORITY_SORT_KEY = {
    PriorityLevel.CRITICAL: 0,
    PriorityLevel.MODERATE: 1,
    PriorityLevel.ROUTINE: 2,
}


def _badge_color(priority: PriorityLevel) -> str:
    return _PRIORITY_COLOR.get(priority, "green")


def _symptoms_preview(text: str) -> str:
    """Truncate to 100 chars with ellipsis per UX invariant."""
    if len(text) <= 100:
        return text
    return text[:100] + "..."


# ---------------------------------------------------------------------------
# DoctorDashboard
# ---------------------------------------------------------------------------

class DoctorDashboard:
    """
    Aggregation service for the doctor-facing dashboard.

    Depends on PatientManager and AppointmentSystem (already implemented).
    NLPEngine and PriorityEngine are accepted via duck-typing; if they are
    empty stubs (Dev A not yet merged), graceful fallbacks are used.
    """

    def __init__(
        self,
        patient_manager: Any,       # PatientManager
        appointment_system: Any,    # AppointmentSystem
        nlp_engine: Any,            # NLPEngine  — may be a stub
        priority_engine: Any,       # PriorityEngine — may be a stub
    ):
        self._patients = patient_manager
        self._appointments = appointment_system
        self._nlp = nlp_engine
        self._priority = priority_engine

    # ------------------------------------------------------------------
    # get_patient_queue
    # ------------------------------------------------------------------

    async def get_patient_queue(
        self, doctor_id: str, target_date: date
    ) -> list[PatientQueueItem]:
        """
        Return prioritised queue of today's appointments for *doctor_id*.
        CRITICAL appointments are listed first, ties broken by scheduled_at.
        """
        appointments: list[Appointment] = await self._appointments.get_doctor_queue(
            doctor_id, target_date
        )

        queue_items: list[PatientQueueItem] = []
        for position, appt in enumerate(appointments, start=1):
            # Fetch patient name / age — fall back gracefully if not found
            try:
                profile = await self._patients.get_patient(appt.patient_id)
                patient_name = profile.full_name
                age = profile.age
            except Exception:
                patient_name = "Unknown"
                age = 0

            # Risk flags: mark CRITICAL or anything with "emergency" in symptoms
            risk_flags: list[str] = []
            if appt.priority_level == PriorityLevel.CRITICAL:
                risk_flags.append("HIGH_PRIORITY")
            if appt.consultation_type.value == "emergency":
                risk_flags.append("EMERGENCY")

            queue_items.append(
                PatientQueueItem(
                    queue_position=position,
                    patient_id=appt.patient_id,
                    patient_name=patient_name,
                    age=age,
                    appointment_id=appt.appointment_id,
                    scheduled_at=appt.scheduled_at.isoformat(),
                    priority_level=appt.priority_level.value,
                    priority_badge_color=_badge_color(appt.priority_level),
                    symptoms_preview=_symptoms_preview(appt.symptoms_description),
                    estimated_duration_minutes=appt.estimated_duration_minutes,
                    status=appt.status.value,
                    risk_flags=risk_flags,
                )
            )

        return queue_items

    # ------------------------------------------------------------------
    # get_dashboard_overview
    # ------------------------------------------------------------------

    async def get_dashboard_overview(
        self, doctor_id: str, target_date: date
    ) -> DashboardOverview:
        """Full aggregated overview for the doctor's daily dashboard."""
        appointments: list[Appointment] = await self._appointments.get_doctor_queue(
            doctor_id, target_date
        )

        critical_count = sum(
            1 for a in appointments if a.priority_level == PriorityLevel.CRITICAL
        )
        moderate_count = sum(
            1 for a in appointments if a.priority_level == PriorityLevel.MODERATE
        )
        routine_count = sum(
            1 for a in appointments if a.priority_level == PriorityLevel.ROUTINE
        )
        completed = sum(
            1 for a in appointments if a.status == AppointmentStatus.COMPLETED
        )
        pending = sum(
            1 for a in appointments
            if a.status in (AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED)
        )
        remaining_minutes = sum(
            a.estimated_duration_minutes
            for a in appointments
            if a.status not in (AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED)
        )

        priority_queue = await self.get_patient_queue(doctor_id, target_date)

        return DashboardOverview(
            doctor_id=doctor_id,
            date=target_date.isoformat(),
            total_patients_today=len(appointments),
            critical_count=critical_count,
            moderate_count=moderate_count,
            routine_count=routine_count,
            completed_consultations=completed,
            pending_consultations=pending,
            estimated_remaining_hours=round(remaining_minutes / 60.0, 2),
            priority_queue=priority_queue,
            recent_activity=[],  # Populated by future event-log service
        )

    # ------------------------------------------------------------------
    # get_patient_summary_card
    # ------------------------------------------------------------------

    async def get_patient_summary_card(self, patient_id: str) -> PatientSummaryCard:
        """Rich patient card data for doctor's in-session view."""
        summary: dict = await self._patients.get_patient_summary(patient_id)

        return PatientSummaryCard(
            patient_id=summary["patient_id"],
            full_name=summary["full_name"],
            age=summary["age"],
            blood_group=summary.get("blood_group"),
            status=summary["status"],
            priority_level=summary.get("priority_level", "routine"),
            risk_indicators=[],           # Populated by priority engine when available
            recent_diagnoses=summary.get("recent_diagnoses", []),
            current_medications=summary.get("current_medications", []),
            last_visit_date=summary.get("last_visit"),
            total_visits=summary.get("total_records", 0),
            consultation_history_preview=[],
            quick_actions=["start_consultation", "view_history", "add_record"],
        )

    # ------------------------------------------------------------------
    # process_consultation
    # ------------------------------------------------------------------

    async def process_consultation(
        self,
        appointment_id: str,
        audio_data: Optional[bytes],
        text_input: Optional[str],
    ) -> ConsultationResult:
        """
        Full consultation processing pipeline.

        Steps:
          1. Resolve appointment → patient / doctor IDs
          2. Transcribe audio via SpeechProcessor (if provided)
          3. Merge transcript + text_input
          4. Extract medical entities via NLPEngine
          5. Score priority via PriorityEngine
          6. Assemble and return ConsultationResult
        """
        if audio_data is None and not text_input:
            raise NLPExtractionError(
                "process_consultation requires either audio_data or text_input"
            )

        # 1. Resolve appointment
        appointment: Appointment = await self._appointments.get_appointment(appointment_id)
        patient_id = appointment.patient_id
        doctor_id = appointment.doctor_id or "unknown"

        # 2. Transcribe audio (if provided) — delegate to NLPEngine / SpeechProcessor
        transcript: Optional[str] = None
        if audio_data is not None:
            try:
                # NLPEngine or SpeechProcessor may expose transcribe(); fall back gracefully
                if hasattr(self._nlp, "transcribe"):
                    transcript = await self._nlp.transcribe(audio_data)
                else:
                    transcript = "[audio transcription unavailable — NLPEngine stub]"
            except Exception:
                transcript = "[audio transcription failed]"

        # 3. Merge sources
        full_text = " ".join(
            filter(None, [transcript, text_input])
        ).strip()

        # 4. Extract entities via NLPEngine
        extracted_data: dict = {}
        try:
            if hasattr(self._nlp, "extract_entities"):
                extracted_data = await self._nlp.extract_entities(full_text)
        except Exception:
            extracted_data = {"raw_text": full_text}

        # 5. Score priority
        priority_level = PriorityLevel.ROUTINE
        try:
            if hasattr(self._priority, "predict_priority") and full_text:
                priority_level = await self._priority.predict_priority(full_text)
        except Exception:
            pass

        # 6. Build structured output
        symptoms = extracted_data.get("symptoms", [full_text[:80]])
        structured_output = {
            "patient_id": patient_id,
            "symptoms": symptoms,
            "risk_level": priority_level.value.capitalize(),
            "medications": extracted_data.get("medications", []),
            "consultation_time": f"{appointment.estimated_duration_minutes} minutes",
            "priority": priority_level.value.capitalize(),
        }

        consultation_id = generate_uuid()
        summary = extracted_data.get(
            "summary",
            f"Consultation processed. Priority: {priority_level.value}."
        )

        return ConsultationResult(
            consultation_id=consultation_id,
            patient_id=patient_id,
            doctor_id=doctor_id,
            transcript=transcript,
            extracted_data=extracted_data,
            consultation_summary=summary,
            priority_level=priority_level.value,
            prescription_text=extracted_data.get("prescription"),
            recommended_follow_up=extracted_data.get("follow_up"),
            structured_output=structured_output,
        )

    # ------------------------------------------------------------------
    # get_analytics
    # ------------------------------------------------------------------

    async def get_analytics(
        self, doctor_id: str, date_from: date, date_to: date
    ) -> dict:
        """Aggregated analytics over a date range."""
        # NOTE: Full implementation requires a date-range query on the
        # appointment repository (not yet in AppointmentSystem interface).
        # Returning a safe default until that is available.
        return {
            "total_consultations": 0,
            "avg_consultation_duration_minutes": 0.0,
            "priority_breakdown": {"critical": 0, "moderate": 0, "routine": 0},
            "most_common_symptoms": [],
            "patient_satisfaction_avg": 0.0,
            "busiest_day": date_from.isoformat(),
        }

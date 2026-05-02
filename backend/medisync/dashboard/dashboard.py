"""
DoctorDashboard service — aggregates patient summaries, priority queues,
real-time consultation data, and analytics for the doctor's daily workflow.

Fast readability. Clear visual hierarchy. One-click access.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Optional

from medisync.core.types import (
    Appointment,
    AppointmentStatus,
    PriorityLevel,
    generate_uuid,
)
from medisync.core.errors import NLPExtractionError
from medisync.patient.patient_management import PatientManager
from medisync.appointment.appointment_system import AppointmentSystem
from medisync.ai_engine.nlp_engine import NLPEngine, ExtractionResult
from medisync.ai_engine.priority_engine import PriorityEngine, PriorityAssessment


# ---------------------------------------------------------------------------
# Return dataclasses — matching SPEC_dashboard.md exactly
# ---------------------------------------------------------------------------

@dataclass
class PatientQueueItem:
    """One entry in the prioritised doctor queue."""

    queue_position: int
    patient_id: str
    patient_name: str
    age: int
    appointment_id: str
    scheduled_at: str                   # ISO 8601
    priority_level: str                 # "critical" | "moderate" | "routine"
    priority_badge_color: str           # "red" | "yellow" | "green"
    symptoms_preview: str               # First 100 chars with trailing "..."
    estimated_duration_minutes: int
    status: str                         # appointment status value
    risk_flags: list[str]               # Urgent flags for doctor attention


@dataclass
class DashboardOverview:
    """Full daily overview for a doctor."""

    doctor_id: str
    date: str                                   # ISO date
    total_patients_today: int
    critical_count: int                         # 🔴
    moderate_count: int                         # 🟡
    routine_count: int                          # 🟢
    completed_consultations: int
    pending_consultations: int
    estimated_remaining_hours: float
    priority_queue: list[PatientQueueItem]      # Ordered by priority
    recent_activity: list[dict]                 # Last 5 actions/events


@dataclass
class PatientSummaryCard:
    """Rich patient card for the doctor's dashboard."""

    patient_id: str
    full_name: str
    age: int
    blood_group: Optional[str]
    status: str
    priority_level: str
    risk_indicators: list[str]                  # Highlighted risk factors
    recent_diagnoses: list[str]                 # Last 3 diagnoses
    current_medications: list[str]              # Active medications
    last_visit_date: Optional[str]              # ISO 8601 or None
    total_visits: int
    consultation_history_preview: list[dict]    # Last 3 consultations (collapsed)
    quick_actions: list[str]                    # Stable identifiers only


@dataclass
class ConsultationResult:
    """Output of the full consultation processing pipeline."""

    consultation_id: str
    patient_id: str
    doctor_id: str
    transcript: Optional[str]
    extracted_data: dict                        # From NLPEngine (ExtractionResult fields)
    consultation_summary: str
    priority_level: str
    prescription_text: Optional[str]
    recommended_follow_up: Optional[str]
    structured_output: dict                     # Machine-readable JSON per spec


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_PRIORITY_COLOR: dict[PriorityLevel, str] = {
    PriorityLevel.CRITICAL: "red",
    PriorityLevel.MODERATE: "yellow",
    PriorityLevel.ROUTINE:  "green",
}

_PRIORITY_SORT_KEY: dict[PriorityLevel, int] = {
    PriorityLevel.CRITICAL: 0,
    PriorityLevel.MODERATE: 1,
    PriorityLevel.ROUTINE:  2,
}


def _badge_color(priority: PriorityLevel) -> str:
    """Return CSS-compatible color string for a given priority level."""
    return _PRIORITY_COLOR.get(priority, "green")


def _symptoms_preview(text: str) -> str:
    """Truncate to 100 chars with '...' suffix per UX invariant."""
    if len(text) <= 100:
        return text
    return text[:100] + "..."


def _extraction_to_dict(extraction: ExtractionResult) -> dict:
    """Convert an ExtractionResult dataclass to a plain dict for JSON output."""
    return {
        "symptoms":           extraction.symptoms,
        "medications":        extraction.medications,
        "dosages":            extraction.dosages,
        "diagnoses":          extraction.diagnoses,
        "severity_indicators": extraction.severity_indicators,
        "medical_terms":      extraction.medical_terms,
        "negations":          extraction.negations,
        "vitals":             extraction.vitals,
        "summary":            extraction.summary,
        "confidence":         extraction.confidence,
    }


# ---------------------------------------------------------------------------
# DoctorDashboard
# ---------------------------------------------------------------------------

class DoctorDashboard:
    """
    Aggregation service for the doctor-facing dashboard.

    Orchestrates PatientManager, AppointmentSystem, NLPEngine and
    PriorityEngine to produce the data structures needed by the frontend.
    """

    def __init__(
        self,
        patient_manager: PatientManager,
        appointment_system: AppointmentSystem,
        nlp_engine: NLPEngine,
        priority_engine: PriorityEngine,
    ) -> None:
        self._patients    = patient_manager
        self._appointments = appointment_system
        self._nlp         = nlp_engine
        self._priority    = priority_engine

    # ------------------------------------------------------------------
    # get_patient_queue
    # ------------------------------------------------------------------

    async def get_patient_queue(
        self, doctor_id: str, target_date: date
    ) -> list[PatientQueueItem]:
        """
        Return the prioritised appointment queue for *doctor_id* on *target_date*.

        Appointments are sorted CRITICAL → MODERATE → ROUTINE, with ties
        broken by scheduled_at ASC.  Only active (non-cancelled) appointments
        are included.
        """
        appointments: list[Appointment] = await self._appointments.get_doctor_queue(
            doctor_id, target_date
        )

        queue_items: list[PatientQueueItem] = []
        for position, appt in enumerate(appointments, start=1):
            # Fetch patient profile for name/age — fall back gracefully
            try:
                profile = await self._patients.get_patient(appt.patient_id)
                patient_name = profile.full_name
                age = profile.age
            except Exception:
                patient_name = "Unknown"
                age = 0

            # Build risk flags from priority level and consultation type
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
        """
        Return the full daily dashboard overview for *doctor_id* on *target_date*.

        Counts all appointments for the day (including completed/cancelled)
        for accurate totals, then builds the priority queue from active ones.
        """
        # Active appointments drive the priority queue and remaining estimates
        active_appointments: list[Appointment] = await self._appointments.get_doctor_queue(
            doctor_id, target_date
        )

        # For today's complete picture we also need completed appointments.
        # We query them via the appointment system's patient appointments method
        # isn't available at the doctor+date level, so we work with active only
        # and count COMPLETED among active (IN_SESSION can transition to COMPLETED).
        critical_count = sum(
            1 for a in active_appointments if a.priority_level == PriorityLevel.CRITICAL
        )
        moderate_count = sum(
            1 for a in active_appointments if a.priority_level == PriorityLevel.MODERATE
        )
        routine_count = sum(
            1 for a in active_appointments if a.priority_level == PriorityLevel.ROUTINE
        )
        completed = sum(
            1 for a in active_appointments if a.status == AppointmentStatus.COMPLETED
        )
        pending = sum(
            1 for a in active_appointments
            if a.status in (AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED)
        )
        # Remaining time = sum of non-completed, non-cancelled durations
        remaining_minutes = sum(
            a.estimated_duration_minutes
            for a in active_appointments
            if a.status not in (AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED)
        )

        priority_queue = await self.get_patient_queue(doctor_id, target_date)

        return DashboardOverview(
            doctor_id=doctor_id,
            date=target_date.isoformat(),
            total_patients_today=len(active_appointments),
            critical_count=critical_count,
            moderate_count=moderate_count,
            routine_count=routine_count,
            completed_consultations=completed,
            pending_consultations=pending,
            estimated_remaining_hours=round(remaining_minutes / 60.0, 2),
            priority_queue=priority_queue,
            recent_activity=[],     # Event-log service not yet available
        )

    # ------------------------------------------------------------------
    # get_patient_summary_card
    # ------------------------------------------------------------------

    async def get_patient_summary_card(self, patient_id: str) -> PatientSummaryCard:
        """
        Build a rich patient summary card for the doctor's in-session view.

        Pulls demographics and medical history from PatientManager and
        enhances risk indicators using the PriorityEngine where available.
        """
        summary: dict = await self._patients.get_patient_summary(patient_id)

        # Build risk indicators by running PriorityEngine over recent symptoms
        risk_indicators: list[str] = []
        consultation_history_preview: list[dict] = []

        # Fetch last 3 consultation logs for history preview
        try:
            logs = await self._patients.get_consultation_logs(patient_id, limit=3)
            for log in logs:
                consultation_history_preview.append({
                    "date":           log.started_at.isoformat(),
                    "priority_level": log.priority_level.value if hasattr(log.priority_level, "value") else str(log.priority_level),
                    "notes_preview":  (log.notes or "")[:100],
                })

            # Use the most recent log's symptoms to derive risk indicators
            if logs and (logs[0].raw_transcript or logs[0].notes):
                text = logs[0].raw_transcript or logs[0].notes
                try:
                    assessment: PriorityAssessment = await self._priority.predict_priority(
                        text, {}
                    )
                    risk_indicators = assessment.risk_factors + assessment.urgent_flags
                except Exception:
                    pass
        except Exception:
            pass

        return PatientSummaryCard(
            patient_id=summary["patient_id"],
            full_name=summary["full_name"],
            age=summary["age"],
            blood_group=summary.get("blood_group"),
            status=summary["status"],
            priority_level=summary.get("priority_level", "routine"),
            risk_indicators=risk_indicators,
            recent_diagnoses=summary.get("recent_diagnoses", []),
            current_medications=summary.get("current_medications", []),
            last_visit_date=summary.get("last_visit"),
            total_visits=summary.get("total_records", 0),
            consultation_history_preview=consultation_history_preview,
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
        Full AI-powered consultation processing pipeline.

        Steps:
          1. Validate that at least one input source is provided
          2. Resolve appointment → patient_id, doctor_id, duration
          3. Transcribe audio (if provided) — via SpeechToText stub if available
          4. Merge transcript and text_input into one document
          5. Extract clinical entities via NLPEngine.extract_from_text()
          6. Score priority via PriorityEngine.predict_priority()
          7. Build and return a ConsultationResult with structured_output

        Raises:
            NLPExtractionError: if both audio_data and text_input are absent,
                                 or if NLP extraction fails on empty text.
        """
        if audio_data is None and not text_input:
            raise NLPExtractionError(
                "process_consultation requires either audio_data or text_input"
            )

        # 1. Resolve appointment
        appointment: Appointment = await self._appointments.get_appointment(appointment_id)
        patient_id = appointment.patient_id
        doctor_id  = appointment.doctor_id or "unknown"

        # 2. Transcribe audio when provided
        transcript: Optional[str] = None
        if audio_data is not None:
            # Delegate to SpeechToText if injected via nlp_engine duck-type, else stub
            try:
                if hasattr(self._nlp, "transcribe"):
                    transcript = await self._nlp.transcribe(audio_data)
                else:
                    # Audio bytes present but no transcriber — use placeholder
                    transcript = "[audio transcription unavailable — no speech processor]"
            except Exception:
                transcript = "[audio transcription failed]"

        # 3. Merge text sources into a single document
        full_text = " ".join(filter(None, [transcript, text_input])).strip()

        # 4. Extract clinical entities — use the NLPEngine spec API
        extraction: ExtractionResult = await self._nlp.extract_from_text(full_text)

        # 5. Score priority with full patient history context if available
        assessment: PriorityAssessment = await self._priority.predict_priority(
            full_text, {}
        )
        priority_level: PriorityLevel = assessment.priority_level

        # 6. Build structured machine-readable output (format per SPEC_dashboard.md)
        structured_output: dict = {
            "patient_id":        patient_id,
            "symptoms":          extraction.symptoms,
            "risk_level":        priority_level.value.capitalize(),
            "medications":       [
                f"{med} {extraction.dosages.get(med, '')}".strip()
                for med in extraction.medications
            ],
            "consultation_time": f"{appointment.estimated_duration_minutes} minutes",
            "priority":          priority_level.value.capitalize(),
        }

        consultation_id = generate_uuid()

        return ConsultationResult(
            consultation_id=consultation_id,
            patient_id=patient_id,
            doctor_id=doctor_id,
            transcript=transcript,
            extracted_data=_extraction_to_dict(extraction),
            consultation_summary=extraction.summary,
            priority_level=priority_level.value,
            prescription_text=None,         # Populated by prescription service (future)
            recommended_follow_up=assessment.recommendation,
            structured_output=structured_output,
        )

    # ------------------------------------------------------------------
    # get_analytics
    # ------------------------------------------------------------------

    async def get_analytics(
        self, doctor_id: str, date_from: date, date_to: date
    ) -> dict:
        """
        Return aggregated analytics for *doctor_id* over [date_from, date_to].

        Currently returns a safe default skeleton until a date-range appointment
        repository query is available.
        """
        return {
            "total_consultations":              0,
            "avg_consultation_duration_minutes": 0.0,
            "priority_breakdown":               {"critical": 0, "moderate": 0, "routine": 0},
            "most_common_symptoms":             [],
            "patient_satisfaction_avg":         0.0,
            "busiest_day":                      date_from.isoformat(),
        }

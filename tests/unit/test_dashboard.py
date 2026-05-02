import pytest
from datetime import datetime, timezone, timedelta
from medisync.core.types import PriorityLevel, AppointmentStatus, ConsultationType, utc_now, generate_patient_id, generate_uuid, Appointment
from medisync.core.config import Settings
from medisync.dashboard.dashboard import DoctorDashboard, PatientQueueItem
from medisync.patient.patient_management import PatientManager
from medisync.appointment.appointment_system import AppointmentSystem
from medisync.ai_engine.nlp_engine import NLPEngine
from medisync.ai_engine.priority_engine import PriorityEngine

class MockPatientManager:
    async def get_patient(self, patient_id):
        class MockProfile:
            full_name = "John Doe"
            age = 45
            blood_group = "O+"
            status = lambda: None
            status.value = "active"
        return MockProfile()
    
    async def get_patient_summary(self, patient_id):
        return {
            "patient_id": patient_id,
            "full_name": "John Doe",
            "age": 45,
            "blood_group": "O+",
            "status": "active",
            "total_records": 5,
            "recent_diagnoses": ["Hypertension"],
            "current_medications": ["Aspirin"],
            "last_visit": "2023-01-01T10:00:00Z",
            "priority_level": "moderate"
        }
        
    async def get_consultation_logs(self, patient_id, limit):
        class MockLog:
            started_at = utc_now()
            notes = "Patient came for routine checkup."
        return [MockLog()]

class MockAppointmentSystem:
    def __init__(self):
        class MockRepo:
            async def get_by_doctor_and_date(self, doctor_id, d):
                app1 = Appointment(
                    appointment_id="a1",
                    patient_id="p1",
                    doctor_id=doctor_id,
                    scheduled_at=utc_now(),
                    consultation_type=ConsultationType.IN_PERSON,
                    status=AppointmentStatus.PENDING,
                    symptoms_description="mild headache",
                    priority_level=PriorityLevel.ROUTINE,
                    estimated_duration_minutes=15,
                    notes=None,
                    created_at=utc_now()
                )
                app2 = Appointment(
                    appointment_id="a2",
                    patient_id="p2",
                    doctor_id=doctor_id,
                    scheduled_at=utc_now(),
                    consultation_type=ConsultationType.IN_PERSON,
                    status=AppointmentStatus.PENDING,
                    symptoms_description="severe chest pain",
                    priority_level=PriorityLevel.CRITICAL,
                    estimated_duration_minutes=30,
                    notes=None,
                    created_at=utc_now()
                )
                return [app1, app2]
        self.repository = MockRepo()
        
    async def get_doctor_queue(self, doctor_id, d):
        apps = await self.repository.get_by_doctor_and_date(doctor_id, d)
        # CRITICAL first
        return [apps[1], apps[0]]
        
    async def get_today_summary(self, doctor_id):
        return {
            "date": utc_now().date().isoformat(),
            "total_appointments": 2,
            "completed": 0,
            "pending": 2,
            "critical_count": 1,
            "estimated_hours": 0.75,
            "queue": []
        }

    async def get_appointment(self, appointment_id):
        return Appointment(
            appointment_id=appointment_id,
            patient_id="p1",
            doctor_id="doc1",
            scheduled_at=utc_now(),
            consultation_type=ConsultationType.IN_PERSON,
            status=AppointmentStatus.PENDING,
            symptoms_description="testing",
            priority_level=PriorityLevel.ROUTINE,
            estimated_duration_minutes=15,
            notes=None,
            created_at=utc_now()
        )

@pytest.fixture
def mock_settings():
    return Settings(use_mock_ai=True, mongodb_url="mongodb://localhost", jwt_secret_key="secret")

@pytest.fixture
def dashboard(mock_settings):
    patient_mgr = MockPatientManager()
    appt_sys = MockAppointmentSystem()
    nlp = NLPEngine(mock_settings)
    priority = PriorityEngine(nlp, mock_settings)
    return DoctorDashboard(patient_mgr, appt_sys, nlp, priority)

@pytest.mark.asyncio
async def test_get_dashboard_overview(dashboard):
    overview = await dashboard.get_dashboard_overview("doc1", utc_now().date())
    assert overview.total_patients_today == 2
    assert overview.critical_count == 1
    assert overview.routine_count == 1
    assert len(overview.priority_queue) == 2
    assert overview.priority_queue[0].priority_level == PriorityLevel.CRITICAL.value

@pytest.mark.asyncio
async def test_get_patient_queue_ordering(dashboard):
    queue = await dashboard.get_patient_queue("doc1", utc_now().date())
    assert len(queue) == 2
    assert queue[0].priority_level == PriorityLevel.CRITICAL.value
    assert queue[1].priority_level == PriorityLevel.ROUTINE.value
    assert queue[0].priority_badge_color == "red"
    assert queue[1].priority_badge_color == "green"

@pytest.mark.asyncio
async def test_get_patient_summary_card(dashboard):
    card = await dashboard.get_patient_summary_card("p1")
    assert card.patient_id == "p1"
    assert card.full_name == "John Doe"
    assert "start_consultation" in card.quick_actions

@pytest.mark.asyncio
async def test_process_consultation_text(dashboard):
    res = await dashboard.process_consultation("a1", None, "Patient reports severe chest pain and fever")
    assert res.patient_id == "p1"
    assert res.transcript is not None
    assert "chest pain" in res.extracted_data["symptoms"]

@pytest.mark.asyncio
async def test_process_consultation_both_none(dashboard):
    from medisync.core.errors import NLPExtractionError
    with pytest.raises(NLPExtractionError):
        await dashboard.process_consultation("a1", None, None)

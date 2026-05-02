import pytest
from medisync.core.config import Settings
import medisync.core.config as config_module


@pytest.fixture
def settings():
    """Minimal test settings with mocks enabled."""
    test_settings = Settings(
        mongodb_url="mongodb://test:27017",
        jwt_secret_key="test-secret-key-32-characters-ok",
        use_mock_ai=True,
        debug=True,
    )
    # Override global settings for tests
    config_module._settings = test_settings
    yield test_settings
    config_module._settings = None

@pytest.fixture
def sample_patient():
    from medisync.core.types import PatientProfile, PatientStatus
    from datetime import date, datetime, timezone
    return PatientProfile(
        patient_id="P-TEST001",
        full_name="Riya Sharma",
        date_of_birth=date(1990, 6, 15),
        gender="female",
        contact_email="riya@example.com",
        contact_phone="+919876543210",
        status=PatientStatus.ACTIVE,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        metadata={},
    )

@pytest.fixture
def sample_appointment(sample_patient):
    from medisync.core.types import Appointment, AppointmentStatus, ConsultationType, PriorityLevel
    from datetime import datetime, timedelta, timezone
    return Appointment(
        appointment_id="APT-TEST001",
        patient_id=sample_patient.patient_id,
        scheduled_at=datetime.now(timezone.utc) + timedelta(hours=2),
        consultation_type=ConsultationType.IN_PERSON,
        status=AppointmentStatus.PENDING,
        symptoms_description="I have been experiencing severe chest pain and shortness of breath.",
        priority_level=PriorityLevel.ROUTINE,
        estimated_duration_minutes=15,
        created_at=datetime.now(timezone.utc),
    )

class MockPatientRepo:
    def __init__(self):
        self.patients = {}
        self.records = []
        self.logs = []
    
    async def create_patient(self, p):
        self.patients[p.patient_id] = p
        
    async def get_patient_by_id(self, pid):
        return self.patients.get(pid)
        
    async def get_patient_by_email(self, email):
        for p in self.patients.values():
            if p.contact_email.lower() == email.lower():
                return p
        return None
        
    async def update_patient(self, p):
        if p.patient_id in self.patients:
            self.patients[p.patient_id] = p
            
    async def search_patients(self, query, limit):
        res = []
        for p in self.patients.values():
            if query.lower() in p.full_name.lower() or query.lower() in p.contact_email.lower() or query.lower() in p.patient_id.lower():
                res.append(p)
        return res[:limit]
        
    async def create_medical_record(self, r):
        self.records.append(r)
        
    async def get_medical_records(self, pid, limit, offset=0):
        res = [r for r in self.records if r.patient_id == pid]
        res.sort(key=lambda x: x.recorded_at, reverse=True)
        return res[offset:offset+limit]
        
    async def create_consultation_log(self, log):
        self.logs.append(log)
        
    async def get_consultation_logs(self, pid, limit):
        res = [l for l in self.logs if l.patient_id == pid]
        res.sort(key=lambda x: x.started_at, reverse=True)
        return res[:limit]

@pytest.fixture
def mock_patient_repo():
    return MockPatientRepo()

class MockAppointmentRepo:
    def __init__(self):
        self.apps = {}
        
    async def create(self, a):
        self.apps[a.appointment_id] = a
        
    async def get_by_id(self, aid):
        return self.apps.get(aid)
        
    async def get_by_patient_id(self, pid, status_filter=None):
        res = [a for a in self.apps.values() if a.patient_id == pid]
        if status_filter:
            res = [a for a in res if a.status == status_filter]
        res.sort(key=lambda x: x.scheduled_at)
        return res
        
    async def get_by_doctor_and_date(self, did, d):
        res = []
        from medisync.core.types import AppointmentStatus
        for a in self.apps.values():
            if a.doctor_id == did and a.scheduled_at.date() == d and a.status in [AppointmentStatus.CONFIRMED, AppointmentStatus.IN_SESSION]:
                res.append(a)
        res.sort(key=lambda x: x.scheduled_at)
        return res
        
    async def update(self, a):
        if a.appointment_id in self.apps:
            self.apps[a.appointment_id] = a
            
    async def get_overlapping(self, did, start_time, end_time):
        from medisync.core.types import AppointmentStatus
        from datetime import timedelta
        res = []
        for a in self.apps.values():
            if a.doctor_id == did and a.status in [AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED, AppointmentStatus.IN_SESSION]:
                app_end = a.scheduled_at + timedelta(minutes=a.estimated_duration_minutes)
                if a.scheduled_at < end_time and app_end > start_time:
                    res.append(a)
        return res

@pytest.fixture
def mock_appointment_repo():
    return MockAppointmentRepo()

class MockNLPEngine:
    def __init__(self, settings):
        self.settings = settings

class MockPriorityEngine:
    def __init__(self, nlp_engine, settings):
        self.nlp_engine = nlp_engine
        self.settings = settings
        
    async def predict_priority(self, desc):
        from medisync.core.types import PriorityLevel
        if "critical" in desc.lower() or "severe" in desc.lower():
            return PriorityLevel.CRITICAL
        return PriorityLevel.ROUTINE
        
    async def estimate_duration(self, desc, history):
        return 15

@pytest.fixture
def mock_nlp_engine(settings):
    return MockNLPEngine(settings)

@pytest.fixture
def mock_priority_engine(mock_nlp_engine, settings):
    return MockPriorityEngine(mock_nlp_engine, settings)

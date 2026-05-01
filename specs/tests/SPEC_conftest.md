## Purpose
Shared pytest fixtures and test configuration for the MediSync AI test suite.
All unit tests MUST work without Docker, MongoDB, or real AI models (fully mocked).

## File Location
`tests/conftest.py`

---

## Fixture: `settings`
```python
@pytest.fixture
def settings():
    """Minimal test settings with mocks enabled."""
    return Settings(
        mongodb_url="mongodb://test:27017",
        jwt_secret_key="test-secret-key-32-characters-ok",
        use_mock_ai=True,
        debug=True,
    )
```

## Fixture: `mock_patient_repo`
```python
@pytest.fixture
def mock_patient_repo():
    """In-memory dict-based PatientRepository mock."""
    ...
```

## Fixture: `mock_appointment_repo`
```python
@pytest.fixture
def mock_appointment_repo():
    """In-memory dict-based AppointmentRepository mock."""
    ...
```

## Fixture: `sample_patient`
```python
@pytest.fixture
def sample_patient():
    return PatientProfile(
        patient_id="P-TEST001",
        full_name="Riya Sharma",
        date_of_birth=date(1990, 6, 15),
        gender="female",
        contact_email="riya@example.com",
        contact_phone="+919876543210",
        status=PatientStatus.ACTIVE,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        metadata={},
    )
```

## Fixture: `sample_appointment`
```python
@pytest.fixture
def sample_appointment(sample_patient):
    return Appointment(
        appointment_id="APT-TEST001",
        patient_id=sample_patient.patient_id,
        scheduled_at=datetime.utcnow() + timedelta(hours=2),
        consultation_type=ConsultationType.IN_PERSON,
        status=AppointmentStatus.PENDING,
        symptoms_description="I have been experiencing severe chest pain and shortness of breath.",
        priority_level=PriorityLevel.ROUTINE,
        estimated_duration_minutes=15,
        created_at=datetime.utcnow(),
    )
```

## Fixture: `mock_nlp_engine`
```python
@pytest.fixture
def mock_nlp_engine(settings):
    engine = NLPEngine(settings)
    # Mock extract_from_text to return fixed ExtractionResult
    return engine
```

## Fixture: `mock_priority_engine`
```python
@pytest.fixture
def mock_priority_engine(mock_nlp_engine, settings):
    return PriorityEngine(mock_nlp_engine, settings)
```

---

## Invariants

- All fixtures MUST be synchronous or properly async (use `pytest-asyncio`)
- No fixture MUST require network access
- All AI fixtures MUST use `settings.use_mock_ai=True`
- Repository fixtures MUST clean up state between tests
- Test database URLs MUST point to local or in-memory stores

import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from medisync.api.app import app
import pytest_asyncio

# We use httpx.AsyncClient for async tests
@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    response = await async_client.get("/api/health")
    # For now, routers return 501 Not Implemented or we might test health which is implemented
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_create_patient(async_client: AsyncClient):
    """Test POST /api/patients -> 201 + PatientResponse"""
    # Stub: implement real assertions when logic is added
    pass

@pytest.mark.asyncio
async def test_duplicate_patient(async_client: AsyncClient):
    """Test POST /api/patients (same email) -> 409"""
    # Stub: implement real assertions when logic is added
    pass

@pytest.mark.asyncio
async def test_get_unknown_patient(async_client: AsyncClient):
    """Test GET /api/patients/UNKNOWN -> 404"""
    # Stub: implement real assertions when logic is added
    pass

@pytest.mark.asyncio
async def test_book_appointment(async_client: AsyncClient):
    """Test POST /api/appointments -> 201 + AppointmentResponse"""
    # Stub: implement real assertions when logic is added
    pass

@pytest.mark.asyncio
async def test_process_consultation_text(async_client: AsyncClient):
    """Test POST /api/consultation/process -> 200 + ConsultationResult"""
    # Stub: implement real assertions when logic is added
    pass

@pytest.mark.asyncio
async def test_unauthorized_access(async_client: AsyncClient):
    """Test GET /api/patients without token -> 401"""
    # Stub: implement real assertions when logic is added
    pass

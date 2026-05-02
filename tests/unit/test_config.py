import pytest
from pydantic import ValidationError
from medisync.core.config import Settings, get_settings, override_settings
import medisync.core.config as config_module


@pytest.fixture(autouse=True)
def clear_settings_cache():
    """Ensure singleton is reset before and after each test."""
    config_module._settings = None
    yield
    config_module._settings = None


def test_missing_required_field(monkeypatch):
    monkeypatch.delenv("MONGODB_URL", raising=False)
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    with pytest.raises(ValidationError):
        Settings()


def test_default_values(monkeypatch):
    monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017")
    monkeypatch.setenv("JWT_SECRET_KEY", "test_secret_key")
    
    settings = Settings()
    
    assert settings.app_name == "MediSync AI"
    assert settings.mongodb_db_name == "medisync_db"
    assert settings.use_mock_ai is False
    assert settings.log_level == "INFO"


def test_threshold_constraint(monkeypatch):
    monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017")
    monkeypatch.setenv("JWT_SECRET_KEY", "test_secret_key")
    monkeypatch.setenv("CRITICAL_SYMPTOM_THRESHOLD", "0.4")
    monkeypatch.setenv("MODERATE_SYMPTOM_THRESHOLD", "0.5")
    
    with pytest.raises(ValueError, match="critical_symptom_threshold MUST be > moderate_symptom_threshold"):
        Settings()


def test_get_settings_singleton(monkeypatch):
    monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017")
    monkeypatch.setenv("JWT_SECRET_KEY", "test_secret_key")
    
    settings_1 = get_settings()
    settings_2 = get_settings()
    
    assert settings_1 is settings_2


def test_override_settings(monkeypatch):
    monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017")
    monkeypatch.setenv("JWT_SECRET_KEY", "test_secret_key")
    monkeypatch.setenv("PORT", "8000")
    
    global_settings = get_settings()
    assert global_settings.port == 8000
    
    overridden = override_settings(port=9000)
    
    assert overridden.port == 9000
    assert global_settings.port == 8000
    assert overridden is not global_settings

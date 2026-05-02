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
    # Reset global settings after test
    config_module._settings = None

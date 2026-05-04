"""
tests/unit/test_security.py
Unit tests for medisync.core.security — JWT creation, password hashing,
role-based access, and data sanitization.
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from medisync.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    sanitize_patient_data,
    UserRole,
    TokenData,
)
from medisync.core.errors import InvalidTokenError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def test_settings(monkeypatch):
    """Override Settings so tests don't require a .env file."""
    monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only")
    # Reset the cached singleton so it picks up the new env vars
    import medisync.core.config as cfg
    cfg._settings = None
    yield
    cfg._settings = None


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

class TestPasswordHashing:
    def test_hash_is_not_plain_text(self):
        hashed = hash_password("mypassword123")
        assert hashed != "mypassword123"

    def test_hash_starts_with_bcrypt_prefix(self):
        hashed = hash_password("mypassword123")
        assert hashed.startswith("$2b$")

    def test_verify_correct_password(self):
        hashed = hash_password("securepass!")
        assert verify_password("securepass!", hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("securepass!")
        assert verify_password("wrongpass", hashed) is False

    def test_verify_empty_string_does_not_raise(self):
        hashed = hash_password("somepass")
        result = verify_password("", hashed)
        assert result is False

    def test_two_hashes_of_same_password_differ(self):
        """bcrypt salts should make each hash unique."""
        h1 = hash_password("samepass")
        h2 = hash_password("samepass")
        assert h1 != h2


# ---------------------------------------------------------------------------
# JWT creation and decoding
# ---------------------------------------------------------------------------

class TestJWT:
    def test_create_access_token_returns_string(self, test_settings):
        token = create_access_token("U-001", UserRole.DOCTOR, "doc@clinic.com")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_access_token_fields(self, test_settings):
        token = create_access_token("U-002", UserRole.PATIENT, "pat@clinic.com")
        data = decode_token(token)
        assert data.user_id == "U-002"
        assert data.role == UserRole.PATIENT
        assert data.email == "pat@clinic.com"
        assert isinstance(data.exp, datetime)
        assert isinstance(data.iat, datetime)

    def test_create_refresh_token_returns_string(self, test_settings):
        token = create_refresh_token("U-003")
        assert isinstance(token, str)

    def test_tampered_token_raises_invalid_token_error(self, test_settings):
        token = create_access_token("U-004", UserRole.ADMIN, "admin@clinic.com")
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(InvalidTokenError):
            decode_token(tampered)

    def test_decode_completely_invalid_token_raises(self, test_settings):
        with pytest.raises(InvalidTokenError):
            decode_token("not.a.jwt.token")

    def test_all_roles_produce_decodable_token(self, test_settings):
        for role in UserRole:
            token = create_access_token("U-999", role, f"{role.value}@test.com")
            data = decode_token(token)
            assert data.role == role


# ---------------------------------------------------------------------------
# sanitize_patient_data
# ---------------------------------------------------------------------------

class TestSanitizePatientData:
    FULL_DATA = {
        "patient_id": "P-001",
        "full_name": "Jane Doe",
        "contact_email": "jane@example.com",
        "insurance_id": "INS-99999",
        "billing_info": "VISA ending 4242",
        "metadata": {
            "prior_visits": 5,
            "insurance_id": "NESTED-INS",
        },
    }

    def test_patient_role_sees_all_own_data(self):
        result = sanitize_patient_data(self.FULL_DATA.copy(), UserRole.PATIENT)
        assert "insurance_id" in result
        assert "billing_info" in result

    def test_nurse_role_strips_sensitive_fields(self):
        result = sanitize_patient_data(self.FULL_DATA.copy(), UserRole.NURSE)
        assert "insurance_id" not in result
        assert "billing_info" not in result

    def test_nurse_role_strips_nested_sensitive_fields(self):
        result = sanitize_patient_data(self.FULL_DATA.copy(), UserRole.NURSE)
        if "metadata" in result and isinstance(result["metadata"], dict):
            assert "insurance_id" not in result["metadata"]

    def test_doctor_role_sees_full_data(self):
        result = sanitize_patient_data(self.FULL_DATA.copy(), UserRole.DOCTOR)
        assert "insurance_id" in result

    def test_admin_role_sees_full_data(self):
        result = sanitize_patient_data(self.FULL_DATA.copy(), UserRole.ADMIN)
        assert "insurance_id" in result

    def test_original_dict_is_not_mutated(self):
        original = self.FULL_DATA.copy()
        sanitize_patient_data(original, UserRole.NURSE)
        assert "insurance_id" in original  # original should be unchanged


# ---------------------------------------------------------------------------
# UserRole enum
# ---------------------------------------------------------------------------

class TestUserRole:
    def test_all_roles_have_string_values(self):
        for role in UserRole:
            assert isinstance(role.value, str)

    def test_role_from_string(self):
        assert UserRole("doctor") == UserRole.DOCTOR
        assert UserRole("patient") == UserRole.PATIENT
        assert UserRole("admin") == UserRole.ADMIN
        assert UserRole("nurse") == UserRole.NURSE

    def test_invalid_role_raises(self):
        with pytest.raises(ValueError):
            UserRole("superuser")

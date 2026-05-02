import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt

from medisync.core.security import (
    UserRole,
    TokenData,
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
    require_role,
    sanitize_patient_data,
)
from medisync.core.errors import InvalidTokenError, InsufficientPermissionsError


def test_hash_password():
    password = "password123"
    hashed = hash_password(password)
    assert hashed.startswith("$2b$")
    assert hashed != password


def test_verify_password_match():
    password = "password123"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True


def test_verify_password_mismatch():
    password = "password123"
    hashed = hash_password(password)
    assert verify_password("wrongpassword", hashed) is False


def test_create_access_token(settings):
    user_id = "U-123"
    role = UserRole.DOCTOR
    email = "doctor@example.com"
    
    token = create_access_token(user_id, role, email)
    token_data = decode_token(token)
    
    assert token_data.user_id == user_id
    assert token_data.role == role
    assert token_data.email == email
    # Check that expiry is roughly correct
    now = datetime.now(timezone.utc)
    assert token_data.exp > now
    assert token_data.iat <= now


def test_decode_token_expired(settings):
    # Manually create an expired token
    now = datetime.now(timezone.utc)
    expire = now - timedelta(minutes=10)
    payload = {
        "sub": "U-123",
        "role": UserRole.PATIENT.value,
        "email": "patient@example.com",
        "iat": now.timestamp(),
        "exp": expire.timestamp()
    }
    expired_token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    
    with pytest.raises(InvalidTokenError, match="Token is invalid or expired"):
        decode_token(expired_token)


def test_decode_token_tampered(settings):
    user_id = "U-123"
    token = create_access_token(user_id, UserRole.PATIENT, "patient@example.com")
    
    # Tamper with the token by appending a character
    tampered_token = token + "a"
    
    with pytest.raises(InvalidTokenError, match="Token is invalid or expired"):
        decode_token(tampered_token)


def test_require_role_wrong_role():
    # Setup dependency with DOCTOR and ADMIN required
    role_checker = require_role(UserRole.DOCTOR, UserRole.ADMIN)
    
    # Mock a PATIENT user
    patient_user = TokenData(
        user_id="U-123",
        role=UserRole.PATIENT,
        email="patient@example.com",
        exp=datetime.now(timezone.utc),
        iat=datetime.now(timezone.utc)
    )
    
    # Executing the dependency should raise InsufficientPermissionsError
    with pytest.raises(InsufficientPermissionsError, match="User role patient not in required roles"):
        role_checker(patient_user)


def test_sanitize_patient_data():
    patient_dict = {
        "full_name": "John Doe",
        "contact_phone": "+1234567890",
        "insurance_id": "INS-999",
        "metadata": {
            "billing_info": "Card ending in 1234",
            "other_info": "Safe"
        }
    }
    
    # Nurse role
    sanitized_nurse = sanitize_patient_data(patient_dict, UserRole.NURSE)
    assert "contact_phone" in sanitized_nurse
    assert "insurance_id" not in sanitized_nurse
    assert "billing_info" not in sanitized_nurse.get("metadata", {})
    assert "other_info" in sanitized_nurse.get("metadata", {})
    
    # Patient role (should not sanitize anything)
    sanitized_patient = sanitize_patient_data(patient_dict, UserRole.PATIENT)
    assert "insurance_id" in sanitized_patient
    assert "billing_info" in sanitized_patient.get("metadata", {})

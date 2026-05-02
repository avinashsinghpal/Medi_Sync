from datetime import datetime, timedelta, timezone
from enum import Enum
from dataclasses import dataclass
from typing import Callable, Any, Dict, List

import bcrypt
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from medisync.core.config import get_settings
from medisync.core.errors import InvalidTokenError, InsufficientPermissionsError


class UserRole(str, Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"
    NURSE = "nurse"


@dataclass
class TokenData:
    user_id: str
    role: UserRole
    email: str
    exp: datetime
    iat: datetime


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def hash_password(password: str) -> str:
    """Use bcrypt to hash a password. Must use >= 12 rounds."""
    salt = bcrypt.gensalt(rounds=12)
    pwd_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash. Never raises an exception."""
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False


def create_access_token(user_id: str, role: UserRole, email: str) -> str:
    """Creates a short-lived access JWT."""
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    
    payload = {
        "sub": user_id,
        "role": role.value,
        "email": email,
        "iat": now.timestamp(),
        "exp": expire.timestamp()
    }
    encoded_jwt = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def create_refresh_token(user_id: str) -> str:
    """Creates a long-lived refresh JWT."""
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.jwt_refresh_token_expire_days)
    
    payload = {
        "sub": user_id,
        "type": "refresh",
        "iat": now.timestamp(),
        "exp": expire.timestamp()
    }
    encoded_jwt = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def decode_token(token: str) -> TokenData:
    """Decodes and validates a JWT."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        
        user_id: str = payload.get("sub")
        role_str: str = payload.get("role")
        email: str = payload.get("email")
        exp_ts: float = payload.get("exp")
        iat_ts: float = payload.get("iat")
        
        if user_id is None or role_str is None or email is None:
            raise InvalidTokenError("Missing required token fields")
            
        try:
            role = UserRole(role_str)
        except ValueError:
            raise InvalidTokenError(f"Invalid role in token: {role_str}")
            
        return TokenData(
            user_id=user_id,
            role=role,
            email=email,
            exp=datetime.fromtimestamp(exp_ts, tz=timezone.utc),
            iat=datetime.fromtimestamp(iat_ts, tz=timezone.utc),
        )
    except JWTError as e:
        raise InvalidTokenError("Token is invalid or expired") from e


def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """FastAPI dependency to extract and validate the bearer token."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return decode_token(token)
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_role(*roles: UserRole) -> Callable:
    """Factory to create a FastAPI dependency for role-based access control."""
    def role_checker(user: TokenData = Depends(get_current_user)) -> TokenData:
        if user.role not in roles:
            raise InsufficientPermissionsError(
                f"User role {user.role.value} not in required roles: {[r.value for r in roles]}"
            )
        return user
    return role_checker


def sanitize_patient_data(data: dict, viewer_role: UserRole) -> dict:
    """Removes PII and financial fields depending on the viewer's role."""
    sanitized = data.copy()
    
    if viewer_role == UserRole.PATIENT:
        # Patients can see all their own data
        return sanitized
        
    if viewer_role == UserRole.NURSE:
        # Nurses should not see detailed financial/insurance info
        sensitive_fields = ["insurance_id", "billing_info", "financial_details", "credit_card"]
        for field in sensitive_fields:
            if field in sanitized:
                del sanitized[field]
            # Also check within metadata if present
            if "metadata" in sanitized and isinstance(sanitized["metadata"], dict):
                if field in sanitized["metadata"]:
                    sanitized["metadata"] = sanitized["metadata"].copy()
                    del sanitized["metadata"][field]
                    
    # Admins and Doctors might have full access (or different filters, but spec says PATIENT and NURSE)
    return sanitized

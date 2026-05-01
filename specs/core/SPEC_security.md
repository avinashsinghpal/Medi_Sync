## Purpose
JWT-based authentication and patient data protection utilities.
All sensitive patient data access MUST pass through this module's validation.

## File Location
`medisync/core/security.py`

## Dependencies
- `passlib`, `python-jose`, `cryptography`
- `medisync/core/config.py`
- NO imports from patient, appointment, or ai_engine modules

---

## `UserRole` (Enum)

```python
class UserRole(str, Enum):
    PATIENT = "patient"   # Can view/edit own records only
    DOCTOR  = "doctor"    # Can view/update assigned patients
    ADMIN   = "admin"     # Full system access
    NURSE   = "nurse"     # Read access + appointment management
```

---

## `TokenData` (Dataclass)

```python
@dataclass
class TokenData:
    user_id: str
    role: UserRole
    email: str
    exp: datetime     # Token expiry (UTC)
    iat: datetime     # Token issued-at (UTC)
```

---

## Functions to Implement

### `hash_password(password: str) -> str`
- Use bcrypt with salt rounds ≥ 12
- MUST NOT store raw password anywhere in logs or memory beyond this call

### `verify_password(plain_password: str, hashed_password: str) -> bool`
- Returns True if passwords match, False otherwise
- NEVER raises exception for wrong password (return False silently)

### `create_access_token(user_id: str, role: UserRole, email: str) -> str`
- Creates JWT with HS256 algorithm
- Expiry from `settings.jwt_access_token_expire_minutes`
- Payload MUST include: `sub`, `role`, `email`, `exp`, `iat`

### `create_refresh_token(user_id: str) -> str`
- Creates long-lived JWT for session renewal
- Expiry from `settings.jwt_refresh_token_expire_days`

### `decode_token(token: str) -> TokenData`
- Decodes and validates JWT
- Raises `InvalidTokenError` if expired or tampered
- Raises `InvalidTokenError` if role is not a valid `UserRole`

### `require_role(*roles: UserRole) -> Callable`
- FastAPI dependency factory
- Returns a dependency that raises `HTTP 403` if the current user's role is not in `roles`
- Usage: `Depends(require_role(UserRole.DOCTOR, UserRole.ADMIN))`

### `get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData`
- FastAPI dependency
- Extracts and validates bearer token from Authorization header
- Raises `HTTP 401` if no token or invalid token

### `sanitize_patient_data(data: dict, viewer_role: UserRole) -> dict`
- Removes PII fields that the viewer role is not authorized to see
- PATIENT role: can see own data fully
- NURSE role: hides detailed financial/insurance data
- Returns sanitized copy (never mutates original)

---

## Security Invariants

- Passwords MUST NEVER appear in logs
- Patient IDs in logs MUST be truncated to first 8 chars
- All tokens MUST be invalidated on password change
- `sanitize_patient_data` MUST be called before returning any PatientProfile over API

---

## Expected Test Outcomes (from `tests/unit/test_security.py`)

| Test | Input | Expected Output |
|---|---|---|
| hash_password | "password123" | bcrypt hash starting with "$2b$" |
| verify_password match | plain + hash | True |
| verify_password mismatch | wrong + hash | False |
| create_access_token | valid user_id | Valid JWT decodable to TokenData |
| decode_token expired | expired JWT | `InvalidTokenError` |
| decode_token tampered | modified JWT | `InvalidTokenError` |
| require_role wrong role | PATIENT accessing DOCTOR route | HTTP 403 |
| sanitize_patient_data | NURSE + patient dict | contact_phone present, insurance_id removed |

## Purpose
Centralized application configuration using Pydantic Settings.
Reads from environment variables and `.env` file.
Single instance shared across the entire application via `get_settings()`.

## File Location
`medisync/core/config.py`

## Dependencies
- `pydantic-settings`, `pydantic`
- NO imports from any other `medisync/` module

---

## `Settings` (Pydantic BaseSettings)

```python
class Settings(BaseSettings):
    # ── Application ──────────────────────────────────────────
    app_name: str = "MediSync AI"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"   # "DEBUG" | "INFO" | "WARNING" | "ERROR"

    # ── Server ───────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000
    allowed_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # ── Database ─────────────────────────────────────────────
    mongodb_url: str           # REQUIRED — from env or .env
    mongodb_db_name: str = "medisync_db"
    redis_url: str = "redis://localhost:6379"

    # ── Authentication ────────────────────────────────────────
    jwt_secret_key: str        # REQUIRED — strong random secret
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7

    # ── AI / NLP ─────────────────────────────────────────────
    openai_api_key: Optional[str] = None    # For GPT-based NLP
    groq_api_key: Optional[str] = None      # Groq Llama3 fallback
    embedding_model: str = "all-MiniLM-L6-v2"
    nlp_model: str = "en_core_web_sm"       # spaCy model name

    # ── Speech Processing ─────────────────────────────────────
    speech_provider: str = "whisper"        # "whisper" | "google" | "azure"
    whisper_model_size: str = "base"        # "tiny" | "base" | "small" | "medium"

    # ── Priority Engine ───────────────────────────────────────
    critical_symptom_threshold: float = 0.8   # Score ≥ 0.8 → CRITICAL
    moderate_symptom_threshold: float = 0.5   # Score ≥ 0.5 → MODERATE
    max_consultation_time_minutes: int = 60
    default_consultation_time_minutes: int = 15

    # ── Feature Flags ─────────────────────────────────────────
    enable_speech_processing: bool = True
    enable_ai_prioritization: bool = True
    enable_time_prediction: bool = True
    use_mock_ai: bool = False  # True in test environments

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
```

---

## Singleton Factory

```python
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """
    Return the global Settings singleton.
    Creates on first call, cached thereafter.
    Override with TEST_OVERRIDE environment variable in tests.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

def override_settings(**kwargs) -> Settings:
    """
    For testing only: create a temporary Settings with overridden values.
    Does NOT mutate the global singleton.
    """
    ...
```

---

## `.env.example` Template

```env
# Required
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/
JWT_SECRET_KEY=your-super-secret-key-here

# Optional AI Keys
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...

# Feature Flags
USE_MOCK_AI=false
ENABLE_SPEECH_PROCESSING=true
DEBUG=false
```

---

## Constraints

- `mongodb_url` MUST be provided or `ValidationError` is raised at startup
- `jwt_secret_key` MUST be provided or `ValidationError` is raised at startup
- `critical_symptom_threshold` MUST be > `moderate_symptom_threshold`
- `log_level` MUST be one of: `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`
- In test mode (`use_mock_ai=True`), AI calls MUST use mock implementations

---

## Expected Test Outcomes (from `tests/unit/test_config.py`)

| Test | Input | Expected Output |
|---|---|---|
| Missing required field | No MONGODB_URL | `ValidationError` at `Settings()` |
| Default values | Minimal env | All defaults applied correctly |
| Threshold constraint | critical < moderate | `ValueError` raised |
| get_settings singleton | Call twice | Same object identity |
| override_settings | New port=9000 | New Settings with port=9000, global unchanged |

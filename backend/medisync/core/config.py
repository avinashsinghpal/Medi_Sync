from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


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
    mongodb_url: str           # REQUIRED
    mongodb_db_name: str = "medisync_db"
    redis_url: str = "redis://localhost:6379"

    # ── Authentication ────────────────────────────────────────
    jwt_secret_key: str        # REQUIRED
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7

    # ── AI / NLP ─────────────────────────────────────────────
    openai_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    embedding_model: str = "all-MiniLM-L6-v2"
    nlp_model: str = "en_core_web_sm"

    # ── Speech Processing ─────────────────────────────────────
    speech_provider: str = "whisper"
    whisper_model_size: str = "base"

    # ── Priority Engine ───────────────────────────────────────
    critical_symptom_threshold: float = 0.8
    moderate_symptom_threshold: float = 0.5
    max_consultation_time_minutes: int = 60
    default_consultation_time_minutes: int = 15

    # ── Feature Flags ─────────────────────────────────────────
    enable_speech_processing: bool = True
    enable_ai_prioritization: bool = True
    enable_time_prediction: bool = True
    use_mock_ai: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @model_validator(mode="after")
    def validate_thresholds_and_log_level(self):
        if self.critical_symptom_threshold <= self.moderate_symptom_threshold:
            raise ValueError("critical_symptom_threshold MUST be > moderate_symptom_threshold")
        if self.log_level not in {"DEBUG", "INFO", "WARNING", "ERROR"}:
            raise ValueError('log_level MUST be one of: "DEBUG", "INFO", "WARNING", "ERROR"')
        return self


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Return the global Settings singleton.
    Creates on first call, cached thereafter.
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
    base = get_settings()
    return base.model_copy(update=kwargs)

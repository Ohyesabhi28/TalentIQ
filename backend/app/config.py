"""
Application configuration.

All settings are loaded from environment variables (or .env file).
Never hard-code secrets here — use .env.example as a reference template.
"""

from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central settings object for the entire application.

    Priority (highest → lowest):
      1. Real environment variables
      2. .env file
      3. Default values defined here
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ────────────────────────────────────────────────────────
    APP_NAME: str = "TalentIQ API"
    APP_VERSION: str = "0.1.0"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False

    # ── API ────────────────────────────────────────────────────────────────
    API_V1_PREFIX: str = "/v1"
    API_TITLE: str = "TalentIQ REST API"
    API_DESCRIPTION: str = (
        "Enterprise AI Recruiter Platform — REST API powering the TalentIQ frontend."
    )

    # ── Server ─────────────────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ── Security ───────────────────────────────────────────────────────────
    SECRET_KEY: str = Field(
        default="change-me-in-production",
        description="Used for signing JWT tokens. Must be at least 32 chars.",
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ── CORS ───────────────────────────────────────────────────────────────
    # Comma-separated list of allowed origins, or "*" for development.
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
    )
    CORS_ALLOW_CREDENTIALS: bool = True

    # ── Database ───────────────────────────────────────────────────────────
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://talentiq:talentiq@localhost:5432/talentiq",
        description="Async SQLAlchemy connection URL.",
    )
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # ── Redis ──────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Object Storage ─────────────────────────────────────────────────────
    S3_BUCKET_NAME: str = "talentiq-files"
    S3_REGION: str = "ap-south-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    S3_PRESIGNED_URL_EXPIRY_SECONDS: int = 3600

    # ── File Upload ────────────────────────────────────────────────────────
    MAX_FILE_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB
    ALLOWED_MIME_TYPES: list[str] = Field(
        default=[
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
        ]
    )

    # ── AI / LLM ───────────────────────────────────────────────────────────
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    EMBEDDING_MODEL: str = "models/text-embedding-004"

    # ── Support ────────────────────────────────────────────────────────────
    SUPPORT_EMAIL: str = "support@talentiq.io"

    # ── Logging ────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = False  # Set True in production for structured JSON logs

    # ── Validators ─────────────────────────────────────────────────────────
    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_must_be_strong(cls, v: str) -> str:
        if v == "change-me-in-production":
            import warnings
            warnings.warn(
                "SECRET_KEY is set to the default insecure value. "
                "Override it in your .env file before deploying.",
                UserWarning,
                stacklevel=2,
            )
        return v

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return a cached singleton Settings instance.

    Using lru_cache means the .env file is parsed only once at startup.
    In tests, call get_settings.cache_clear() before overriding settings.
    """
    return Settings()

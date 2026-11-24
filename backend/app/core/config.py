"""Application Configuration for SafeTriage.

Configures:
- Database connection (SQLite default, PostgreSQL-ready)
- Security & JWT settings
- Environment & Production safety checks (refuses to start in production with default secrets)
- Rate limiting parameters
"""

import os
from typing import List
from pydantic import BaseModel, Field


class Settings(BaseModel):
    PROJECT_NAME: str = "SafeTriage"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Environment: development, test, production
    ENVIRONMENT: str = Field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))

    # Database
    DATABASE_URL: str = Field(
        default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./safetriage.db")
    )

    # JWT Settings
    JWT_SECRET: str = Field(
        default_factory=lambda: os.getenv("JWT_SECRET", "safetriage-insecure-dev-secret-key-change-in-production")
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ]
    )

    # Rate Limiting
    LOGIN_RATE_LIMIT_MAX_ATTEMPTS: int = 5
    LOGIN_RATE_LIMIT_WINDOW_SECONDS: int = 60

    # Follow-ups
    DEFAULT_MAX_OPTIONAL_FOLLOWUPS: int = 3

    # Guest Retention (TTL in hours)
    GUEST_RETENTION_HOURS: int = 24

    def validate_production_safety(self) -> None:
        """Refuse to start in production if insecure default JWT secret is used."""
        if self.ENVIRONMENT.lower() == "production":
            insecure_defaults = [
                "safetriage-insecure-dev-secret-key-change-in-production",
                "secret",
                "changeme",
                "default",
            ]
            if self.JWT_SECRET in insecure_defaults or len(self.JWT_SECRET) < 32:
                raise RuntimeError(
                    "FATAL SECURITY ERROR: Cannot start SafeTriage in production with default "
                    "or short (<32 chars) JWT_SECRET. Configure a cryptographically secure key."
                )


settings = Settings()
# Check startup safety
settings.validate_production_safety()

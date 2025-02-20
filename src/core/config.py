# src/core/config.py
from typing import ClassVar, Optional

from pydantic import computed_field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings and configuration.
    attention: DO NOT EDIT THIS FILE
    check `src/docs/ENVIRONMENT.md` for details
    """

    # Project settings
    API_VERSION: str = "0.0.1"
    COMPOSE_PROJECT_NAME: str = "set-project-name"
    ENVIRONMENT: str = "dev"
    PROJECT_NAME: str = "set-project-name"

    # API Server Settings
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # Docker Compose Settings
    GID: int = 1000
    UID: int = 1000

    # Database Configuration
    POSTGRES_DB: str = "set-db-name"
    POSTGRES_HOST: str = "set-db-host"
    POSTGRES_PASSWORD: str = "set-postgres-password"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "set-postgres-user"

    # Security Settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    ALGORITHM: str = "HS256"
    LOGIN_RATE_LIMIT_REQUESTS: int = 20
    LOGIN_RATE_LIMIT_WINDOW: int = 60
    REFRESH_SECRET_KEY: str = "set-refresh-secret-key"
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SECRET_KEY: str = "set-secret-key"
    TOKEN_AUDIENCE: str = "your-app-users"
    TOKEN_ISSUER: str = "your-app-name"

    # Auth Settings
    AUTH_ALGORITHM: str = "HS256"
    AUTH_REFRESH_SECRET_KEY: str
    AUTH_SECRET_KEY: str
    AUTH_TOKEN_AUDIENCE: str = "fastapi-users"
    AUTH_TOKEN_ISSUER: str = "fastapi-auth-service"

    # CORS Configuration
    ALLOWED_ORIGINS: Optional[str] = None

    # Redis Configuration
    REDIS_URL: str = "redis://redis:6379/0"

    # Logging Configuration
    LOG_LEVEL: str = "INFO"

    # Token type constants
    TOKEN_TYPE_ACCESS: ClassVar[str] = "access"  # nosec B105
    TOKEN_TYPE_REFRESH: ClassVar[str] = "refresh"  # nosec B105

    # Database Configuration (Generated)
    DATABASE_URL: str = ""
    TEST_DATABASE_URL: str = ""

    @field_validator("POSTGRES_DB")
    @classmethod
    def validate_database_name(cls, v: str, info) -> str:
        """Validate and format database name using project name and environment."""
        if not v:
            raise ValueError("POSTGRES_DB must be set")
        project_name = info.data.get("PROJECT_NAME", "set-project-name")
        environment = info.data.get("ENVIRONMENT", "dev")
        return f"{project_name}_{environment}"

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str, info) -> str:
        """Validate and format database URL using project name and environment."""
        if not v:
            raise ValueError("DATABASE_URL must be set")
        return v

    class Config:
        """Pydantic settings configuration."""

        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


# Create a global settings instance
settings = Settings()

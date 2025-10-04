"""Application configuration using pydantic-settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Parents Healthline Assistant"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # Database
    database_url: str = "postgresql://healthline_user:healthline_pass@localhost:5432/healthline_db"

    # Anthropic API
    anthropic_api_key: str = ""

    # Security
    secret_key: str = "change-this-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Performance
    max_response_time_seconds: int = 5
    max_concurrent_requests: int = 1000

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()

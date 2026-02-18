"""Application configuration from environment variables."""

from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/todo_db"

    # JWT Configuration
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # CORS - can be set as comma-separated string in env: CORS_ORIGINS="url1,url2"
    cors_origins: list[str] = ["*"]  # Allow all origins for now

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # Environment
    environment: str = "development"

    # OpenAI Configuration (Phase 3)
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # Chat Configuration (Phase 3)
    max_conversation_messages: int = 20

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()

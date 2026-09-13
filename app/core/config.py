"""Environment-backed application settings."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from `.env` and environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    llm_provider: str = Field(default="gemini", alias="LLM_PROVIDER")
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-flash-latest", alias="GEMINI_MODEL")
    llm_temperature: float = Field(default=0.2, alias="LLM_TEMPERATURE", ge=0, le=1)
    llm_timeout_seconds: float = Field(default=30, alias="LLM_TIMEOUT_SECONDS", gt=0, le=120)
    workflow_timeout_seconds: float = Field(
        default=60, alias="WORKFLOW_TIMEOUT_SECONDS", gt=0, le=300
    )
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")


@lru_cache
def get_settings() -> Settings:
    """Return one immutable settings object for the process."""

    return Settings()

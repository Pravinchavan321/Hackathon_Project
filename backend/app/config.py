"""Application configuration settings for AgentShield AI.
Loads environment variables using pydantic-settings.
"""
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Core application settings."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_ENV: str = "development"
    APP_SECRET_KEY: str = "default-dev-secret-key-change-in-production-64char"
    JWT_SECRET_KEY: str = "default-jwt-secret-key-change-in-production-64char"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "agentshield_ai"

    GEMINI_API_KEY: Optional[str] = ""
    LLM_PROVIDER: str = "mock"  # "mock" or "gemini"

    FRONTEND_ORIGIN: str = "http://localhost:5173"
    STORAGE_MODE: str = "local"
    LOCAL_STORAGE_PATH: str = "./storage"


@lru_cache()
def get_settings() -> Settings:
    """Return cached singleton settings instance."""
    return Settings()

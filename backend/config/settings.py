"""
Sentinel AI - Settings Configuration
======================================
File: backend/config/settings.py
Purpose: Pydantic BaseSettings class for environment variables and 
         secrets management. Implements a Singleton pattern.

Dependencies: pydantic-settings, pydantic, python-dotenv
"""

import os
from pathlib import Path
from functools import lru_cache
from typing import Optional, List
from loguru import logger
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Locate root .env file
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and .env files.
    """

    # Environment & Application
    ENVIRONMENT: str = Field(default="development", alias="ENVIRONMENT")
    DEBUG: bool = Field(default=True, alias="DEBUG")
    APP_NAME: str = Field(default="Sentinel AI", alias="APP_NAME")
    APP_VERSION: str = Field(default="1.0.0", alias="APP_VERSION")
    API_V1_STR: str = Field(default="/api/v1", alias="API_V1_STR")

    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000", "*"],
        alias="CORS_ORIGINS"
    )

    # Gemini API
    GEMINI_API_KEY: str = Field(default="", alias="GEMINI_API_KEY")
    GEMINI_MODEL: str = Field(default="gemini-2.0-flash", alias="GEMINI_MODEL")
    GEMINI_TEMPERATURE: float = Field(default=0.2, alias="GEMINI_TEMPERATURE")

    # PostgreSQL Database Configuration
    POSTGRES_HOST: str = Field(default="localhost", alias="POSTGRES_HOST")
    POSTGRES_PORT: str = Field(default="5432", alias="POSTGRES_PORT")
    POSTGRES_DB: str = Field(default="sentinel_db", alias="POSTGRES_DB")
    POSTGRES_USER: str = Field(default="postgres", alias="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(default="postgres", alias="POSTGRES_PASSWORD")

    # Optional Direct Connection String Override
    RAW_DATABASE_URL: Optional[str] = Field(default=None, alias="DATABASE_URL")

    # Neo4j Knowledge Graph Configuration
    NEO4J_URI: str = Field(default="bolt://localhost:7687", alias="NEO4J_URI")
    NEO4J_USER: str = Field(default="neo4j", alias="NEO4J_USER")
    NEO4J_PASSWORD: str = Field(default="password", alias="NEO4J_PASSWORD")

    # JWT Security & Authentication
    SECRET_KEY: str = Field(
        default="YOUR_SUPER_SECRET_HACKATHON_KEY_DO_NOT_USE_IN_PROD",
        alias="SECRET_KEY"
    )
    ALGORITHM: str = Field(default="HS256", alias="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=10080, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Machine Learning
    ML_MODEL_DIR: str = Field(default="ml/models", alias="ML_MODEL_DIR")

    @property
    def DATABASE_URL(self) -> str:
        """Construct or return async PostgreSQL connection string."""
        if self.RAW_DATABASE_URL and self.RAW_DATABASE_URL.strip():
            url = self.RAW_DATABASE_URL.strip()
            if url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
                return url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url

        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def DATABASE_URL_SYNC(self) -> str:
        """Construct sync PostgreSQL connection string."""
        if self.RAW_DATABASE_URL and self.RAW_DATABASE_URL.strip():
            url = self.RAW_DATABASE_URL.strip()
            if url.startswith("postgresql+asyncpg://"):
                return url.replace("postgresql+asyncpg://", "postgresql://", 1)
            return url

        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def JWT_SECRET_KEY(self) -> str:
        """Alias for SECRET_KEY."""
        return self.SECRET_KEY

    @property
    def JWT_ALGORITHM(self) -> str:
        """Alias for ALGORITHM."""
        return self.ALGORITHM

    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Alias for BACKEND_CORS_ORIGINS."""
        return self.BACKEND_CORS_ORIGINS

    def validate_database_config(self) -> bool:
        """
        Check database configuration and return True if configured.
        """
        if not self.POSTGRES_USER or not self.POSTGRES_PASSWORD:
            logger.warning("PostgreSQL credentials rely on defaults. Ensure .env is properly configured.")
            return False
        return True

    model_config = SettingsConfigDict(
        env_file=[str(ENV_FILE), ".env"],
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get a cached instance of the Settings object (Singleton pattern).
    """
    return Settings()

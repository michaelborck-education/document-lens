"""
Configuration settings for CiteSight API
"""

import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App settings
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "CiteSight"

    # CORS settings
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",  # React dev server
        "http://localhost:80",    # Production frontend
        "http://0.0.0.0:3000",
    ]

    # File processing settings
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB default
    PROCESS_TIMEOUT: int = int(os.getenv("PROCESS_TIMEOUT", "120"))   # 2 minutes
    MAX_FILES_PER_REQUEST: int = int(os.getenv("MAX_FILES_PER_REQUEST", "5"))

    # Rate limiting
    RATE_LIMIT: str = os.getenv("RATE_LIMIT", "10/hour")

    # Analysis settings
    DEFAULT_CITATION_STYLE: str = "auto"
    SUPPORTED_FILE_TYPES: list[str] = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # DOCX
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",  # PPTX
        "text/plain",
        "text/markdown",
        "application/json"
    ]

    # External services
    CROSSREF_API_BASE: str = "https://api.crossref.org"
    WAYBACK_API_BASE: str = "https://archive.org/wayback"

    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

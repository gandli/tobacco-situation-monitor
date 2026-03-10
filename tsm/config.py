"""Configuration for TSM application."""

from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application settings
    app_name: str = "TSM - Tobacco Situation Monitor"
    version: str = "0.1.0"
    debug: bool = False
    
    # Database settings
    database_path: str = "tsm.db"
    
    # Logging settings
    log_level: str = "INFO"
    log_file: str = "logs/tsm.log"
    
    # CORS settings
    cors_origins: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()

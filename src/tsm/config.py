"""Configuration for TSM application."""

import logging
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Database settings
    database_url: str = "sqlite:///tsm.db"
    database_path: Path = Path("tsm.db")
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Application settings
    app_title: str = "Tobacco Situation Monitor"
    app_version: str = "0.1.0"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format=settings.log_format,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("tsm.log", encoding="utf-8")
    ]
)

logger = logging.getLogger(__name__)
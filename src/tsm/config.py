"""Configuration for TSM application."""

import logging
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Database settings - database_url is the single source of truth
    database_url: str = "sqlite:///tsm.db"
    database_path: Optional[Path] = None  # Derived from database_url
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Application settings
    app_title: str = "Tobacco Situation Monitor"
    app_version: str = "0.1.0"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @model_validator(mode="after")
    def derive_database_path(self) -> "Settings":
        """Derive database_path from database_url for SQLite URLs."""
        url = self.database_url
        if url.startswith("sqlite:///"):
            # Handle both relative and absolute paths
            path_str = url[len("sqlite:///"):]
            self.database_path = Path(path_str)
        return self


# Global settings instance
settings = Settings()


def setup_logging() -> None:
    """Configure logging for the application.
    
    This should be called from the application entry point, not at import time.
    """
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format=settings.log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("tsm.log", encoding="utf-8")
        ]
    )


logger = logging.getLogger(__name__)

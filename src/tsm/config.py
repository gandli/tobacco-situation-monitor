"""Configuration for TSM."""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "TSM"
    debug: bool = False
    database_path: Path = Path("tsm.db")
    log_level: str = "INFO"
    api_key: Optional[str] = None  # For future authentication

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
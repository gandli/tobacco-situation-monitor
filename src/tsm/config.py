"""Configuration for TSM."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "TSM"
    debug: bool = False


settings = Settings()
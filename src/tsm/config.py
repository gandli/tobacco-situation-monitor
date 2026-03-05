"""Configuration for TSM.

Centralized configuration management using pydantic-settings.
"""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support.

    Configuration can be provided via:
    1. Environment variables (e.g., TSM_APP_NAME, TSM_DEBUG)
    2. .env file
    3. Default values in this class
    """

    model_config = SettingsConfigDict(
        env_prefix="TSM_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="TSM", description="Application name")
    debug: bool = Field(default=False, description="Enable debug mode")
    version: str = Field(default="0.2.0", description="Application version")

    # Database
    database_path: str = Field(
        default="tsm.db",
        description="Path to SQLite database file"
    )
    database_timeout: float = Field(
        default=5.0,
        description="Database connection timeout in seconds"
    )

    # API
    api_host: str = Field(default="0.0.0.0", description="API server host")
    api_port: int = Field(default=8000, description="API server port")
    api_prefix: str = Field(default="/api", description="API URL prefix")
    cors_origins: list[str] = Field(
        default=["*"],
        description="Allowed CORS origins"
    )

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[str] = Field(
        default=None,
        description="Path to log file (None for console only)"
    )

    # Crawler
    crawler_timeout: float = Field(
        default=10.0,
        description="HTTP request timeout in seconds"
    )
    crawler_user_agent: str = Field(
        default="TSM-Crawler/0.2.0",
        description="User-Agent header for HTTP requests"
    )
    crawler_max_retries: int = Field(
        default=3,
        description="Maximum number of retry attempts"
    )
    crawler_delay: float = Field(
        default=1.0,
        description="Delay between requests in seconds"
    )

    # Scheduler
    scheduler_enabled: bool = Field(
        default=True,
        description="Enable background scheduler"
    )
    crawl_interval_hours: int = Field(
        default=1,
        description="Hours between crawl jobs"
    )

    # Security
    secret_key: Optional[str] = Field(
        default=None,
        description="Secret key for token generation (auto-generated if not set)"
    )
    rate_limit_per_minute: int = Field(
        default=60,
        description="API rate limit per minute per client"
    )

    # Feature flags
    enable_analytics: bool = Field(default=True, description="Enable analytics endpoints")
    enable_alerts: bool = Field(default=True, description="Enable alert system")
    enable_reports: bool = Field(default=True, description="Enable report generation")

    @property
    def workspace_path(self) -> Path:
        """Get the workspace root directory."""
        return Path(__file__).parent.parent.parent

    @property
    def db_path_absolute(self) -> Path:
        """Get absolute path to database file."""
        db_path = Path(self.database_path)
        if db_path.is_absolute():
            return db_path
        return self.workspace_path / db_path

    @property
    def migrations_path(self) -> Path:
        """Get path to database migrations directory."""
        return self.workspace_path / "db" / "migrations"

    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.debug

    def is_production(self) -> bool:
        """Check if running in production mode."""
        return not self.debug


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance.

    Returns:
        Settings object with current configuration.
    """
    return settings


def reload_settings() -> Settings:
    """Reload settings from environment.

    Useful for testing or dynamic configuration updates.

    Returns:
        New Settings instance with refreshed configuration.
    """
    global settings
    settings = Settings()
    return settings

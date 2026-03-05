"""Logging configuration for TSM.

Provides centralized logging setup with appropriate formatters and handlers.
"""

import logging
import sys
from logging.config import dictConfig
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_format: Optional[str] = None,
    enable_console: bool = True,
    log_file: Optional[str] = None,
) -> None:
    """Configure logging for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_format: Custom log format string. Uses default if not provided.
        enable_console: Enable console output handler.
        log_file: Path to log file. If None, no file handler is added.
    """
    if log_format is None:
        log_format = (
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        )

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": log_format,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": (
                    "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | "
                    "%(funcName)s | %(message)s"
                ),
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": level,
                "stream": sys.stdout,
            } if enable_console else None,
        },
        "root": {
            "level": level,
            "handlers": ["console"] if enable_console else [],
        },
        "loggers": {
            "tsm": {
                "level": level,
                "handlers": ["console"] if enable_console else [],
                "propagate": False,
            },
        },
    }

    # Add file handler if specified
    if log_file:
        config["handlers"]["file"] = {  # type: ignore[assignment]
            "class": "logging.FileHandler",
            "formatter": "detailed",
            "level": level,
            "filename": log_file,
            "mode": "a",
            "encoding": "utf-8",
        }
        config["root"]["handlers"].append("file")  # type: ignore[union-attr]
        config["loggers"]["tsm"]["handlers"].append("file")  # type: ignore[union-attr]

    # Remove None handlers (when console is disabled)
    config["handlers"] = {k: v for k, v in config["handlers"].items() if v is not None}  # type: ignore[assignment]

    dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name.

    Args:
        name: Logger name (typically __name__).

    Returns:
        Configured logger instance.
    """
    return logging.getLogger(f"tsm.{name}")

"""Tests for the configuration module."""

import os
from pathlib import Path

import pytest

from tsm.config import Settings, get_settings, reload_settings


def test_settings_default_values():
    """Test that settings have correct default values."""
    settings = Settings()
    assert settings.app_name == "TSM"
    assert settings.version == "0.2.0"
    assert settings.debug is False
    assert settings.database_path == "tsm.db"


def test_settings_from_env(monkeypatch):
    """Test that settings can be overridden by environment variables."""
    monkeypatch.setenv("TSM_DEBUG", "true")
    monkeypatch.setenv("TSM_APP_NAME", "TestApp")
    
    settings = Settings()
    assert settings.debug is True
    assert settings.app_name == "TestApp"


def test_workspace_path():
    """Test that workspace path is correctly calculated."""
    settings = Settings()
    expected_path = Path(__file__).parent.parent.parent
    assert settings.workspace_path == expected_path


def test_get_settings():
    """Test the get_settings function returns the global instance."""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2


def test_reload_settings():
    """Test that reload_settings creates a new instance."""
    original = get_settings()
    reloaded = reload_settings()
    assert original is not reloaded
"""Tests for the main application module."""

import pytest
from fastapi.testclient import TestClient

from tsm.main import app


def test_health_check():
    """Test the health check endpoint."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_app_info():
    """Test that the app has correct metadata."""
    assert app.title == "TSM - Tobacco Situation Monitor"
    assert "OSINT-powered surveillance system" in app.description
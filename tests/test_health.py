"""Health check endpoint tests."""

import pytest
from fastapi.testclient import TestClient

from tsm.main import app

client = TestClient(app)


def test_health_check():
    """Test the health check endpoint returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "version": "0.1.0"}
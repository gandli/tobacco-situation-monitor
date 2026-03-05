"""Test dashboard API endpoints."""

import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from tsm.db import init_db


@pytest.fixture
def test_db():
    """Create a temporary test database."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        conn = sqlite3.connect(str(db_path))
        init_db(conn)
        conn.close()
        yield str(db_path)


@pytest.fixture
def client(test_db):
    """Create a test client with a temporary database."""
    with patch('tsm.services.source_manager.DB_PATH', test_db), \
         patch('tsm.services.review_service.DB_PATH', test_db), \
         patch('tsm.api.dashboard.DB_PATH', test_db), \
         patch('tsm.api.intels.DB_PATH', test_db):
        from tsm.main import app
        with TestClient(app) as c:
            yield c


def test_dashboard_summary_contains_counts(client):
    """Test that dashboard summary returns required count fields."""
    resp = client.get("/api/dashboard/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert "today_new" in data
    assert "high_risk" in data
    assert "by_region" in data
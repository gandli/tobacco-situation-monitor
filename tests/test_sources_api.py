"""Test sources API endpoints."""

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
    # Patch the DB_PATH in source_manager to use test database
    with patch('tsm.services.source_manager.DB_PATH', test_db):
        from tsm.main import app
        with TestClient(app) as c:
            yield c


def test_create_source(client):
    """Test creating a new source via API."""
    resp = client.post("/api/sources", json={"name": "Fujian Tobacco", "list_url": "https://example.com/list"})
    assert resp.status_code == 201
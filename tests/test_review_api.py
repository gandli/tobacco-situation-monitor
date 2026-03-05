"""Test review API endpoints."""

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
         patch('tsm.services.review_service.DB_PATH', test_db):
        from tsm.main import app
        with TestClient(app) as c:
            yield c


@pytest.fixture
def seeded_intel_id(test_db):
    """Create a test intel record and return its ID."""
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    
    # Create a source first
    cursor.execute(
        "INSERT INTO sources (name, list_url) VALUES (?, ?)",
        ("Test Source", "https://example.com/list")
    )
    source_id = cursor.lastrowid
    
    # Create a raw article
    cursor.execute(
        "INSERT INTO raw_articles (source_id, url, title) VALUES (?, ?, ?)",
        (source_id, "https://example.com/article/1", "Test Article")
    )
    article_id = cursor.lastrowid
    
    # Create a case intel
    cursor.execute(
        "INSERT INTO case_intels (article_id, is_case_related, case_type, status) VALUES (?, ?, ?, ?)",
        (article_id, 1, "counterfeit", "new")
    )
    intel_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return intel_id


def test_submit_review_action(client, seeded_intel_id):
    """Test submitting a review action for an intel."""
    resp = client.post(
        f"/api/intels/{seeded_intel_id}/review",
        json={"action": "confirm", "comment": "确认有效"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["intel_id"] == seeded_intel_id
    assert data["action"] == "confirm"
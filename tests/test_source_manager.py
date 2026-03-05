"""Tests for source management service."""

import os
import sqlite3
import tempfile
from pathlib import Path

import pytest
from tsm.db import init_db
from tsm.services.source_manager import (
    SourceCreate,
    create_source,
    get_db_connection,
    validate_url,
)


def setup_test_db():
    """Create a temporary test database with schema."""
    db_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    db_path = db_file.name
    db_file.close()

    conn = sqlite3.connect(db_path)
    init_db(conn)
    conn.close()

    return db_path


def teardown_test_db(db_path):
    """Clean up test database."""
    if os.path.exists(db_path):
        os.unlink(db_path)


def test_validate_url():
    """Test URL validation."""
    # Valid URLs
    assert validate_url("https://example.com") is True
    assert validate_url("http://example.com/path") is True
    assert validate_url("https://sub.example.com:8080/path?query=1") is True

    # Invalid URLs
    assert validate_url("not-a-url") is False
    assert validate_url("ftp://example.com") is False  # Only HTTP/HTTPS allowed
    assert validate_url("") is False
    assert validate_url(None) is False


def test_create_source_success():
    """Test successful source creation."""
    db_path = setup_test_db()
    try:
        payload = SourceCreate(name="Test Source", list_url="https://example.com")
        source = create_source(payload, db_path=db_path)

        assert source.id == 1
        assert source.name == "Test Source"
        assert source.list_url == "https://example.com"
        assert source.created_at is not None
        assert source.updated_at is not None
    finally:
        teardown_test_db(db_path)


def test_create_source_invalid_url():
    """Test source creation with invalid URL."""
    db_path = setup_test_db()
    try:
        payload = SourceCreate(name="Bad Source", list_url="not-a-url")
        with pytest.raises(ValueError, match="Invalid URL format"):
            create_source(payload, db_path=db_path)
    finally:
        teardown_test_db(db_path)


def test_create_source_duplicate_url():
    """Test source creation with duplicate URL."""
    db_path = setup_test_db()
    try:
        # Create first source
        payload1 = SourceCreate(name="Source 1", list_url="https://example.com")
        create_source(payload1, db_path=db_path)

        # Try to create second source with same URL
        payload2 = SourceCreate(name="Source 2", list_url="https://example.com")
        with pytest.raises(sqlite3.IntegrityError):
            create_source(payload2, db_path=db_path)
    finally:
        teardown_test_db(db_path)


def test_get_db_connection():
    """Test database connection utility."""
    db_path = setup_test_db()
    try:
        conn = get_db_connection(db_path)
        assert conn is not None
        assert isinstance(conn, sqlite3.Connection)
        conn.close()
    finally:
        teardown_test_db(db_path)


def test_get_db_connection_file_not_found():
    """Test database connection with non-existent file."""
    with pytest.raises(FileNotFoundError):
        get_db_connection("/non/existent/path.db")
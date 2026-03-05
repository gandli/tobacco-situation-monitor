"""Test database schema for required tables."""

import sqlite3
import tempfile
from pathlib import Path

from tsm.db import init_db, list_tables


def test_required_tables_exist():
    """Test that all required tables are created by the init migration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        conn = sqlite3.connect(str(db_path))
        
        # Initialize the database with our schema
        init_db(conn)
        
        # Check that all required tables exist
        expected = {"sources", "raw_articles", "case_intels", "alerts", "review_logs"}
        found = set(list_tables(conn))
        
        conn.close()
        
        assert expected.issubset(found), f"Missing tables: {expected - found}"
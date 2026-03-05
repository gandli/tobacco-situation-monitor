"""Database utilities for TSM."""

import logging
import sqlite3
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def init_db(conn: sqlite3.Connection) -> None:
    """Initialize the database with the v0.1 schema."""
    try:
        migration_path = Path(__file__).parent.parent.parent / "db" / "migrations" / "001_init.sql"
        with open(migration_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        conn.executescript(schema_sql)
        conn.commit()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def list_tables(conn: sqlite3.Connection) -> list[str]:
    """List all table names in the database."""
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    return [row[0] for row in cursor.fetchall()]


def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Get a database connection with proper configuration."""
    if db_path is None:
        from tsm.config import settings
        db_path = settings.database_url.replace("sqlite:///", "")
    
    conn = sqlite3.connect(db_path)
    # Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
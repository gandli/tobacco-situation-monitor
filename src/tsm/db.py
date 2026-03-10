"""Database utilities for TSM."""

import sqlite3
from pathlib import Path

from .config import settings


def get_db_path() -> str:
    """Get the configured database path.
    
    Returns:
        The filesystem path to the SQLite database.
        
    Raises:
        ValueError: If database_url is not a valid SQLite URL.
    """
    url = settings.database_url
    if not url.startswith("sqlite:///"):
        raise ValueError(
            f"Invalid database URL scheme: {url}. "
            "Expected 'sqlite:///' prefix for SQLite databases."
        )
    return url[len("sqlite:///"):]


def init_db(conn: sqlite3.Connection) -> None:
    """Initialize the database with the v0.1 schema."""
    migration_path = Path(__file__).parent.parent.parent / "db" / "migrations" / "001_init.sql"
    with open(migration_path, "r") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.commit()


def list_tables(conn: sqlite3.Connection) -> list[str]:
    """List all table names in the database."""
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    return [row[0] for row in cursor.fetchall()]

"""Database connection management for TSM.

Provides context managers and connection pooling for database operations.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

from tsm.exceptions import DatabaseError


# Default database path
DEFAULT_DB_PATH: str = "tsm.db"


@contextmanager
def get_db_connection(
    db_path: Optional[str] = None,
    timeout: float = 5.0,
) -> Generator[sqlite3.Connection, None, None]:
    """Get a database connection with proper error handling.

    Usage:
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT * FROM table")

    Args:
        db_path: Path to database file. Uses DEFAULT_DB_PATH if not provided.
        timeout: Connection timeout in seconds.

    Yields:
        SQLite connection object.

    Raises:
        DatabaseError: If connection fails.
    """
    db = db_path or DEFAULT_DB_PATH
    conn = None
    try:
        conn = sqlite3.connect(db, timeout=timeout)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        yield conn
    except sqlite3.Error as e:
        raise DatabaseError(f"Database connection failed: {e}") from e
    finally:
        if conn:
            conn.close()


@contextmanager
def transaction(
    db_path: Optional[str] = None,
) -> Generator[sqlite3.Connection, None, None]:
    """Get a database connection with automatic transaction management.

    Usage:
        with transaction() as conn:
            conn.execute("INSERT INTO table VALUES (...)")
            # Commits automatically on success
            # Rolls back on exception

    Args:
        db_path: Path to database file. Uses DEFAULT_DB_PATH if not provided.

    Yields:
        SQLite connection object within a transaction.

    Raises:
        DatabaseError: If database operation fails.
    """
    with get_db_connection(db_path) as conn:
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise DatabaseError(f"Transaction failed: {e}") from e


def init_db(conn: Optional[sqlite3.Connection] = None, db_path: Optional[str] = None) -> None:
    """Initialize the database with the schema.

    Args:
        conn: Existing connection (optional). Creates new connection if not provided.
        db_path: Database path (only used if conn is not provided).

    Raises:
        DatabaseError: If initialization fails.
    """
    should_close = False
    if conn is None:
        conn = sqlite3.connect(db_path or DEFAULT_DB_PATH)
        should_close = True

    try:
        migration_path = Path(__file__).parent.parent.parent / "db" / "migrations" / "001_init.sql"
        if not migration_path.exists():
            raise DatabaseError(f"Migration file not found: {migration_path}")

        with open(migration_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        conn.executescript(schema_sql)
        conn.commit()
    except sqlite3.Error as e:
        raise DatabaseError(f"Database initialization failed: {e}") from e
    finally:
        if should_close and conn:
            conn.close()


def list_tables(conn: sqlite3.Connection) -> list[str]:
    """List all table names in the database.

    Args:
        conn: Database connection.

    Returns:
        List of table names.

    Raises:
        DatabaseError: If query fails.
    """
    try:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        return [row[0] for row in cursor.fetchall()]
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to list tables: {e}") from e


def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    """Check if a table exists in the database.

    Args:
        conn: Database connection.
        table_name: Name of table to check.

    Returns:
        True if table exists, False otherwise.

    Raises:
        DatabaseError: If query fails.
    """
    try:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        return cursor.fetchone() is not None
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to check table existence: {e}") from e

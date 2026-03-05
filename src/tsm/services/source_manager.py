"""Source management service."""

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

# Default database path, can be overridden for testing
DB_PATH: str = "tsm.db"


@dataclass
class Source:
    """Represents a source entity."""
    id: int
    name: str
    list_url: str
    last_crawled_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class SourceCreate:
    """Payload for creating a new source."""
    name: str
    list_url: str


def create_source(payload: SourceCreate, db_path: Optional[str] = None) -> Source:
    """Create a new source in the database."""
    db = db_path or DB_PATH
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute(
        "INSERT INTO sources (name, list_url, created_at, updated_at) VALUES (?, ?, ?, ?)",
        (payload.name, payload.list_url, now, now)
    )
    source_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return Source(
        id=source_id,
        name=payload.name,
        list_url=payload.list_url,
        created_at=now,
        updated_at=now
    )
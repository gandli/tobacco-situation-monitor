"""Review service for case intel review actions."""

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

# Default database path, can be overridden for testing
DB_PATH: str = "tsm.db"


@dataclass
class ReviewIn:
    """Payload for submitting a review."""
    action: str
    comment: Optional[str] = None


@dataclass
class ReviewLog:
    """Represents a review log entry."""
    id: int
    intel_id: int
    action: str
    comment: Optional[str]
    reviewed_at: str
    created_at: str


def submit_review(intel_id: int, payload: ReviewIn, db_path: Optional[str] = None) -> ReviewLog:
    """Submit a review action for an intel record."""
    db = db_path or DB_PATH
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    
    now = datetime.now(timezone.utc).isoformat()
    
    # Insert review log
    cursor.execute(
        "INSERT INTO review_logs (intel_id, action, comment, reviewed_at, created_at) VALUES (?, ?, ?, ?, ?)",
        (intel_id, payload.action, payload.comment, now, now)
    )
    review_id = cursor.lastrowid
    
    # Update intel status based on action
    new_status = "confirmed" if payload.action == "confirm" else payload.action
    cursor.execute(
        "UPDATE case_intels SET status = ?, updated_at = ? WHERE id = ?",
        (new_status, now, intel_id)
    )
    
    conn.commit()
    conn.close()
    
    return ReviewLog(
        id=review_id,
        intel_id=intel_id,
        action=payload.action,
        comment=payload.comment,
        reviewed_at=now,
        created_at=now
    )
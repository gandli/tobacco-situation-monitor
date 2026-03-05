"""Dashboard API endpoints."""

import sqlite3
from datetime import date
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends

router = APIRouter()

# Default database path, can be overridden for testing
DB_PATH: str = "tsm.db"


def get_db_path() -> Optional[str]:
    """Get the database path (can be overridden in tests)."""
    return None


@router.get("/api/dashboard/summary")
def summary(db_path: Optional[str] = Depends(get_db_path)) -> Dict[str, Any]:
    """Get dashboard summary with counts."""
    db = db_path or DB_PATH
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    today = date.today().isoformat()

    # Count today's new intels
    cursor.execute(
        "SELECT COUNT(*) FROM case_intels WHERE date(created_at) = ?",
        (today,)
    )
    today_new = cursor.fetchone()[0]

    # Count high risk intels
    cursor.execute(
        "SELECT COUNT(*) FROM case_intels WHERE risk_level = 'high'"
    )
    high_risk = cursor.fetchone()[0]

    # Count by region
    cursor.execute(
        "SELECT region, COUNT(*) as cnt FROM case_intels WHERE region IS NOT NULL GROUP BY region ORDER BY cnt DESC LIMIT 10"
    )
    by_region = [{"region": row[0], "count": row[1]} for row in cursor.fetchall()]

    conn.close()

    return {
        "today_new": today_new,
        "high_risk": high_risk,
        "by_region": by_region
    }
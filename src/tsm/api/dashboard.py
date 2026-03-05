"""Dashboard API endpoints for TSM.

Provides both summary statistics and KPI metrics for OSINT effectiveness monitoring.

KPI Definitions (V0.1):
- coverage_rate (覆盖率): % of sources successfully crawled
- timeliness_score (时效性): Avg hours from article publish to collection
- accuracy_rate (识别准确率): % of confirmed intels / total reviewed
- noise_rate (噪音率): % of dismissed intels / total reviewed
- reviewable_rate (可复核率): % of intels with review logs
"""

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


@router.get("/api/dashboard/kpi")
def kpi(db_path: Optional[str] = Depends(get_db_path)) -> Dict[str, Any]:
    """Get OSINT effectiveness KPIs.
    
    Returns:
        Dict with 5 KPIs:
        - coverage_rate: % of sources successfully crawled
        - timeliness_score: Avg hours from publish to collection
        - accuracy_rate: % of confirmed intels / total reviewed
        - noise_rate: % of dismissed intels / total reviewed
        - reviewable_rate: % of intels with review logs
    """
    db = db_path or DB_PATH
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    # 1. Coverage Rate: % of sources with last_crawled_at not NULL
    cursor.execute("SELECT COUNT(*) FROM sources")
    total_sources = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM sources WHERE last_crawled_at IS NOT NULL")
    crawled_sources = cursor.fetchone()[0]
    
    coverage_pct = (crawled_sources / total_sources * 100) if total_sources > 0 else 0

    # 2. Timeliness Score: Avg hours between published_at and fetched_at
    cursor.execute("""
        SELECT AVG((julianday(fetched_at) - julianday(published_at)) * 24)
        FROM raw_articles
        WHERE published_at IS NOT NULL 
          AND fetched_at IS NOT NULL
          AND published_at <= fetched_at
    """)
    result = cursor.fetchone()[0]
    avg_hours = round(result, 2) if result is not None else None

    # 3 & 4. Accuracy and Noise rates from review status
    cursor.execute("""
        SELECT status, COUNT(*) 
        FROM case_intels 
        WHERE status IN ('confirmed', 'dismissed')
        GROUP BY status
    """)
    status_counts = dict(cursor.fetchall())
    confirmed_count = status_counts.get('confirmed', 0)
    dismissed_count = status_counts.get('dismissed', 0)
    total_reviewed = confirmed_count + dismissed_count

    accuracy_pct = (confirmed_count / total_reviewed * 100) if total_reviewed > 0 else 0
    noise_pct = (dismissed_count / total_reviewed * 100) if total_reviewed > 0 else 0

    # 5. Reviewable Rate: % of intels with at least one review log
    cursor.execute("SELECT COUNT(*) FROM case_intels")
    total_intels = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(DISTINCT intel_id) 
        FROM review_logs
    """)
    reviewed_intels = cursor.fetchone()[0]

    reviewable_pct = (reviewed_intels / total_intels * 100) if total_intels > 0 else 0

    conn.close()

    return {
        "coverage_rate": {
            "value": crawled_sources,
            "total": total_sources,
            "percentage": round(coverage_pct, 2),
            "description": f"{crawled_sources}/{total_sources} sources successfully crawled"
        },
        "timeliness_score": {
            "value": avg_hours,
            "avg_hours": avg_hours,
            "description": f"Average {avg_hours:.1f} hours from publish to collection" if avg_hours else "No articles with publish timestamps"
        },
        "accuracy_rate": {
            "value": confirmed_count,
            "total": total_reviewed,
            "percentage": round(accuracy_pct, 2),
            "description": f"{confirmed_count}/{total_reviewed} reviewed intels confirmed as valid cases"
        },
        "noise_rate": {
            "value": dismissed_count,
            "total": total_reviewed,
            "percentage": round(noise_pct, 2),
            "description": f"{dismissed_count}/{total_reviewed} reviewed intels dismissed as noise"
        },
        "reviewable_rate": {
            "value": reviewed_intels,
            "total": total_intels,
            "percentage": round(reviewable_pct, 2),
            "description": f"{reviewed_intels}/{total_intels} intels have review logs"
        }
    }
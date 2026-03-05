"""Alerts API endpoints for TSM.

Provides endpoints for managing and querying alerts generated
by the alert rules engine.
"""

import sqlite3
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()

# Default database path, can be overridden for testing
DB_PATH: str = "tsm.db"


def get_db_path() -> Optional[str]:
    """Get the database path (can be overridden in tests)."""
    return None


class AlertResponse(BaseModel):
    """Schema for alert response."""
    id: int
    intel_id: int
    rule_name: Optional[str] = None
    alert_type: Optional[str] = None
    severity: str = "warning"
    title: Optional[str] = None
    message: Optional[str] = None
    is_sent: bool = False
    sent_at: Optional[str] = None
    created_at: str


class AlertListResponse(BaseModel):
    """Schema for alert list response."""
    items: List[AlertResponse]
    total: int


class AlertStatsResponse(BaseModel):
    """Schema for alert statistics."""
    total_alerts: int
    by_severity: Dict[str, int]
    by_type: Dict[str, int]
    unsent_count: int


@router.get("/api/alerts", response_model=AlertListResponse)
def list_alerts(
    severity: Optional[str] = Query(None, pattern="^(info|warning|critical)$"),
    alert_type: Optional[str] = None,
    is_sent: Optional[bool] = None,
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db_path: Optional[str] = Depends(get_db_path)
) -> AlertListResponse:
    """Query alerts with optional filters.

    Args:
        severity: Filter by severity (info, warning, critical).
        alert_type: Filter by alert type.
        is_sent: Filter by sent status.
        days: Number of days to look back (1-30).
        limit: Results per page (1-200).
        offset: Pagination offset.
        db_path: Database path override.

    Returns:
        AlertListResponse with filtered alerts.
    """
    db = db_path or DB_PATH
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    # Build query with filters
    conditions = ["date(created_at) >= date('now', ? || ' days')"]
    params = [f"-{days}"]

    if severity:
        conditions.append("severity = ?")
        params.append(severity)
    if alert_type:
        conditions.append("alert_type = ?")
        params.append(alert_type)
    if is_sent is not None:
        conditions.append("is_sent = ?")
        params.append(1 if is_sent else 0)

    where_clause = " AND ".join(conditions)

    # Get total count
    cursor.execute(f"SELECT COUNT(*) FROM alerts WHERE {where_clause}", params)
    total = cursor.fetchone()[0]

    # Get items
    cursor.execute(
        f"""SELECT id, intel_id, rule_name, alert_type, severity, title, message, 
                   is_sent, sent_at, created_at
            FROM alerts 
            WHERE {where_clause}
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?""",
        params + [limit, offset]
    )
    rows = cursor.fetchall()
    conn.close()

    items = [
        AlertResponse(
            id=row[0],
            intel_id=row[1],
            rule_name=row[2],
            alert_type=row[3],
            severity=row[4] or "warning",
            title=row[5],
            message=row[6],
            is_sent=bool(row[7]),
            sent_at=row[8],
            created_at=row[9]
        )
        for row in rows
    ]

    return AlertListResponse(items=items, total=total)


@router.get("/api/alerts/{alert_id}", response_model=AlertResponse)
def get_alert(
    alert_id: int,
    db_path: Optional[str] = Depends(get_db_path)
) -> AlertResponse:
    """Get a single alert by ID.

    Args:
        alert_id: Alert ID.
        db_path: Database path override.

    Returns:
        AlertResponse with alert details.
    """
    db = db_path or DB_PATH
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.execute(
        """SELECT id, intel_id, rule_name, alert_type, severity, title, message,
                  is_sent, sent_at, created_at
           FROM alerts WHERE id = ?""",
        (alert_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Alert not found")

    return AlertResponse(
        id=row[0],
        intel_id=row[1],
        rule_name=row[2],
        alert_type=row[3],
        severity=row[4] or "warning",
        title=row[5],
        message=row[6],
        is_sent=bool(row[7]),
        sent_at=row[8],
        created_at=row[9]
    )


@router.post("/api/alerts/{alert_id}/send")
def mark_alert_sent(
    alert_id: int,
    db_path: Optional[str] = Depends(get_db_path)
) -> Dict[str, Any]:
    """Mark an alert as sent/notified.

    Args:
        alert_id: Alert ID.
        db_path: Database path override.

    Returns:
        Success message.
    """
    db = db_path or DB_PATH
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM alerts WHERE id = ?", (alert_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Alert not found")

    now = datetime.now(timezone.utc).isoformat()
    cursor.execute(
        "UPDATE alerts SET is_sent = 1, sent_at = ? WHERE id = ?",
        (now, alert_id)
    )
    conn.commit()
    conn.close()

    return {"status": "ok", "message": f"Alert {alert_id} marked as sent"}


@router.get("/api/alerts/stats", response_model=AlertStatsResponse)
def alert_stats(
    days: int = Query(7, ge=1, le=30),
    db_path: Optional[str] = Depends(get_db_path)
) -> AlertStatsResponse:
    """Get alert statistics.

    Args:
        days: Number of days to analyze (1-30).
        db_path: Database path override.

    Returns:
        AlertStatsResponse with statistics.
    """
    db = db_path or DB_PATH
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    # Total alerts in period
    cursor.execute(
        "SELECT COUNT(*) FROM alerts WHERE date(created_at) >= date('now', ? || ' days')",
        (f"-{days}",)
    )
    total_alerts = cursor.fetchone()[0]

    # By severity
    cursor.execute(
        """SELECT COALESCE(severity, 'warning'), COUNT(*) 
           FROM alerts 
           WHERE date(created_at) >= date('now', ? || ' days')
           GROUP BY severity""",
        (f"-{days}",)
    )
    by_severity = {row[0]: row[1] for row in cursor.fetchall()}

    # By type
    cursor.execute(
        """SELECT alert_type, COUNT(*) 
           FROM alerts 
           WHERE date(created_at) >= date('now', ? || ' days')
             AND alert_type IS NOT NULL
           GROUP BY alert_type""",
        (f"-{days}",)
    )
    by_type = {row[0]: row[1] for row in cursor.fetchall()}

    # Unsent count
    cursor.execute(
        """SELECT COUNT(*) 
           FROM alerts 
           WHERE date(created_at) >= date('now', ? || ' days')
             AND is_sent = 0""",
        (f"-{days}",)
    )
    unsent_count = cursor.fetchone()[0]

    conn.close()

    return AlertStatsResponse(
        total_alerts=total_alerts,
        by_severity=by_severity,
        by_type=by_type,
        unsent_count=unsent_count
    )


@router.get("/api/alerts/critical")
def list_critical_alerts(
    limit: int = Query(20, ge=1, le=50),
    db_path: Optional[str] = Depends(get_db_path)
) -> AlertListResponse:
    """Get critical alerts requiring immediate attention.

    Args:
        limit: Maximum results (1-50).
        db_path: Database path override.

    Returns:
        AlertListResponse with critical alerts.
    """
    db = db_path or DB_PATH
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    # Get critical alerts from last 24 hours
    cursor.execute(
        """SELECT id, intel_id, rule_name, alert_type, severity, title, message,
                  is_sent, sent_at, created_at
           FROM alerts 
           WHERE severity = 'critical'
             AND date(created_at) >= date('now', '-1 day')
           ORDER BY created_at DESC 
           LIMIT ?""",
        (limit,)
    )
    rows = cursor.fetchall()

    # Get total
    cursor.execute(
        "SELECT COUNT(*) FROM alerts WHERE severity = 'critical' AND date(created_at) >= date('now', '-1 day')"
    )
    total = cursor.fetchone()[0]

    conn.close()

    items = [
        AlertResponse(
            id=row[0],
            intel_id=row[1],
            rule_name=row[2],
            alert_type=row[3],
            severity=row[4] or "warning",
            title=row[5],
            message=row[6],
            is_sent=bool(row[7]),
            sent_at=row[8],
            created_at=row[9]
        )
        for row in rows
    ]

    return AlertListResponse(items=items, total=total)
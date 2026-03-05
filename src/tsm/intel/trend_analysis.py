"""Trend analysis module for tobacco case intelligence.

This module provides trend analysis capabilities including:
- Time-based trend analysis (daily, weekly, monthly)
- Case type distribution trends
- Regional distribution trends
- Risk level trends over time
"""

import sqlite3
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class TimeGranularity(str, Enum):
    """Time granularity for trend analysis."""
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


@dataclass
class TrendPoint:
    """Single point in a trend series."""
    time: str  # ISO date or date range
    value: int
    label: str  # Human-readable label


@dataclass
class TrendSeries:
    """A series of trend points."""
    name: str
    points: List[TrendPoint] = field(default_factory=list)
    total: int = 0
    average: float = 0.0
    trend_direction: str = "stable"  # "up", "down", "stable"


@dataclass
class TrendAnalysis:
    """Complete trend analysis result."""
    period_start: str
    period_end: str
    granularity: TimeGranularity
    by_time: TrendSeries
    by_case_type: List[TrendSeries] = field(default_factory=list)
    by_risk_level: List[TrendSeries] = field(default_factory=list)
    by_region: List[TrendSeries] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)


# Default database path
DB_PATH: str = "tsm.db"


def analyze_trends(
    days: int = 30,
    granularity: TimeGranularity = TimeGranularity.DAY,
    db_path: Optional[str] = None
) -> TrendAnalysis:
    """Analyze trends over a time period.

    Args:
        days: Number of days to analyze (from today backwards).
        granularity: Time granularity for grouping.
        db_path: Optional database path override.

    Returns:
        TrendAnalysis with all trend data.
    """
    db = db_path or DB_PATH
    conn = sqlite3.connect(db)

    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    # Get time-based trends
    by_time = _get_time_trend(conn, start_date, end_date, granularity)

    # Get case type distribution
    by_case_type = _get_case_type_trends(conn, start_date, end_date)

    # Get risk level distribution
    by_risk_level = _get_risk_level_trends(conn, start_date, end_date)

    # Get regional distribution
    by_region = _get_region_trends(conn, start_date, end_date)

    # Calculate summary
    summary = _calculate_summary(conn, start_date, end_date, by_time)

    conn.close()

    return TrendAnalysis(
        period_start=start_date.isoformat(),
        period_end=end_date.isoformat(),
        granularity=granularity,
        by_time=by_time,
        by_case_type=by_case_type,
        by_risk_level=by_risk_level,
        by_region=by_region,
        summary=summary
    )


def _get_time_trend(
    conn: sqlite3.Connection,
    start_date: date,
    end_date: date,
    granularity: TimeGranularity
) -> TrendSeries:
    """Get trend by time period."""
    cursor = conn.cursor()

    if granularity == TimeGranularity.DAY:
        query = """
            SELECT date(created_at) as period, COUNT(*) as cnt
            FROM case_intels
            WHERE date(created_at) BETWEEN ? AND ?
            GROUP BY date(created_at)
            ORDER BY period
        """
        cursor.execute(query, (start_date.isoformat(), end_date.isoformat()))
        results = cursor.fetchall()

        points = [
            TrendPoint(time=row[0], value=row[1], label=row[0])
            for row in results
        ]

    elif granularity == TimeGranularity.WEEK:
        query = """
            SELECT strftime('%Y-%W', created_at) as period,
                   date(created_at, 'weekday 0', '-6 days') as week_start,
                   COUNT(*) as cnt
            FROM case_intels
            WHERE date(created_at) BETWEEN ? AND ?
            GROUP BY strftime('%Y-%W', created_at)
            ORDER BY period
        """
        cursor.execute(query, (start_date.isoformat(), end_date.isoformat()))
        results = cursor.fetchall()

        points = [
            TrendPoint(time=row[0], value=row[2], label=f"Week of {row[1]}")
            for row in results
        ]

    else:  # MONTH
        query = """
            SELECT strftime('%Y-%m', created_at) as period, COUNT(*) as cnt
            FROM case_intels
            WHERE date(created_at) BETWEEN ? AND ?
            GROUP BY strftime('%Y-%m', created_at)
            ORDER BY period
        """
        cursor.execute(query, (start_date.isoformat(), end_date.isoformat()))
        results = cursor.fetchall()

        points = [
            TrendPoint(time=row[0], value=row[1], label=row[0])
            for row in results
        ]

    total = sum(p.value for p in points)
    average = total / len(points) if points else 0

    # Determine trend direction
    trend_direction = "stable"
    if len(points) >= 2:
        first_half = sum(p.value for p in points[:len(points)//2])
        second_half = sum(p.value for p in points[len(points)//2:])
        if second_half > first_half * 1.2:
            trend_direction = "up"
        elif second_half < first_half * 0.8:
            trend_direction = "down"

    return TrendSeries(
        name="cases_over_time",
        points=points,
        total=total,
        average=round(average, 2),
        trend_direction=trend_direction
    )


def _get_case_type_trends(
    conn: sqlite3.Connection,
    start_date: date,
    end_date: date
) -> List[TrendSeries]:
    """Get trends by case type."""
    cursor = conn.cursor()

    query = """
        SELECT case_type, COUNT(*) as cnt
        FROM case_intels
        WHERE date(created_at) BETWEEN ? AND ?
          AND case_type IS NOT NULL
        GROUP BY case_type
        ORDER BY cnt DESC
    """
    cursor.execute(query, (start_date.isoformat(), end_date.isoformat()))
    results = cursor.fetchall()

    series_list = []
    for case_type, count in results:
        # Get daily breakdown for this case type
        cursor.execute("""
            SELECT date(created_at) as day, COUNT(*) as cnt
            FROM case_intels
            WHERE date(created_at) BETWEEN ? AND ?
              AND case_type = ?
            GROUP BY date(created_at)
            ORDER BY day
        """, (start_date.isoformat(), end_date.isoformat(), case_type))

        daily_results = cursor.fetchall()
        points = [
            TrendPoint(time=row[0], value=row[1], label=row[0])
            for row in daily_results
        ]

        series_list.append(TrendSeries(
            name=case_type,
            points=points,
            total=count
        ))

    return series_list


def _get_risk_level_trends(
    conn: sqlite3.Connection,
    start_date: date,
    end_date: date
) -> List[TrendSeries]:
    """Get trends by risk level."""
    cursor = conn.cursor()

    series_list = []
    for level in ["high", "medium", "low"]:
        cursor.execute("""
            SELECT date(created_at) as day, COUNT(*) as cnt
            FROM case_intels
            WHERE date(created_at) BETWEEN ? AND ?
              AND risk_level = ?
            GROUP BY date(created_at)
            ORDER BY day
        """, (start_date.isoformat(), end_date.isoformat(), level))

        results = cursor.fetchall()
        points = [
            TrendPoint(time=row[0], value=row[1], label=row[0])
            for row in results
        ]

        total = sum(p.value for p in points)
        if total > 0:  # Only include if there's data
            series_list.append(TrendSeries(
                name=level,
                points=points,
                total=total
            ))

    return series_list


def _get_region_trends(
    conn: sqlite3.Connection,
    start_date: date,
    end_date: date,
    limit: int = 10
) -> List[TrendSeries]:
    """Get trends by region (top N regions)."""
    cursor = conn.cursor()

    # Get top regions by count
    cursor.execute("""
        SELECT region, COUNT(*) as cnt
        FROM case_intels
        WHERE date(created_at) BETWEEN ? AND ?
          AND region IS NOT NULL
        GROUP BY region
        ORDER BY cnt DESC
        LIMIT ?
    """, (start_date.isoformat(), end_date.isoformat(), limit))

    top_regions = cursor.fetchall()

    series_list = []
    for region, total_count in top_regions:
        # Get daily breakdown for this region
        cursor.execute("""
            SELECT date(created_at) as day, COUNT(*) as cnt
            FROM case_intels
            WHERE date(created_at) BETWEEN ? AND ?
              AND region = ?
            GROUP BY date(created_at)
            ORDER BY day
        """, (start_date.isoformat(), end_date.isoformat(), region))

        results = cursor.fetchall()
        points = [
            TrendPoint(time=row[0], value=row[1], label=row[0])
            for row in results
        ]

        series_list.append(TrendSeries(
            name=region,
            points=points,
            total=total_count
        ))

    return series_list


def _calculate_summary(
    conn: sqlite3.Connection,
    start_date: date,
    end_date: date,
    time_trend: TrendSeries
) -> Dict[str, Any]:
    """Calculate summary statistics."""
    cursor = conn.cursor()

    # Total cases in period
    cursor.execute("""
        SELECT COUNT(*) FROM case_intels
        WHERE date(created_at) BETWEEN ? AND ?
    """, (start_date.isoformat(), end_date.isoformat()))
    total_cases = cursor.fetchone()[0]

    # High risk cases
    cursor.execute("""
        SELECT COUNT(*) FROM case_intels
        WHERE date(created_at) BETWEEN ? AND ?
          AND risk_level = 'high'
    """, (start_date.isoformat(), end_date.isoformat()))
    high_risk_cases = cursor.fetchone()[0]

    # Cases by case type
    cursor.execute("""
        SELECT case_type, COUNT(*) as cnt
        FROM case_intels
        WHERE date(created_at) BETWEEN ? AND ?
          AND case_type IS NOT NULL
        GROUP BY case_type
        ORDER BY cnt DESC
    """, (start_date.isoformat(), end_date.isoformat()))
    case_type_dist = {row[0]: row[1] for row in cursor.fetchall()}

    # Top region
    cursor.execute("""
        SELECT region, COUNT(*) as cnt
        FROM case_intels
        WHERE date(created_at) BETWEEN ? AND ?
          AND region IS NOT NULL
        GROUP BY region
        ORDER BY cnt DESC
        LIMIT 1
    """, (start_date.isoformat(), end_date.isoformat()))
    top_region_row = cursor.fetchone()
    top_region = top_region_row[0] if top_region_row else None

    return {
        "total_cases": total_cases,
        "high_risk_cases": high_risk_cases,
        "high_risk_percentage": round(high_risk_cases / total_cases * 100, 2) if total_cases > 0 else 0,
        "cases_per_day_avg": time_trend.average,
        "trend_direction": time_trend.trend_direction,
        "case_type_distribution": case_type_dist,
        "top_region": top_region,
    }


def get_hotspots(
    days: int = 7,
    threshold: int = 3,
    db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get regional hotspots with case concentration above threshold.

    Args:
        days: Number of days to look back.
        threshold: Minimum cases to be considered a hotspot.
        db_path: Optional database path override.

    Returns:
        List of hotspot dictionaries with region and case count.
    """
    db = db_path or DB_PATH
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    cursor.execute("""
        SELECT region, COUNT(*) as cnt
        FROM case_intels
        WHERE date(created_at) BETWEEN ? AND ?
          AND region IS NOT NULL
        GROUP BY region
        HAVING cnt >= ?
        ORDER BY cnt DESC
    """, (start_date.isoformat(), end_date.isoformat(), threshold))

    results = cursor.fetchall()
    conn.close()

    return [
        {"region": row[0], "count": row[1], "period_days": days}
        for row in results
    ]
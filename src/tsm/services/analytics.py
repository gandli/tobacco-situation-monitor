"""Analytics service for TSM data analysis.

Provides trend analysis, regional distribution, case type breakdown,
and data source effectiveness metrics.
"""

import sqlite3
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional


@dataclass
class TrendPoint:
    """A single point in a time series trend."""
    date: str
    count: int


@dataclass
class TimeSeriesTrend:
    """Time series trend data."""
    period: str  # 'daily', 'weekly', 'monthly'
    metric: str
    data: List[TrendPoint] = field(default_factory=list)
    total: int = 0
    average: float = 0.0


@dataclass
class RegionalDistribution:
    """Regional distribution of cases."""
    region: str
    count: int
    percentage: float
    case_types: Dict[str, int] = field(default_factory=dict)


@dataclass
class CaseTypeBreakdown:
    """Breakdown by case type."""
    case_type: str
    count: int
    percentage: float
    avg_risk_score: float
    by_status: Dict[str, int] = field(default_factory=dict)


@dataclass
class SourceEffectiveness:
    """Effectiveness metrics for a data source."""
    source_id: int
    source_name: str
    articles_collected: int
    intels_generated: int
    conversion_rate: float
    confirmed_count: int
    accuracy_rate: float


@dataclass
class AnalyticsReport:
    """Complete analytics report."""
    report_date: str
    period_start: str
    period_end: str
    total_intels: int
    new_intels: int
    confirmed_intels: int
    dismissed_intels: int
    pending_intels: int
    trend: Optional[TimeSeriesTrend] = None
    regional_distribution: List[RegionalDistribution] = field(default_factory=list)
    case_type_breakdown: List[CaseTypeBreakdown] = field(default_factory=list)
    source_effectiveness: List[SourceEffectiveness] = field(default_factory=list)


# Default database path
DB_PATH: str = "tsm.db"


def get_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    period: str = "daily",
    db_path: Optional[str] = None
) -> AnalyticsReport:
    """Generate comprehensive analytics report.
    
    Args:
        start_date: Start date in YYYY-MM-DD format (default: 30 days ago)
        end_date: End date in YYYY-MM-DD format (default: today)
        period: Trend period ('daily', 'weekly', 'monthly')
        db_path: Database path (uses default if not provided)
    
    Returns:
        AnalyticsReport with all analytics data
    """
    db = db_path or DB_PATH
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Set default date range
    if end_date is None:
        end_date = date.today().isoformat()
    if start_date is None:
        start_date = (date.today() - timedelta(days=30)).isoformat()
    
    # Get basic counts
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN date(created_at) >= ? THEN 1 ELSE 0 END) as new_intels,
            SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) as confirmed,
            SUM(CASE WHEN status = 'dismissed' THEN 1 ELSE 0 END) as dismissed,
            SUM(CASE WHEN status = 'new' OR status IS NULL THEN 1 ELSE 0 END) as pending
        FROM case_intels
    """, (start_date,))
    
    row = cursor.fetchone()
    total_intels = row["total"] or 0
    new_intels = row["new_intels"] or 0
    confirmed_intels = row["confirmed"] or 0
    dismissed_intels = row["dismissed"] or 0
    pending_intels = row["pending"] or 0
    
    # Get trend data
    trend = _get_trend(cursor, start_date, end_date, period)
    
    # Get regional distribution
    regional = _get_regional_distribution(cursor, start_date, end_date)
    
    # Get case type breakdown
    case_types = _get_case_type_breakdown(cursor, start_date, end_date)
    
    # Get source effectiveness
    source_eff = _get_source_effectiveness(cursor, start_date, end_date)
    
    conn.close()
    
    return AnalyticsReport(
        report_date=date.today().isoformat(),
        period_start=start_date,
        period_end=end_date,
        total_intels=total_intels,
        new_intels=new_intels,
        confirmed_intels=confirmed_intels,
        dismissed_intels=dismissed_intels,
        pending_intels=pending_intels,
        trend=trend,
        regional_distribution=regional,
        case_type_breakdown=case_types,
        source_effectiveness=source_eff
    )


def _get_trend(
    cursor: sqlite3.Cursor,
    start_date: str,
    end_date: str,
    period: str
) -> TimeSeriesTrend:
    """Get time series trend data."""
    if period == "daily":
        date_format = "%Y-%m-%d"
        group_by = "date(created_at)"
    elif period == "weekly":
        date_format = "%Y-W%W"
        group_by = "strftime('%Y-W%W', created_at)"
    else:  # monthly
        date_format = "%Y-%m"
        group_by = "strftime('%Y-%m', created_at)"
    
    cursor.execute(f"""
        SELECT {group_by} as period_key, COUNT(*) as count
        FROM case_intels
        WHERE date(created_at) >= ? AND date(created_at) <= ?
        GROUP BY {group_by}
        ORDER BY period_key
    """, (start_date, end_date))
    
    data = []
    total = 0
    for row in cursor.fetchall():
        point = TrendPoint(date=row[0], count=row[1])
        data.append(point)
        total += row[1]
    
    avg = total / len(data) if data else 0.0
    
    return TimeSeriesTrend(
        period=period,
        metric="intels_count",
        data=data,
        total=total,
        average=round(avg, 2)
    )


def _get_regional_distribution(
    cursor: sqlite3.Cursor,
    start_date: str,
    end_date: str
) -> List[RegionalDistribution]:
    """Get regional distribution of cases."""
    # Get total count first for percentage calculation
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM case_intels
        WHERE date(created_at) >= ? AND date(created_at) <= ?
          AND region IS NOT NULL
    """, (start_date, end_date))
    
    total = cursor.fetchone()[0] or 1  # Avoid division by zero
    
    # Get distribution by region
    cursor.execute("""
        SELECT region, COUNT(*) as count
        FROM case_intels
        WHERE date(created_at) >= ? AND date(created_at) <= ?
          AND region IS NOT NULL
        GROUP BY region
        ORDER BY count DESC
        LIMIT 20
    """, (start_date, end_date))
    
    results = []
    for row in cursor.fetchall():
        region, count = row[0], row[1]
        
        # Get case types for this region
        cursor.execute("""
            SELECT case_type, COUNT(*) as cnt
            FROM case_intels
            WHERE region = ? AND case_type IS NOT NULL
              AND date(created_at) >= ? AND date(created_at) <= ?
            GROUP BY case_type
        """, (region, start_date, end_date))
        
        case_types = {r[0]: r[1] for r in cursor.fetchall()}
        
        results.append(RegionalDistribution(
            region=region,
            count=count,
            percentage=round(count / total * 100, 2),
            case_types=case_types
        ))
    
    return results


def _get_case_type_breakdown(
    cursor: sqlite3.Cursor,
    start_date: str,
    end_date: str
) -> List[CaseTypeBreakdown]:
    """Get breakdown by case type."""
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM case_intels
        WHERE date(created_at) >= ? AND date(created_at) <= ?
          AND case_type IS NOT NULL
    """, (start_date, end_date))
    
    total = cursor.fetchone()[0] or 1
    
    cursor.execute("""
        SELECT 
            case_type,
            COUNT(*) as count,
            AVG(risk_score) as avg_score
        FROM case_intels
        WHERE date(created_at) >= ? AND date(created_at) <= ?
          AND case_type IS NOT NULL
        GROUP BY case_type
        ORDER BY count DESC
    """, (start_date, end_date))
    
    results = []
    for row in cursor.fetchall():
        case_type, count, avg_score = row[0], row[1], row[2] or 0
        
        # Get status breakdown for this case type
        cursor.execute("""
            SELECT status, COUNT(*) as cnt
            FROM case_intels
            WHERE case_type = ?
              AND date(created_at) >= ? AND date(created_at) <= ?
            GROUP BY status
        """, (case_type, start_date, end_date))
        
        by_status = {r[0] or 'new': r[1] for r in cursor.fetchall()}
        
        results.append(CaseTypeBreakdown(
            case_type=case_type,
            count=count,
            percentage=round(count / total * 100, 2),
            avg_risk_score=round(avg_score, 2),
            by_status=by_status
        ))
    
    return results


def _get_source_effectiveness(
    cursor: sqlite3.Cursor,
    start_date: str,
    end_date: str
) -> List[SourceEffectiveness]:
    """Get effectiveness metrics for each data source."""
    cursor.execute("""
        SELECT 
            s.id as source_id,
            s.name as source_name,
            COUNT(DISTINCT a.id) as articles_collected,
            COUNT(DISTINCT ci.id) as intels_generated,
            SUM(CASE WHEN ci.status = 'confirmed' THEN 1 ELSE 0 END) as confirmed_count
        FROM sources s
        LEFT JOIN raw_articles a ON s.id = a.source_id
            AND date(a.fetched_at) >= ? AND date(a.fetched_at) <= ?
        LEFT JOIN case_intels ci ON a.id = ci.article_id AND ci.is_case_related = 1
        GROUP BY s.id, s.name
        ORDER BY intels_generated DESC
    """, (start_date, end_date))
    
    results = []
    for row in cursor.fetchall():
        source_id, source_name, articles, intels, confirmed = row
        articles = articles or 0
        intels = intels or 0
        confirmed = confirmed or 0
        
        conversion_rate = (intels / articles * 100) if articles > 0 else 0
        accuracy_rate = (confirmed / intels * 100) if intels > 0 else 0
        
        results.append(SourceEffectiveness(
            source_id=source_id,
            source_name=source_name,
            articles_collected=articles,
            intels_generated=intels,
            conversion_rate=round(conversion_rate, 2),
            confirmed_count=confirmed,
            accuracy_rate=round(accuracy_rate, 2)
        ))
    
    return results


def get_risk_distribution(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """Get distribution of cases by risk level.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        db_path: Database path
    
    Returns:
        Dict with risk level distribution and statistics
    """
    db = db_path or DB_PATH
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    
    if end_date is None:
        end_date = date.today().isoformat()
    if start_date is None:
        start_date = (date.today() - timedelta(days=30)).isoformat()
    
    cursor.execute("""
        SELECT 
            risk_level,
            COUNT(*) as count,
            AVG(risk_score) as avg_score,
            MAX(risk_score) as max_score,
            MIN(risk_score) as min_score
        FROM case_intels
        WHERE date(created_at) >= ? AND date(created_at) <= ?
        GROUP BY risk_level
        ORDER BY 
            CASE risk_level
                WHEN 'high' THEN 1
                WHEN 'medium' THEN 2
                WHEN 'low' THEN 3
                ELSE 4
            END
    """, (start_date, end_date))
    
    distribution = {}
    total = 0
    for row in cursor.fetchall():
        level, count, avg, max_s, min_s = row
        distribution[level or 'unknown'] = {
            "count": count,
            "avg_score": round(avg, 2) if avg else 0,
            "max_score": max_s or 0,
            "min_score": min_s or 0
        }
        total += count
    
    # Add percentages
    for level in distribution:
        distribution[level]["percentage"] = round(
            distribution[level]["count"] / total * 100, 2
        ) if total > 0 else 0
    
    conn.close()
    
    return {
        "period": {"start": start_date, "end": end_date},
        "total": total,
        "distribution": distribution
    }


def get_hourly_pattern(
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """Get pattern of intel creation by hour of day.
    
    Useful for understanding when cases are typically reported/discovered.
    
    Args:
        db_path: Database path
    
    Returns:
        Dict with hourly distribution data
    """
    db = db_path or DB_PATH
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            CAST(strftime('%H', created_at) AS INTEGER) as hour,
            COUNT(*) as count
        FROM case_intels
        GROUP BY hour
        ORDER BY hour
    """)
    
    hourly = {hour: 0 for hour in range(24)}
    total = 0
    for row in cursor.fetchall():
        hour, count = row
        hourly[hour] = count
        total += count
    
    # Find peak hours (top 3)
    sorted_hours = sorted(hourly.items(), key=lambda x: x[1], reverse=True)
    peak_hours = [{"hour": h, "count": c} for h, c in sorted_hours[:3] if c > 0]
    
    conn.close()
    
    return {
        "hourly_distribution": hourly,
        "peak_hours": peak_hours,
        "total_intels": total
    }


def get_weekly_pattern(
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """Get pattern of intel creation by day of week.
    
    Args:
        db_path: Database path
    
    Returns:
        Dict with weekly distribution data
    """
    db = db_path or DB_PATH
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            CAST(strftime('%w', created_at) AS INTEGER) as day_of_week,
            COUNT(*) as count
        FROM case_intels
        GROUP BY day_of_week
        ORDER BY day_of_week
    """)
    
    day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    weekly = {i: {"day": day_names[i], "count": 0} for i in range(7)}
    total = 0
    
    for row in cursor.fetchall():
        day, count = row
        weekly[day]["count"] = count
        total += count
    
    conn.close()
    
    return {
        "weekly_distribution": list(weekly.values()),
        "total_intels": total
    }
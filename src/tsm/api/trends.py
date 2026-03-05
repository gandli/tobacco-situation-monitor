"""Trend analysis API endpoints for TSM.

Provides trend analysis and hotspot detection endpoints for
monitoring tobacco case patterns over time.
"""

import sqlite3
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from tsm.intel.trend_analysis import (
    TimeGranularity,
    analyze_trends,
    get_hotspots,
)

router = APIRouter()

# Default database path, can be overridden for testing
DB_PATH: str = "tsm.db"


def get_db_path() -> Optional[str]:
    """Get the database path (can be overridden in tests)."""
    return None


class TrendPointResponse(BaseModel):
    """Single point in a trend series."""
    time: str
    value: int
    label: str


class TrendSeriesResponse(BaseModel):
    """A series of trend points."""
    name: str
    points: List[TrendPointResponse]
    total: int
    average: Optional[float] = None
    trend_direction: Optional[str] = None


class TrendAnalysisResponse(BaseModel):
    """Complete trend analysis result."""
    period_start: str
    period_end: str
    granularity: str
    by_time: TrendSeriesResponse
    by_case_type: List[TrendSeriesResponse]
    by_risk_level: List[TrendSeriesResponse]
    by_region: List[TrendSeriesResponse]
    summary: Dict[str, Any]


class HotspotResponse(BaseModel):
    """Regional hotspot."""
    region: str
    count: int
    period_days: int


@router.get("/api/trends", response_model=TrendAnalysisResponse)
def trends(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    granularity: str = Query("day", pattern="^(day|week|month)$", description="Time granularity"),
    db_path: Optional[str] = Depends(get_db_path)
) -> TrendAnalysisResponse:
    """Get trend analysis for tobacco cases.

    Analyzes case distribution over time, by case type, by risk level,
    and by region.

    Args:
        days: Number of days to analyze (1-365).
        granularity: Time granularity (day, week, month).
        db_path: Database path override.

    Returns:
        TrendAnalysisResponse with all trend data.
    """
    granularity_enum = TimeGranularity(granularity)
    
    try:
        analysis = analyze_trends(
            days=days,
            granularity=granularity_enum,
            db_path=db_path or DB_PATH
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    return TrendAnalysisResponse(
        period_start=analysis.period_start,
        period_end=analysis.period_end,
        granularity=analysis.granularity.value,
        by_time=TrendSeriesResponse(
            name=analysis.by_time.name,
            points=[
                TrendPointResponse(time=p.time, value=p.value, label=p.label)
                for p in analysis.by_time.points
            ],
            total=analysis.by_time.total,
            average=analysis.by_time.average,
            trend_direction=analysis.by_time.trend_direction,
        ),
        by_case_type=[
            TrendSeriesResponse(
                name=s.name,
                points=[
                    TrendPointResponse(time=p.time, value=p.value, label=p.label)
                    for p in s.points
                ],
                total=s.total,
            )
            for s in analysis.by_case_type
        ],
        by_risk_level=[
            TrendSeriesResponse(
                name=s.name,
                points=[
                    TrendPointResponse(time=p.time, value=p.value, label=p.label)
                    for p in s.points
                ],
                total=s.total,
            )
            for s in analysis.by_risk_level
        ],
        by_region=[
            TrendSeriesResponse(
                name=s.name,
                points=[
                    TrendPointResponse(time=p.time, value=p.value, label=p.label)
                    for p in s.points
                ],
                total=s.total,
            )
            for s in analysis.by_region
        ],
        summary=analysis.summary,
    )


@router.get("/api/hotspots", response_model=List[HotspotResponse])
def hotspots(
    days: int = Query(7, ge=1, le=30, description="Number of days to look back"),
    threshold: int = Query(3, ge=1, description="Minimum cases to be considered a hotspot"),
    db_path: Optional[str] = Depends(get_db_path)
) -> List[HotspotResponse]:
    """Get regional hotspots with case concentration above threshold.

    A hotspot is a region with case count exceeding the threshold
    within the specified time period.

    Args:
        days: Number of days to look back (1-30).
        threshold: Minimum cases to be considered a hotspot.
        db_path: Database path override.

    Returns:
        List of hotspots with region, count, and period.
    """
    try:
        spots = get_hotspots(
            days=days,
            threshold=threshold,
            db_path=db_path or DB_PATH
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

    return [
        HotspotResponse(
            region=spot["region"],
            count=spot["count"],
            period_days=spot["period_days"]
        )
        for spot in spots
    ]


@router.get("/api/summary/today")
def today_summary(db_path: Optional[str] = Depends(get_db_path)) -> Dict[str, Any]:
    """Get a quick summary of today's cases.

    Returns counts and highlights for the current day.

    Args:
        db_path: Database path override.

    Returns:
        Summary with today's case counts and highlights.
    """
    db = db_path or DB_PATH
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    from datetime import date
    today = date.today().isoformat()

    # Total cases today
    cursor.execute(
        "SELECT COUNT(*) FROM case_intels WHERE date(created_at) = ?",
        (today,)
    )
    total_today = cursor.fetchone()[0]

    # High risk cases today
    cursor.execute(
        "SELECT COUNT(*) FROM case_intels WHERE date(created_at) = ? AND risk_level = 'high'",
        (today,)
    )
    high_risk_today = cursor.fetchone()[0]

    # Cases by type today
    cursor.execute(
        """SELECT case_type, COUNT(*) as cnt 
           FROM case_intels 
           WHERE date(created_at) = ? AND case_type IS NOT NULL
           GROUP BY case_type 
           ORDER BY cnt DESC""",
        (today,)
    )
    by_type = {row[0]: row[1] for row in cursor.fetchall()}

    # Cases by region today
    cursor.execute(
        """SELECT region, COUNT(*) as cnt 
           FROM case_intels 
           WHERE date(created_at) = ? AND region IS NOT NULL
           GROUP BY region 
           ORDER BY cnt DESC 
           LIMIT 5""",
        (today,)
    )
    by_region = {row[0]: row[1] for row in cursor.fetchall()}

    # Total monetary value today
    cursor.execute(
        """SELECT SUM(monetary_value) 
           FROM case_intels 
           WHERE date(created_at) = ? AND monetary_value IS NOT NULL""",
        (today,)
    )
    total_monetary = cursor.fetchone()[0] or 0

    # Alerts generated today
    cursor.execute(
        "SELECT COUNT(*) FROM alerts WHERE date(created_at) = ?",
        (today,)
    )
    alerts_today = cursor.fetchone()[0]

    conn.close()

    return {
        "date": today,
        "total_cases": total_today,
        "high_risk_cases": high_risk_today,
        "by_case_type": by_type,
        "by_region": by_region,
        "total_monetary_value": total_monetary,
        "alerts_generated": alerts_today,
    }
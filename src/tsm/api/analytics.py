"""Analytics API endpoints for TSM.

Provides endpoints for data analysis, trend analysis, and report generation.
"""

import json
from datetime import date, timedelta
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from tsm.services.analytics import (
    AnalyticsReport,
    get_analytics,
    get_risk_distribution,
    get_hourly_pattern,
    get_weekly_pattern,
)
from tsm.services.report_generator import (
    generate_markdown_report,
    generate_json_report,
    generate_csv_report,
    generate_executive_summary,
    generate_comprehensive_report,
    export_weekly_report,
    export_monthly_report,
)

router = APIRouter()

# Default database path
DB_PATH: str = "tsm.db"


def get_db_path() -> Optional[str]:
    """Get the database path (can be overridden in tests)."""
    return None


class TrendPoint(BaseModel):
    """A single point in a time series trend."""
    date: str
    count: int


class TrendResponse(BaseModel):
    """Response for trend analysis."""
    period: str
    metric: str
    data: list
    total: int
    average: float


class RiskDistributionResponse(BaseModel):
    """Response for risk distribution analysis."""
    period: dict
    total: int
    distribution: dict


class HourlyPatternResponse(BaseModel):
    """Response for hourly pattern analysis."""
    hourly_distribution: dict
    peak_hours: list
    total_intels: int


class WeeklyPatternResponse(BaseModel):
    """Response for weekly pattern analysis."""
    weekly_distribution: list
    total_intels: int


class ExecutiveSummaryResponse(BaseModel):
    """Response for executive summary."""
    summary: str
    start_date: str
    end_date: str


# ============================================================================
# Analytics Endpoints
# ============================================================================

@router.get("/api/analytics/trend")
def get_trend(
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
    period: str = Query("daily", description="Period: daily, weekly, monthly"),
    db_path: Optional[str] = None
) -> TrendResponse:
    """Get time series trend of intel collection.
    
    Shows how many intels were collected over time.
    """
    db = db_path or DB_PATH
    
    if end_date is None:
        end_date = date.today().isoformat()
    if start_date is None:
        start_date = (date.today() - timedelta(days=30)).isoformat()
    
    report = get_analytics(start_date, end_date, period, db)
    
    if report.trend is None:
        return TrendResponse(period=period, metric="intels_count", data=[], total=0, average=0)
    
    trend = report.trend
    return TrendResponse(
        period=trend.period,
        metric=trend.metric,
        data=[{"date": p.date, "count": p.count} for p in trend.data],
        total=trend.total,
        average=trend.average
    )


@router.get("/api/analytics/risk-distribution")
def get_risk_dist(
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
    db_path: Optional[str] = None
) -> RiskDistributionResponse:
    """Get distribution of cases by risk level.
    
    Shows breakdown by high/medium/low risk levels.
    """
    db = db_path or DB_PATH
    
    if end_date is None:
        end_date = date.today().isoformat()
    if start_date is None:
        start_date = (date.today() - timedelta(days=30)).isoformat()
    
    result = get_risk_distribution(start_date, end_date, db)
    
    return RiskDistributionResponse(
        period=result["period"],
        total=result["total"],
        distribution=result["distribution"]
    )


@router.get("/api/analytics/hourly-pattern")
def get_hourly(db_path: Optional[str] = None) -> HourlyPatternResponse:
    """Get pattern of intel creation by hour of day.
    
    Useful for understanding when cases are typically reported.
    """
    db = db_path or DB_PATH
    result = get_hourly_pattern(db)
    
    return HourlyPatternResponse(
        hourly_distribution=result["hourly_distribution"],
        peak_hours=result["peak_hours"],
        total_intels=result["total_intels"]
    )


@router.get("/api/analytics/weekly-pattern")
def get_weekly(db_path: Optional[str] = None) -> WeeklyPatternResponse:
    """Get pattern of intel creation by day of week.
    
    Shows which days have most activity.
    """
    db = db_path or DB_PATH
    result = get_weekly_pattern(db)
    
    return WeeklyPatternResponse(
        weekly_distribution=result["weekly_distribution"],
        total_intels=result["total_intels"]
    )


@router.get("/api/analytics/regional")
def get_regional(
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
    limit: int = Query(20, ge=1, le=100),
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """Get regional distribution of cases.
    
    Shows which regions have most cases and their case type breakdown.
    """
    db = db_path or DB_PATH
    
    if end_date is None:
        end_date = date.today().isoformat()
    if start_date is None:
        start_date = (date.today() - timedelta(days=30)).isoformat()
    
    report = get_analytics(start_date, end_date, "daily", db)
    
    regional = report.regional_distribution[:limit]
    
    return {
        "period": {"start": start_date, "end": end_date},
        "total_regions": len(report.regional_distribution),
        "data": [
            {
                "region": r.region,
                "count": r.count,
                "percentage": r.percentage,
                "case_types": r.case_types
            }
            for r in regional
        ]
    }


@router.get("/api/analytics/case-types")
def get_case_types(
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """Get breakdown by case type.
    
    Shows distribution of different case types with risk scores.
    """
    db = db_path or DB_PATH
    
    if end_date is None:
        end_date = date.today().isoformat()
    if start_date is None:
        start_date = (date.today() - timedelta(days=30)).isoformat()
    
    report = get_analytics(start_date, end_date, "daily", db)
    
    return {
        "period": {"start": start_date, "end": end_date},
        "total_types": len(report.case_type_breakdown),
        "data": [
            {
                "case_type": ct.case_type,
                "count": ct.count,
                "percentage": ct.percentage,
                "avg_risk_score": ct.avg_risk_score,
                "by_status": ct.by_status
            }
            for ct in report.case_type_breakdown
        ]
    }


@router.get("/api/analytics/sources")
def get_sources_effectiveness(
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """Get effectiveness metrics for each data source.
    
    Shows how well each source is performing.
    """
    db = db_path or DB_PATH
    
    if end_date is None:
        end_date = date.today().isoformat()
    if start_date is None:
        start_date = (date.today() - timedelta(days=30)).isoformat()
    
    report = get_analytics(start_date, end_date, "daily", db)
    
    return {
        "period": {"start": start_date, "end": end_date},
        "sources": [
            {
                "source_id": s.source_id,
                "source_name": s.source_name,
                "articles_collected": s.articles_collected,
                "intels_generated": s.intels_generated,
                "conversion_rate": s.conversion_rate,
                "confirmed_count": s.confirmed_count,
                "accuracy_rate": s.accuracy_rate
            }
            for s in report.source_effectiveness
        ]
    }


# ============================================================================
# Report Generation Endpoints
# ============================================================================

@router.get("/api/reports/summary")
def get_summary(
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
    db_path: Optional[str] = None
) -> ExecutiveSummaryResponse:
    """Get executive summary of analytics.
    
    Returns a brief summary suitable for quick review.
    """
    db = db_path or DB_PATH
    
    if end_date is None:
        end_date = date.today().isoformat()
    if start_date is None:
        start_date = (date.today() - timedelta(days=7)).isoformat()
    
    report = get_analytics(start_date, end_date, "daily", db)
    summary = generate_executive_summary(report)
    
    return ExecutiveSummaryResponse(
        summary=summary,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/api/reports/weekly")
def get_weekly_report(
    format: str = Query("markdown", description="Output format: markdown, json"),
    db_path: Optional[str] = None
):
    """Generate weekly report.
    
    Returns comprehensive weekly report in specified format.
    """
    db = db_path or DB_PATH
    result = export_weekly_report(db)
    
    if format == "json":
        return result["json"]
    else:
        return PlainTextResponse(content=result["markdown"], media_type="text/markdown")


@router.get("/api/reports/monthly")
def get_monthly_report(
    format: str = Query("markdown", description="Output format: markdown, json"),
    db_path: Optional[str] = None
):
    """Generate monthly report.
    
    Returns comprehensive monthly report in specified format.
    """
    db = db_path or DB_PATH
    result = export_monthly_report(db)
    
    if format == "json":
        return result["json"]
    else:
        return PlainTextResponse(content=result["markdown"], media_type="text/markdown")


@router.get("/api/reports/custom")
def get_custom_report(
    start_date: str = Query(..., description="Start date YYYY-MM-DD"),
    end_date: str = Query(..., description="End date YYYY-MM-DD"),
    period: str = Query("daily", description="Trend period: daily, weekly, monthly"),
    format: str = Query("markdown", description="Output format: markdown, json"),
    db_path: Optional[str] = None
):
    """Generate custom report for specified date range.
    
    Returns comprehensive report in specified format.
    """
    db = db_path or DB_PATH
    
    report = get_analytics(start_date, end_date, period, db)
    
    if format == "json":
        return generate_json_report(report)
    else:
        return PlainTextResponse(
            content=generate_markdown_report(report),
            media_type="text/markdown"
        )


@router.get("/api/reports/export")
def export_report(
    start_date: str = Query(..., description="Start date YYYY-MM-DD"),
    end_date: str = Query(..., description="End date YYYY-MM-DD"),
    section: str = Query("summary", description="Section: summary, regional, case_types, sources"),
    db_path: Optional[str] = None
):
    """Export report section as CSV.
    
    Returns CSV data for spreadsheet import.
    """
    db = db_path or DB_PATH
    
    report = get_analytics(start_date, end_date, "daily", db)
    csv_data = generate_csv_report(report, section)
    
    return PlainTextResponse(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=tsm_{section}_{start_date}_{end_date}.csv"
        }
    )
"""Report generator for TSM.

Generates formatted reports in Markdown, JSON, and CSV formats.
"""

import csv
import io
import json
from dataclasses import asdict
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from tsm.services.analytics import (
    AnalyticsReport,
    CaseTypeBreakdown,
    RegionalDistribution,
    SourceEffectiveness,
    TimeSeriesTrend,
    get_analytics,
    get_risk_distribution,
    get_hourly_pattern,
    get_weekly_pattern,
)


def generate_markdown_report(
    report: AnalyticsReport,
    include_trend: bool = True,
    include_regional: bool = True,
    include_case_types: bool = True,
    include_sources: bool = True
) -> str:
    """Generate a Markdown formatted report.
    
    Args:
        report: AnalyticsReport object
        include_trend: Include trend analysis section
        include_regional: Include regional distribution section
        include_case_types: Include case type breakdown section
        include_sources: Include source effectiveness section
    
    Returns:
        Markdown formatted report string
    """
    lines = []
    
    # Header
    lines.append(f"# TSM 情报分析报告")
    lines.append("")
    lines.append(f"**报告日期**: {report.report_date}")
    lines.append(f"**统计周期**: {report.period_start} ~ {report.period_end}")
    lines.append("")
    
    # Summary
    lines.append("## 📊 总体概览")
    lines.append("")
    lines.append(f"| 指标 | 数量 |")
    lines.append(f"|------|------|")
    lines.append(f"| 情报总数 | {report.total_intels} |")
    lines.append(f"| 本周期新增 | {report.new_intels} |")
    lines.append(f"| 已确认案件 | {report.confirmed_intels} |")
    lines.append(f"| 已排除噪音 | {report.dismissed_intels} |")
    lines.append(f"| 待复核 | {report.pending_intels} |")
    lines.append("")
    
    # Trend analysis
    if include_trend and report.trend:
        lines.append("## 📈 趋势分析")
        lines.append("")
        trend = report.trend
        lines.append(f"**周期**: {trend.period} | **总计**: {trend.total} | **平均**: {trend.average}")
        lines.append("")
        
        if trend.data:
            lines.append("### 时间序列数据")
            lines.append("")
            lines.append("| 日期 | 数量 |")
            lines.append("|------|------|")
            for point in trend.data[-10:]:  # Show last 10 points
                lines.append(f"| {point.date} | {point.count} |")
            lines.append("")
    
    # Regional distribution
    if include_regional and report.regional_distribution:
        lines.append("## 🗺️ 地区分布")
        lines.append("")
        
        if report.regional_distribution:
            lines.append("| 地区 | 数量 | 占比 | 案件类型分布 |")
            lines.append("|------|------|------|--------------|")
            for r in report.regional_distribution[:10]:
                case_types_str = ", ".join(f"{k}:{v}" for k, v in r.case_types.items())
                lines.append(f"| {r.region} | {r.count} | {r.percentage}% | {case_types_str or '-'} |")
            lines.append("")
    
    # Case type breakdown
    if include_case_types and report.case_type_breakdown:
        lines.append("## 🔍 案件类型分析")
        lines.append("")
        
        if report.case_type_breakdown:
            lines.append("| 案件类型 | 数量 | 占比 | 平均风险分 | 状态分布 |")
            lines.append("|----------|------|------|------------|----------|")
            for ct in report.case_type_breakdown:
                status_str = ", ".join(f"{k}:{v}" for k, v in ct.by_status.items())
                lines.append(f"| {ct.case_type} | {ct.count} | {ct.percentage}% | {ct.avg_risk_score} | {status_str or '-'} |")
            lines.append("")
    
    # Source effectiveness
    if include_sources and report.source_effectiveness:
        lines.append("## 📡 数据源效能")
        lines.append("")
        
        if report.source_effectiveness:
            lines.append("| 数据源 | 采集文章 | 生成情报 | 转化率 | 已确认 | 准确率 |")
            lines.append("|--------|----------|----------|--------|--------|--------|")
            for s in report.source_effectiveness:
                lines.append(
                    f"| {s.source_name} | {s.articles_collected} | {s.intels_generated} | "
                    f"{s.conversion_rate}% | {s.confirmed_count} | {s.accuracy_rate}% |"
                )
            lines.append("")
    
    # Footer
    lines.append("---")
    lines.append(f"*报告由 TSM (Tobacco Situation Monitor) 自动生成*")
    
    return "\n".join(lines)


def generate_json_report(report: AnalyticsReport) -> str:
    """Generate a JSON formatted report.
    
    Args:
        report: AnalyticsReport object
    
    Returns:
        JSON formatted report string
    """
    # Convert dataclasses to dicts
    data = {
        "report_date": report.report_date,
        "period": {
            "start": report.period_start,
            "end": report.period_end
        },
        "summary": {
            "total_intels": report.total_intels,
            "new_intels": report.new_intels,
            "confirmed_intels": report.confirmed_intels,
            "dismissed_intels": report.dismissed_intels,
            "pending_intels": report.pending_intels
        }
    }
    
    # Add trend
    if report.trend:
        data["trend"] = {
            "period": report.trend.period,
            "metric": report.trend.metric,
            "total": report.trend.total,
            "average": report.trend.average,
            "data": [{"date": p.date, "count": p.count} for p in report.trend.data]
        }
    
    # Add regional distribution
    if report.regional_distribution:
        data["regional_distribution"] = [
            {
                "region": r.region,
                "count": r.count,
                "percentage": r.percentage,
                "case_types": r.case_types
            }
            for r in report.regional_distribution
        ]
    
    # Add case type breakdown
    if report.case_type_breakdown:
        data["case_type_breakdown"] = [
            {
                "case_type": ct.case_type,
                "count": ct.count,
                "percentage": ct.percentage,
                "avg_risk_score": ct.avg_risk_score,
                "by_status": ct.by_status
            }
            for ct in report.case_type_breakdown
        ]
    
    # Add source effectiveness
    if report.source_effectiveness:
        data["source_effectiveness"] = [
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
    
    return json.dumps(data, ensure_ascii=False, indent=2)


def generate_csv_report(report: AnalyticsReport, section: str = "summary") -> str:
    """Generate a CSV formatted report.
    
    Args:
        report: AnalyticsReport object
        section: Which section to export ('summary', 'regional', 'case_types', 'sources')
    
    Returns:
        CSV formatted report string
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    if section == "summary":
        writer.writerow(["指标", "数量"])
        writer.writerow(["情报总数", report.total_intels])
        writer.writerow(["本周期新增", report.new_intels])
        writer.writerow(["已确认案件", report.confirmed_intels])
        writer.writerow(["已排除噪音", report.dismissed_intels])
        writer.writerow(["待复核", report.pending_intels])
    
    elif section == "regional" and report.regional_distribution:
        writer.writerow(["地区", "数量", "占比", "案件类型"])
        for r in report.regional_distribution:
            case_types_str = "; ".join(f"{k}:{v}" for k, v in r.case_types.items())
            writer.writerow([r.region, r.count, r.percentage, case_types_str])
    
    elif section == "case_types" and report.case_type_breakdown:
        writer.writerow(["案件类型", "数量", "占比", "平均风险分", "状态分布"])
        for ct in report.case_type_breakdown:
            status_str = "; ".join(f"{k}:{v}" for k, v in ct.by_status.items())
            writer.writerow([ct.case_type, ct.count, ct.percentage, ct.avg_risk_score, status_str])
    
    elif section == "sources" and report.source_effectiveness:
        writer.writerow(["数据源ID", "数据源名称", "采集文章", "生成情报", "转化率", "已确认", "准确率"])
        for s in report.source_effectiveness:
            writer.writerow([
                s.source_id, s.source_name, s.articles_collected,
                s.intels_generated, s.conversion_rate, s.confirmed_count, s.accuracy_rate
            ])
    
    return output.getvalue()


def generate_executive_summary(report: AnalyticsReport) -> str:
    """Generate a brief executive summary in Chinese.
    
    Args:
        report: AnalyticsReport object
    
    Returns:
        Executive summary string
    """
    lines = []
    
    # Title
    lines.append("📋 执行摘要")
    lines.append("")
    
    # Period
    lines.append(f"统计周期: {report.period_start} 至 {report.period_end}")
    lines.append("")
    
    # Key metrics
    lines.append("### 核心指标")
    lines.append(f"- 本周期共收集情报 **{report.new_intels}** 条")
    lines.append(f"- 已确认案件 **{report.confirmed_intels}** 条")
    
    # Accuracy rate
    reviewed = report.confirmed_intels + report.dismissed_intels
    if reviewed > 0:
        accuracy = report.confirmed_intels / reviewed * 100
        lines.append(f"- 识别准确率 **{accuracy:.1f}%**")
    
    lines.append("")
    
    # Top regions
    if report.regional_distribution:
        top_regions = report.regional_distribution[:3]
        lines.append("### 重点地区")
        for r in top_regions:
            lines.append(f"- **{r.region}**: {r.count} 条 ({r.percentage}%)")
        lines.append("")
    
    # Top case types
    if report.case_type_breakdown:
        top_types = report.case_type_breakdown[:3]
        lines.append("### 主要案件类型")
        for ct in top_types:
            lines.append(f"- **{ct.case_type}**: {ct.count} 条 ({ct.percentage}%)")
        lines.append("")
    
    # High risk
    lines.append(f"### 待处理")
    lines.append(f"- 待复核情报: **{report.pending_intels}** 条")
    lines.append("")
    
    return "\n".join(lines)


def generate_comprehensive_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    period: str = "daily",
    db_path: Optional[str] = None,
    format: str = "markdown"
) -> str:
    """Generate a comprehensive report with all analytics.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        period: Trend period ('daily', 'weekly', 'monthly')
        db_path: Database path
        format: Output format ('markdown', 'json')
    
    Returns:
        Formatted report string
    """
    # Get analytics data
    report = get_analytics(start_date, end_date, period, db_path)
    
    if format == "json":
        return generate_json_report(report)
    else:
        return generate_markdown_report(report)


def export_weekly_report(
    db_path: Optional[str] = None
) -> Dict[str, str]:
    """Export weekly report in multiple formats.
    
    Args:
        db_path: Database path
    
    Returns:
        Dict with 'markdown', 'json', and 'summary' keys
    """
    from datetime import timedelta
    
    end_date = date.today()
    start_date = end_date - timedelta(days=7)
    
    report = get_analytics(
        start_date.isoformat(),
        end_date.isoformat(),
        period="daily",
        db_path=db_path
    )
    
    return {
        "markdown": generate_markdown_report(report),
        "json": generate_json_report(report),
        "summary": generate_executive_summary(report),
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }


def export_monthly_report(
    db_path: Optional[str] = None
) -> Dict[str, str]:
    """Export monthly report in multiple formats.
    
    Args:
        db_path: Database path
    
    Returns:
        Dict with 'markdown', 'json', and 'summary' keys
    """
    from datetime import timedelta
    
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    report = get_analytics(
        start_date.isoformat(),
        end_date.isoformat(),
        period="weekly",
        db_path=db_path
    )
    
    return {
        "markdown": generate_markdown_report(report),
        "json": generate_json_report(report),
        "summary": generate_executive_summary(report),
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }
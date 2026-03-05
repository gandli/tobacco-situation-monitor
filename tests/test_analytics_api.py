"""Test Analytics API endpoints for TSM.

Tests the analytics and reporting functionality added in V0.2.
"""

import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from tsm.db import init_db


@pytest.fixture
def analytics_test_db():
    """Create a comprehensive test database with sample analytics data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "analytics_test.db"
        conn = sqlite3.connect(str(db_path))
        init_db(conn)
        
        now = datetime.now()
        
        # Insert test sources
        conn.execute("""
            INSERT INTO sources (id, name, list_url, last_crawled_at)
            VALUES 
                (1, '烟草新闻网', 'http://news.example.com', datetime('now')),
                (2, '执法日报', 'http://law.example.com', datetime('now')),
                (3, '走私情报网', 'http://smuggling.example.com', NULL)
        """)
        
        # Insert test articles over time
        articles = []
        for i in range(1, 31):
            days_ago = (now - timedelta(days=i)).isoformat()
            source_id = 1 if i <= 15 else 2
            articles.append((
                i, source_id, f'http://example.com/{i}', f'Article {i}',
                days_ago, days_ago
            ))
        
        for article in articles:
            conn.execute(
                "INSERT INTO raw_articles (id, source_id, url, title, published_at, fetched_at) VALUES (?, ?, ?, ?, ?, ?)",
                article
            )
        
        # Insert test intels with various attributes
        regions = ['上海', '北京', '广州', '深圳', '福州', '厦门']
        case_types = ['counterfeit', 'smuggling', 'unlicensed', 'tax_evasion']
        risk_levels = ['low', 'medium', 'high']
        statuses = ['new', 'confirmed', 'dismissed']
        
        for i in range(1, 51):
            days_ago = (now - timedelta(days=i % 30)).isoformat()
            region = regions[i % len(regions)]
            case_type = case_types[i % len(case_types)]
            risk_level = risk_levels[i % len(risk_levels)]
            status = statuses[i % len(statuses)]
            risk_score = 20 if risk_level == 'low' else (45 if risk_level == 'medium' else 75)
            
            conn.execute("""
                INSERT INTO case_intels 
                (id, article_id, is_case_related, case_type, region, risk_score, risk_level, status, created_at)
                VALUES (?, ?, 1, ?, ?, ?, ?, ?, ?)
            """, (i, (i % 30) + 1, case_type, region, risk_score, risk_level, status, days_ago))
        
        # Insert some review logs
        for i in [1, 2, 3, 10, 11, 12, 20, 21, 22]:
            conn.execute("""
                INSERT INTO review_logs (intel_id, action, comment)
                VALUES (?, ?, ?)
            """, (i, 'confirm' if i % 2 == 0 else 'dismiss', f'Review {i}'))
        
        conn.commit()
        conn.close()
        yield str(db_path)


@pytest.fixture
def client(analytics_test_db):
    """Create a test client with analytics test database."""
    # Import modules first
    import tsm.services.analytics
    import tsm.api.analytics
    import tsm.api.dashboard
    import tsm.api.intels
    import tsm.services.source_manager
    import tsm.services.review_service
    
    # Set DB_PATH directly on modules
    tsm.services.analytics.DB_PATH = analytics_test_db
    tsm.api.analytics.DB_PATH = analytics_test_db
    tsm.api.dashboard.DB_PATH = analytics_test_db
    tsm.api.intels.DB_PATH = analytics_test_db
    tsm.services.source_manager.DB_PATH = analytics_test_db
    tsm.services.review_service.DB_PATH = analytics_test_db
    
    from tsm.main import app
    with TestClient(app) as c:
        yield c


class TestTrendAnalytics:
    """Test trend analysis endpoint."""
    
    def test_trend_endpoint_returns_200(self, client):
        """Trend endpoint should return HTTP 200."""
        resp = client.get("/api/analytics/trend")
        assert resp.status_code == 200
    
    def test_trend_response_has_required_fields(self, client):
        """Trend response should have all required fields."""
        resp = client.get("/api/analytics/trend")
        data = resp.json()
        
        assert "period" in data
        assert "metric" in data
        assert "data" in data
        assert "total" in data
        assert "average" in data
    
    def test_trend_with_custom_date_range(self, client):
        """Trend should accept custom date range."""
        resp = client.get("/api/analytics/trend?start_date=2025-01-01&end_date=2026-01-01")
        assert resp.status_code == 200
    
    def test_trend_with_weekly_period(self, client):
        """Trend should support weekly aggregation."""
        resp = client.get("/api/analytics/trend?period=weekly")
        assert resp.status_code == 200
        assert resp.json()["period"] == "weekly"
    
    def test_trend_with_monthly_period(self, client):
        """Trend should support monthly aggregation."""
        resp = client.get("/api/analytics/trend?period=monthly")
        assert resp.status_code == 200
        assert resp.json()["period"] == "monthly"


class TestRiskDistribution:
    """Test risk distribution endpoint."""
    
    def test_risk_distribution_returns_200(self, client):
        """Risk distribution endpoint should return HTTP 200."""
        resp = client.get("/api/analytics/risk-distribution")
        assert resp.status_code == 200
    
    def test_risk_distribution_has_required_fields(self, client):
        """Risk distribution response should have required fields."""
        resp = client.get("/api/analytics/risk-distribution")
        data = resp.json()
        
        assert "period" in data
        assert "total" in data
        assert "distribution" in data


class TestRegionalDistribution:
    """Test regional distribution endpoint."""
    
    def test_regional_returns_200(self, client):
        """Regional endpoint should return HTTP 200."""
        resp = client.get("/api/analytics/regional")
        assert resp.status_code == 200
    
    def test_regional_has_data_structure(self, client):
        """Regional response should have proper data structure."""
        resp = client.get("/api/analytics/regional")
        data = resp.json()
        
        assert "period" in data
        assert "total_regions" in data
        assert "data" in data
        assert isinstance(data["data"], list)


class TestCaseTypesAnalytics:
    """Test case types breakdown endpoint."""
    
    def test_case_types_returns_200(self, client):
        """Case types endpoint should return HTTP 200."""
        resp = client.get("/api/analytics/case-types")
        assert resp.status_code == 200
    
    def test_case_types_has_required_fields(self, client):
        """Case types response should have required fields."""
        resp = client.get("/api/analytics/case-types")
        data = resp.json()
        
        assert "period" in data
        assert "total_types" in data
        assert "data" in data


class TestSourcesEffectiveness:
    """Test source effectiveness endpoint."""
    
    def test_sources_returns_200(self, client):
        """Sources effectiveness endpoint should return HTTP 200."""
        resp = client.get("/api/analytics/sources")
        assert resp.status_code == 200
    
    def test_sources_has_metrics(self, client):
        """Sources response should have effectiveness metrics."""
        resp = client.get("/api/analytics/sources")
        data = resp.json()
        
        assert "period" in data
        assert "sources" in data


class TestHourlyPattern:
    """Test hourly pattern endpoint."""
    
    def test_hourly_returns_200(self, client):
        """Hourly pattern endpoint should return HTTP 200."""
        resp = client.get("/api/analytics/hourly-pattern")
        assert resp.status_code == 200
    
    def test_hourly_has_24_hours(self, client):
        """Hourly distribution should have 24 hours."""
        resp = client.get("/api/analytics/hourly-pattern")
        data = resp.json()
        
        assert "hourly_distribution" in data
        assert "peak_hours" in data
        # Should have entries for all 24 hours
        assert len(data["hourly_distribution"]) == 24


class TestWeeklyPattern:
    """Test weekly pattern endpoint."""
    
    def test_weekly_returns_200(self, client):
        """Weekly pattern endpoint should return HTTP 200."""
        resp = client.get("/api/analytics/weekly-pattern")
        assert resp.status_code == 200
    
    def test_weekly_has_7_days(self, client):
        """Weekly distribution should have 7 days."""
        resp = client.get("/api/analytics/weekly-pattern")
        data = resp.json()
        
        assert "weekly_distribution" in data
        assert len(data["weekly_distribution"]) == 7


class TestReportGeneration:
    """Test report generation endpoints."""
    
    def test_summary_returns_200(self, client):
        """Summary endpoint should return HTTP 200."""
        resp = client.get("/api/reports/summary")
        assert resp.status_code == 200
    
    def test_summary_has_required_fields(self, client):
        """Summary response should have required fields."""
        resp = client.get("/api/reports/summary")
        data = resp.json()
        
        assert "summary" in data
        assert "start_date" in data
        assert "end_date" in data
    
    def test_weekly_report_markdown(self, client):
        """Weekly report should return markdown by default."""
        resp = client.get("/api/reports/weekly")
        assert resp.status_code == 200
        assert "# TSM" in resp.text or "情报" in resp.text
    
    def test_weekly_report_json(self, client):
        """Weekly report should support JSON format."""
        resp = client.get("/api/reports/weekly?format=json")
        assert resp.status_code == 200
        data = resp.json()
        assert "report_date" in data
    
    def test_monthly_report_markdown(self, client):
        """Monthly report should return markdown."""
        resp = client.get("/api/reports/monthly")
        assert resp.status_code == 200
    
    def test_monthly_report_json(self, client):
        """Monthly report should support JSON format."""
        resp = client.get("/api/reports/monthly?format=json")
        assert resp.status_code == 200
        data = resp.json()
        assert "report_date" in data
    
    def test_custom_report(self, client):
        """Custom report should accept date range."""
        resp = client.get("/api/reports/custom?start_date=2025-01-01&end_date=2026-01-01")
        assert resp.status_code == 200
    
    def test_export_csv_summary(self, client):
        """Export should return CSV for summary."""
        resp = client.get("/api/reports/export?start_date=2025-01-01&end_date=2026-01-01&section=summary")
        assert resp.status_code == 200
        assert "指标" in resp.text or "text/csv" in resp.headers.get("content-type", "")
    
    def test_export_csv_regional(self, client):
        """Export should return CSV for regional data."""
        resp = client.get("/api/reports/export?start_date=2025-01-01&end_date=2026-01-01&section=regional")
        assert resp.status_code == 200


class TestAnalyticsService:
    """Test analytics service directly."""
    
    def test_get_analytics_returns_report(self, analytics_test_db):
        """Analytics service should return AnalyticsReport."""
        from tsm.services.analytics import get_analytics
        
        report = get_analytics(db_path=analytics_test_db)
        
        assert report.total_intels == 50
        assert report.new_intels >= 0
        assert report.confirmed_intels >= 0
        assert report.trend is not None
        assert len(report.regional_distribution) > 0
        assert len(report.case_type_breakdown) > 0
    
    def test_get_risk_distribution(self, analytics_test_db):
        """Risk distribution should have levels."""
        from tsm.services.analytics import get_risk_distribution
        
        result = get_risk_distribution(db_path=analytics_test_db)
        
        assert result["total"] > 0
        assert "distribution" in result
    
    def test_get_hourly_pattern(self, analytics_test_db):
        """Hourly pattern should have 24 hours."""
        from tsm.services.analytics import get_hourly_pattern
        
        result = get_hourly_pattern(db_path=analytics_test_db)
        
        assert len(result["hourly_distribution"]) == 24
        assert result["total_intels"] >= 0
    
    def test_get_weekly_pattern(self, analytics_test_db):
        """Weekly pattern should have 7 days."""
        from tsm.services.analytics import get_weekly_pattern
        
        result = get_weekly_pattern(db_path=analytics_test_db)
        
        assert len(result["weekly_distribution"]) == 7


class TestReportGenerator:
    """Test report generator service."""
    
    def test_generate_markdown_report(self, analytics_test_db):
        """Should generate markdown report."""
        from tsm.services.analytics import get_analytics
        from tsm.services.report_generator import generate_markdown_report
        
        report = get_analytics(db_path=analytics_test_db)
        md = generate_markdown_report(report)
        
        assert "# TSM" in md
        assert "情报" in md
    
    def test_generate_json_report(self, analytics_test_db):
        """Should generate JSON report."""
        import json
        
        from tsm.services.analytics import get_analytics
        from tsm.services.report_generator import generate_json_report
        
        report = get_analytics(db_path=analytics_test_db)
        json_str = generate_json_report(report)
        data = json.loads(json_str)
        
        assert "report_date" in data
        assert "summary" in data
    
    def test_generate_executive_summary(self, analytics_test_db):
        """Should generate executive summary."""
        from tsm.services.analytics import get_analytics
        from tsm.services.report_generator import generate_executive_summary
        
        report = get_analytics(db_path=analytics_test_db)
        summary = generate_executive_summary(report)
        
        assert "执行摘要" in summary or "摘要" in summary


class TestEdgeCases:
    """Test edge cases for analytics."""
    
    def test_empty_database_analytics(self):
        """Analytics should handle empty database gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "empty.db"
            conn = sqlite3.connect(str(db_path))
            init_db(conn)
            conn.close()
            
            # Set DB_PATH directly on modules
            import tsm.services.analytics
            import tsm.api.analytics
            
            tsm.services.analytics.DB_PATH = str(db_path)
            tsm.api.analytics.DB_PATH = str(db_path)
            
            from tsm.main import app
            with TestClient(app) as client:
                # All endpoints should return 200
                assert client.get("/api/analytics/trend").status_code == 200
                assert client.get("/api/analytics/risk-distribution").status_code == 200
                assert client.get("/api/analytics/regional").status_code == 200
                assert client.get("/api/analytics/case-types").status_code == 200
    
    def test_date_range_validation(self, client):
        """Should handle various date ranges."""
        # Future dates should work (just return empty)
        resp = client.get("/api/analytics/trend?start_date=2030-01-01&end_date=2030-12-31")
        assert resp.status_code == 200
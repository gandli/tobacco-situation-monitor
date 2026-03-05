"""Test KPI API endpoints for OSINT Effect Dashboard V0.1.

KPIs defined:
- coverage_rate (覆盖率): % of sources successfully crawled
- timeliness_score (时效性): Avg time from article publish to collection (hours)
- accuracy_rate (识别准确率): % of confirmed intels / total classified
- noise_rate (噪音率): % of dismissed intels / total classified
- reviewable_rate (可复核率): % of intels with review logs
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
def test_db():
    """Create a temporary test database with sample data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        conn = sqlite3.connect(str(db_path))
        init_db(conn)
        
        # Insert test sources
        conn.execute("""
            INSERT INTO sources (id, name, list_url, last_crawled_at)
            VALUES 
                (1, 'Source A', 'http://a.com', datetime('now')),
                (2, 'Source B', 'http://b.com', datetime('now')),
                (3, 'Source C', 'http://c.com', NULL)
        """)
        
        # Insert test articles with various timestamps
        now = datetime.now()
        articles = [
            # Article 1: published 2 hours ago, fetched 1 hour ago (timeliness: 1 hour)
            (1, 1, 'http://a.com/1', 'Article 1', now - timedelta(hours=2), now - timedelta(hours=1)),
            # Article 2: published 5 hours ago, fetched 4 hours ago (timeliness: 1 hour)
            (2, 1, 'http://a.com/2', 'Article 2', now - timedelta(hours=5), now - timedelta(hours=4)),
            # Article 3: published 10 hours ago, fetched 2 hours ago (timeliness: 8 hours)
            (3, 2, 'http://b.com/1', 'Article 3', now - timedelta(hours=10), now - timedelta(hours=2)),
            # Article 4: published yesterday, fetched today (timeliness: 20 hours)
            (4, 2, 'http://b.com/2', 'Article 4', now - timedelta(hours=28), now - timedelta(hours=8)),
            # Article 5: no publish date, skip for timeliness
            (5, 2, 'http://b.com/3', 'Article 5', None, now - timedelta(hours=1)),
        ]
        for article in articles:
            conn.execute(
                "INSERT INTO raw_articles (id, source_id, url, title, published_at, fetched_at) VALUES (?, ?, ?, ?, ?, ?)",
                article
            )
        
        # Insert test intels with various classifications and statuses
        conn.execute("""
            INSERT INTO case_intels (id, article_id, is_case_related, case_type, region, risk_level, status)
            VALUES 
                (1, 1, 1, 'smuggling', 'Shanghai', 'high', 'confirmed'),
                (2, 2, 1, 'counterfeit', 'Beijing', 'medium', 'confirmed'),
                (3, 3, 1, 'smuggling', 'Guangzhou', 'low', 'dismissed'),
                (4, 4, 1, 'unlicensed', 'Shenzhen', 'medium', 'new'),
                (5, 5, 0, NULL, NULL, 'low', 'new')
        """)
        
        # Insert review logs for some intels
        conn.execute("""
            INSERT INTO review_logs (intel_id, action, comment)
            VALUES 
                (1, 'confirm', 'Verified case'),
                (2, 'confirm', 'Confirmed'),
                (3, 'dismiss', 'False positive')
        """)
        
        conn.commit()
        conn.close()
        yield str(db_path)


@pytest.fixture
def client(test_db):
    """Create a test client with a temporary database."""
    with patch('tsm.services.source_manager.DB_PATH', test_db), \
         patch('tsm.services.review_service.DB_PATH', test_db), \
         patch('tsm.api.dashboard.DB_PATH', test_db), \
         patch('tsm.api.intels.DB_PATH', test_db):
        from tsm.main import app
        with TestClient(app) as c:
            yield c


class TestKPIEndpointExists:
    """Test that KPI endpoint exists and returns expected structure."""
    
    def test_kpi_endpoint_returns_200(self, client):
        """KPI endpoint should return HTTP 200."""
        resp = client.get("/api/dashboard/kpi")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    
    def test_kpi_response_has_all_five_kpis(self, client):
        """KPI response must contain all 5 required KPIs."""
        resp = client.get("/api/dashboard/kpi")
        assert resp.status_code == 200
        data = resp.json()
        
        required_kpis = [
            "coverage_rate",
            "timeliness_score", 
            "accuracy_rate",
            "noise_rate",
            "reviewable_rate"
        ]
        for kpi in required_kpis:
            assert kpi in data, f"Missing required KPI: {kpi}"


class TestCoverageRate:
    """Test coverage_rate KPI: % of sources successfully crawled."""
    
    def test_coverage_rate_calculation(self, client):
        """Coverage rate should be crawled_sources / total_sources * 100."""
        resp = client.get("/api/dashboard/kpi")
        assert resp.status_code == 200
        data = resp.json()
        
        # We have 3 sources, 2 have been crawled (last_crawled_at is not NULL)
        # Expected: 2/3 * 100 = 66.67%
        coverage = data["coverage_rate"]
        assert "value" in coverage
        assert "percentage" in coverage
        assert "description" in coverage
        
        # Allow some floating point tolerance
        expected = 2 / 3 * 100
        assert abs(coverage["percentage"] - expected) < 0.1, \
            f"Expected coverage ~{expected}%, got {coverage['percentage']}%"


class TestTimelinessScore:
    """Test timeliness_score KPI: Avg time from article publish to collection."""
    
    def test_timeliness_calculation(self, client):
        """Timeliness should be avg hours between published_at and fetched_at."""
        resp = client.get("/api/dashboard/kpi")
        assert resp.status_code == 200
        data = resp.json()
        
        timeliness = data["timeliness_score"]
        assert "value" in timeliness
        assert "avg_hours" in timeliness
        assert "description" in timeliness
        
        # Articles with publish dates: 
        # Art1: 1 hour delay, Art2: 1 hour delay, Art3: 8 hours, Art4: 20 hours
        # Average = (1+1+8+20) / 4 = 7.5 hours
        expected_avg = (1 + 1 + 8 + 20) / 4
        assert abs(timeliness["avg_hours"] - expected_avg) < 0.5, \
            f"Expected avg ~{expected_avg} hours, got {timeliness['avg_hours']}"


class TestAccuracyRate:
    """Test accuracy_rate KPI: % of confirmed intels / total classified."""
    
    def test_accuracy_rate_calculation(self, client):
        """Accuracy rate should be confirmed / (confirmed + dismissed) * 100."""
        resp = client.get("/api/dashboard/kpi")
        assert resp.status_code == 200
        data = resp.json()
        
        accuracy = data["accuracy_rate"]
        assert "value" in accuracy
        assert "percentage" in accuracy
        assert "description" in accuracy
        
        # We have 2 confirmed, 1 dismissed = 3 reviewed total
        # Accuracy = 2/3 * 100 = 66.67%
        expected = 2 / 3 * 100
        assert abs(accuracy["percentage"] - expected) < 0.1, \
            f"Expected accuracy ~{expected}%, got {accuracy['percentage']}%"


class TestNoiseRate:
    """Test noise_rate KPI: % of dismissed intels / total classified."""
    
    def test_noise_rate_calculation(self, client):
        """Noise rate should be dismissed / (confirmed + dismissed) * 100."""
        resp = client.get("/api/dashboard/kpi")
        assert resp.status_code == 200
        data = resp.json()
        
        noise = data["noise_rate"]
        assert "value" in noise
        assert "percentage" in noise
        assert "description" in noise
        
        # We have 1 dismissed, 3 reviewed total
        # Noise = 1/3 * 100 = 33.33%
        expected = 1 / 3 * 100
        assert abs(noise["percentage"] - expected) < 0.1, \
            f"Expected noise ~{expected}%, got {noise['percentage']}%"


class TestReviewableRate:
    """Test reviewable_rate KPI: % of intels with review logs."""
    
    def test_reviewable_rate_calculation(self, client):
        """Reviewable rate should be intels_with_reviews / total_intels * 100."""
        resp = client.get("/api/dashboard/kpi")
        assert resp.status_code == 200
        data = resp.json()
        
        reviewable = data["reviewable_rate"]
        assert "value" in reviewable
        assert "percentage" in reviewable
        assert "description" in reviewable
        
        # We have 5 intels, 3 have review logs
        # Reviewable = 3/5 * 100 = 60%
        expected = 3 / 5 * 100
        assert abs(reviewable["percentage"] - expected) < 0.1, \
            f"Expected reviewable ~{expected}%, got {reviewable['percentage']}%"


class TestKPIEdgeCases:
    """Test KPI calculations with edge cases."""
    
    def test_empty_database_returns_zeros(self):
        """KPI should return 0 values when no data exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "empty.db"
            conn = sqlite3.connect(str(db_path))
            init_db(conn)
            conn.close()
            
            with patch('tsm.api.dashboard.DB_PATH', str(db_path)):
                from tsm.main import app
                with TestClient(app) as client:
                    resp = client.get("/api/dashboard/kpi")
                    assert resp.status_code == 200
                    data = resp.json()
                    
                    # All should have 0 or None values gracefully
                    assert data["coverage_rate"]["percentage"] == 0
                    assert data["accuracy_rate"]["percentage"] == 0
                    assert data["noise_rate"]["percentage"] == 0
                    assert data["reviewable_rate"]["percentage"] == 0
                    # Timeliness could be None or 0 when no data
                    assert data["timeliness_score"]["avg_hours"] is None or \
                           data["timeliness_score"]["avg_hours"] == 0
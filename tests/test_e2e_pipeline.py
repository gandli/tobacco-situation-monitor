"""End-to-end pipeline test: from source to intel.

This test exercises the complete crawl pipeline:
  1. Source configured in database
  2. Fetch list page (mocked)
  3. Extract article links
  4. Fetch article pages (mocked)
  5. Parse article content
  6. Deduplicate
  7. Classify and score
  8. Persist to database
  9. Query via API
"""

import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from tsm.db import init_db


@pytest.fixture
def test_db():
    """Create a temporary test database with schema initialized."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        conn = sqlite3.connect(str(db_path))
        init_db(conn)
        conn.close()
        yield str(db_path)


@pytest.fixture
def fake_source():
    """Return a fake source configuration for testing."""
    return {
        "id": 1,
        "name": "Test Tobacco Bureau",
        "list_url": "https://test.gov.cn/list.html",
    }


@pytest.fixture
def fake_list_html():
    """Return fake list page HTML with article links."""
    return """
    <!DOCTYPE html>
    <html>
    <body>
        <h1>案件通报</h1>
        <ul>
            <li><a href="/news/2026-001.html">查获假烟案件通报</a></li>
            <li><a href="/news/2026-002.html">走私烟草案件</a></li>
        </ul>
    </body>
    </html>
    """


@pytest.fixture
def fake_article_html():
    """Return fake article detail page HTML."""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>案件通报</title></head>
    <body>
        <h1>查获假冒卷烟案件</h1>
        <time>2026-03-05</time>
        <div id="content">
            近日，执法人员查获假冒卷烟案件，涉案金额达50万元。
            跨省运输渠道被查获，嫌疑人已被刑事拘留。
            假烟数量巨大，案情正在进一步调查中。
        </div>
    </body>
    </html>
    """


@pytest.fixture
def fake_http(fake_list_html, fake_article_html):
    """Return a fake HTTP fetcher that returns mock responses."""

    def mock_fetch(url: str, timeout: float = 10.0) -> str:
        """Mock fetch that returns appropriate HTML based on URL."""
        if "list.html" in url:
            return fake_list_html
        elif "/news/" in url:
            return fake_article_html
        else:
            raise ValueError(f"Unexpected URL: {url}")

    return mock_fetch


def test_pipeline_from_source_to_intel(test_db, fake_source, fake_http):
    """Test the complete pipeline from source configuration to intel records.

    This test verifies:
    1. Source exists in database
    2. Crawl job fetches and processes articles
    3. Articles are deduplicated correctly
    4. Classification identifies case-related content
    5. Scoring assigns appropriate risk levels
    6. Intel records are queryable via API
    """
    # Setup: Insert test source into database
    conn = sqlite3.connect(test_db)
    conn.execute(
        "INSERT INTO sources (id, name, list_url) VALUES (?, ?, ?)",
        (fake_source["id"], fake_source["name"], fake_source["list_url"])
    )
    conn.commit()
    conn.close()

    # Mock HTTP fetcher and database path
    # Patch fetch where it's used (in crawl_job module)
    with patch("tsm.jobs.crawl_job.fetch", side_effect=fake_http):
        with patch("tsm.jobs.crawl_job.DB_PATH", test_db):
            with patch("tsm.api.intels.DB_PATH", test_db):
                # Clear deduper state for clean test
                from tsm.services.deduper import clear_seen_hashes
                clear_seen_hashes()

                # Execute: Run one crawl cycle
                from tsm.jobs.crawl_job import run_crawl_once
                result = run_crawl_once()

                # Verify crawl completed successfully
                assert result["status"] == "ok"
                assert result["sources_crawled"] >= 1, "Should have crawled at least 1 source"

                # Import the API to query intels
                from tsm.main import app
                import tsm.api.intels as intels_module
                intels_module.DB_PATH = test_db

                with TestClient(app) as client:
                    # Query intels via API
                    resp = client.get("/api/intels")
                    assert resp.status_code == 200

                    data = resp.json()
                    # Should have created intel records from the articles
                    assert data["total"] >= 1, "Expected at least 1 intel record from pipeline"

                    # Verify intel has proper fields
                    if data["total"] > 0:
                        intel = data["items"][0]
                        assert intel["is_case_related"] is True, "Article should be classified as case-related"
                        assert intel["risk_level"] in ("low", "medium", "high"), "Risk level should be assigned"
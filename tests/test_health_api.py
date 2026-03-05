"""Tests for health check API endpoints.

Comprehensive tests for health check, readiness, and liveness probes.
"""

import sqlite3
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tsm.api.health import HealthStatus, router
from tsm.config import Settings
from tsm.database import get_db_connection


@pytest.fixture
def app() -> FastAPI:
    """Create test FastAPI app with health router."""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create test client."""
    return TestClient(app)


class TestBasicHealthCheck:
    """Tests for basic health check endpoint."""

    def test_health_check_returns_healthy(self, client: TestClient) -> None:
        """Health check should return healthy status."""
        response = client.get("/health/")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == HealthStatus.HEALTHY
        assert "timestamp" in data
        assert "service" in data

    def test_health_check_has_iso_timestamp(self, client: TestClient) -> None:
        """Health check should return ISO format timestamp."""
        response = client.get("/health/")
        data = response.json()

        # ISO format should contain 'T' separator
        assert "T" in data["timestamp"]


class TestReadinessProbe:
    """Tests for readiness probe endpoint."""

    def test_readiness_healthy_with_database(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Readiness should be healthy when database is available."""
        db_path = str(tmp_path / "test.db")

        with patch("tsm.api.health.DEFAULT_DB_PATH", db_path):
            # Create test database
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE test (id INTEGER)")
            conn.close()

            response = client.get("/health/ready")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == HealthStatus.HEALTHY
            assert "checks" in data
            assert "database" in data["checks"]
            assert data["checks"]["database"]["status"] == HealthStatus.HEALTHY

    def test_readiness_reports_latency(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Readiness should report database latency."""
        db_path = str(tmp_path / "test.db")

        with patch("tsm.api.health.DEFAULT_DB_PATH", db_path):
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE test (id INTEGER)")
            conn.close()

            response = client.get("/health/ready")
            data = response.json()

            assert "latency_ms" in data["checks"]["database"]
            assert isinstance(data["checks"]["database"]["latency_ms"], (int, float))
            assert data["checks"]["database"]["latency_ms"] >= 0


class TestLivenessProbe:
    """Tests for liveness probe endpoint."""

    def test_liveness_returns_alive(self, client: TestClient) -> None:
        """Liveness probe should return alive status."""
        response = client.get("/health/live")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"
        assert "timestamp" in data

    def test_liveness_independent_of_database(
        self, client: TestClient
    ) -> None:
        """Liveness should work even if database is unavailable."""
        with patch("tsm.api.health.get_db_connection") as mock_conn:
            mock_conn.side_effect = Exception("Database unavailable")

            response = client.get("/health/live")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "alive"


class TestDetailedHealth:
    """Tests for detailed health check endpoint."""

    def test_detailed_health_includes_service_info(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Detailed health should include service information."""
        db_path = str(tmp_path / "test.db")

        with patch("tsm.api.health.DEFAULT_DB_PATH", db_path):
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE test (id INTEGER)")
            conn.close()

            response = client.get("/health/detail")

            assert response.status_code == 200
            data = response.json()
            assert "service" in data
            assert "version" in data
            assert "debug" in data

    def test_detailed_health_includes_table_count(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Detailed health should report table count."""
        db_path = str(tmp_path / "test.db")

        with patch("tsm.api.health.DEFAULT_DB_PATH", db_path):
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE users (id INTEGER)")
            conn.execute("CREATE TABLE posts (id INTEGER)")
            conn.close()

            response = client.get("/health/detail")
            data = response.json()

            assert "table_count" in data["checks"]["database"]
            # Note: count may include system tables, so we check >= 2
            assert data["checks"]["database"]["table_count"] >= 2

    def test_detailed_health_handles_missing_articles_table(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Detailed health should handle missing articles table gracefully."""
        db_path = str(tmp_path / "test.db")

        with patch("tsm.api.health.DEFAULT_DB_PATH", db_path):
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE other (id INTEGER)")
            conn.close()

            response = client.get("/health/detail")
            data = response.json()

            assert "article_count" in data["checks"]["database"]
            assert data["checks"]["database"]["article_count"] == 0


class TestHealthStatusValues:
    """Tests for health status constants."""

    def test_health_status_values(self) -> None:
        """Verify health status constants."""
        assert HealthStatus.HEALTHY == "healthy"
        assert HealthStatus.DEGRADED == "degraded"
        assert HealthStatus.UNHEALTHY == "unhealthy"


class TestDatabaseErrors:
    """Tests for database error handling."""

    def test_readiness_handles_database_error(
        self, client: TestClient
    ) -> None:
        """Readiness should handle database errors gracefully."""
        with patch("tsm.api.health.get_db_connection") as mock_conn:
            mock_conn.side_effect = sqlite3.Error("Database locked")

            response = client.get("/health/ready")

            assert response.status_code == 503
            data = response.json()
            assert "detail" in data

    def test_detailed_health_handles_database_error(
        self, client: TestClient
    ) -> None:
        """Detailed health should handle database errors gracefully."""
        with patch("tsm.api.health.get_db_connection") as mock_conn:
            mock_conn.side_effect = sqlite3.Error("Database corrupted")

            response = client.get("/health/detail")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == HealthStatus.DEGRADED
            assert data["checks"]["database"]["status"] == HealthStatus.UNHEALTHY
            assert "error" in data["checks"]["database"]
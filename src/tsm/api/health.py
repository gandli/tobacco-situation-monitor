"""Health check endpoints for TSM.

Provides health check and readiness probes for container orchestration.
"""

import sqlite3
import time
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, status

from tsm.config import settings
from tsm.database import DEFAULT_DB_PATH, get_db_connection

router = APIRouter(prefix="/health", tags=["health"])


class HealthStatus:
    """Health status constants."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@router.get(
    "/",
    response_model=dict[str, Any],
    summary="Basic health check",
    description="Returns basic health status for load balancer checks.",
)
async def health_check() -> dict[str, Any]:
    """Basic health check endpoint.

    Returns:
        Simple status indicating the service is running.
    """
    return {
        "status": HealthStatus.HEALTHY,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": settings.app_name,
    }


@router.get(
    "/ready",
    response_model=dict[str, Any],
    summary="Readiness probe",
    description="Checks if the service is ready to accept requests (database available).",
)
async def readiness_probe() -> dict[str, Any]:
    """Readiness probe for Kubernetes/container orchestration.

    Checks:
    - Database connectivity
    - Database responsiveness

    Returns:
        Detailed health status with component checks.

    Raises:
        HTTPException: If any critical component is unhealthy.
    """
    checks: dict[str, Any] = {}
    overall_status = HealthStatus.HEALTHY

    # Check database
    try:
        start_time = time.time()
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT 1")
            cursor.fetchone()
        latency_ms = round((time.time() - start_time) * 1000, 2)

        checks["database"] = {
            "status": HealthStatus.HEALTHY,
            "latency_ms": latency_ms,
        }
    except Exception as e:
        checks["database"] = {
            "status": HealthStatus.UNHEALTHY,
            "error": str(e),
        }
        overall_status = HealthStatus.UNHEALTHY

    if overall_status == HealthStatus.UNHEALTHY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": overall_status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "checks": checks,
            },
        )

    return {
        "status": overall_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": settings.app_name,
        "checks": checks,
    }


@router.get(
    "/live",
    response_model=dict[str, Any],
    summary="Liveness probe",
    description="Checks if the service process is alive (does not check dependencies).",
)
async def liveness_probe() -> dict[str, Any]:
    """Liveness probe for Kubernetes/container orchestration.

    This is a simple check that the process is running.
    If this fails, the container should be restarted.

    Returns:
        Simple alive status.
    """
    return {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get(
    "/detail",
    response_model=dict[str, Any],
    summary="Detailed health check",
    description="Returns comprehensive health information including system metrics.",
)
async def detailed_health() -> dict[str, Any]:
    """Detailed health check with system information.

    Returns:
        Comprehensive health status including:
        - Service info
        - Database status
        - System metrics
    """
    checks: dict[str, Any] = {}

    # Database check with details
    try:
        start_time = time.time()
        with get_db_connection() as conn:
            # Get table count
            cursor = conn.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
            )
            table_count = cursor.fetchone()[0]

            # Get article count (if exists)
            try:
                cursor = conn.execute("SELECT COUNT(*) FROM articles")
                article_count = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                article_count = 0

        latency_ms = round((time.time() - start_time) * 1000, 2)

        checks["database"] = {
            "status": HealthStatus.HEALTHY,
            "latency_ms": latency_ms,
            "table_count": table_count,
            "article_count": article_count,
        }
    except Exception as e:
        checks["database"] = {
            "status": HealthStatus.UNHEALTHY,
            "error": str(e),
        }

    # Determine overall status
    all_healthy = all(
        check.get("status") == HealthStatus.HEALTHY
        for check in checks.values()
    )
    overall_status = HealthStatus.HEALTHY if all_healthy else HealthStatus.DEGRADED

    return {
        "status": overall_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": settings.app_name,
        "version": settings.version,
        "debug": settings.debug,
        "checks": checks,
    }
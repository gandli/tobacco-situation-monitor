"""Main FastAPI application for TSM."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from tsm.api import alerts, analytics, dashboard, health, intels, review, sources, trends
from tsm.config import settings
from tsm.exceptions import DatabaseError
from tsm.logging_config import get_logger, setup_logging

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup/shutdown events."""
    # Startup
    setup_logging(level=settings.log_level, log_file=settings.log_file)
    logger.info(f"Starting {settings.app_name} v{settings.version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Database: {settings.database_path}")

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")


app = FastAPI(
    title="TSM - Tobacco Situation Monitor",
    description="OSINT-powered surveillance system for tobacco law enforcement",
    version=settings.version,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler for database errors
@app.exception_handler(DatabaseError)
async def database_error_handler(request: Request, exc: DatabaseError):
    """Handle database errors globally."""
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Database operation failed. Please try again later."}
    )

# Include routers
app.include_router(health.router)
app.include_router(sources.router)
app.include_router(review.router)
app.include_router(dashboard.router)
app.include_router(intels.router)
app.include_router(analytics.router)
app.include_router(trends.router)
app.include_router(alerts.router)
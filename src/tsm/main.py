"""Main FastAPI application for TSM."""

from fastapi import FastAPI

from tsm.api import dashboard, health, intels, review, sources
from tsm.config import settings, setup_logging

# Setup logging at application startup
setup_logging()

app = FastAPI(title=settings.app_title, version=settings.app_version)
app.include_router(health.router)
app.include_router(sources.router)
app.include_router(review.router)
app.include_router(dashboard.router)
app.include_router(intels.router)

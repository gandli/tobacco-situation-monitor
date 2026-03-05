"""Main FastAPI application for TSM."""

from fastapi import FastAPI

from tsm.api import dashboard, health, intels, review, sources

app = FastAPI(title="TSM")
app.include_router(health.router)
app.include_router(sources.router)
app.include_router(review.router)
app.include_router(dashboard.router)
app.include_router(intels.router)
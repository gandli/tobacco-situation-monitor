"""Main FastAPI application for TSM."""

from fastapi import FastAPI

from tsm.api import review, sources

app = FastAPI(title="TSM")
app.include_router(sources.router)
app.include_router(review.router)
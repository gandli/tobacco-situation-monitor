"""Main FastAPI application for TSM."""

from fastapi import FastAPI

from tsm.api import sources

app = FastAPI(title="TSM")
app.include_router(sources.router)
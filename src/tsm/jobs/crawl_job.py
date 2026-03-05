"""Crawl job entry point."""

from tsm.config import settings


def run_crawl_once() -> dict:
    """Execute one crawl cycle. Returns summary of what was done."""
    # Placeholder - actual implementation in later tasks
    return {"status": "ok", "sources": settings.sources if hasattr(settings, "sources") else []}
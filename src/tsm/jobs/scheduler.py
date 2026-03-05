"""Hourly scheduler for crawl jobs."""

from apscheduler.schedulers.background import BackgroundScheduler

from tsm.jobs.crawl_job import run_crawl_once


def build_scheduler() -> BackgroundScheduler:
    """Build and configure the scheduler with hourly crawl job."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_crawl_once, "interval", hours=1, id="crawl_hourly")
    return scheduler
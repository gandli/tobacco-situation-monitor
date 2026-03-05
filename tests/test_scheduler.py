"""Tests for the hourly crawl scheduler."""

from tsm.jobs.scheduler import build_scheduler


def test_scheduler_registers_hourly_job():
    """Verify the scheduler has an hourly crawl job registered."""
    scheduler = build_scheduler()
    jobs = scheduler.get_jobs()
    assert any(
        hasattr(j.trigger, "interval") and j.trigger.interval.total_seconds() == 3600
        for j in jobs
    ), "No hourly job found in scheduler"
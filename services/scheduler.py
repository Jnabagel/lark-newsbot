"""Scheduler service for automatic NewsBot runs."""

import logging
import sys
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.router import Router

logger = logging.getLogger(__name__)


class NewsScheduler:
    """Scheduler for automatic NewsBot execution."""

    def __init__(self, router: Router):
        """
        Initialize scheduler.

        Args:
            router: Router instance with NewsBot
        """
        self.router = router
        self.scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Hong_Kong'))
        self._setup_job()
        logger.info("Initialized NewsScheduler")

    def _setup_job(self):
        """Set up the daily NewsBot job at 7:30 AM HKT."""
        # Schedule NewsBot to run daily at 7:30 AM Hong Kong time
        self.scheduler.add_job(
            func=self._run_newsbot,
            trigger=CronTrigger(hour=7, minute=30, timezone=pytz.timezone('Asia/Hong_Kong')),
            id='daily_newsbot',
            name='Daily NewsBot at 7:30 AM HKT',
            replace_existing=True
        )
        logger.info("Scheduled NewsBot to run daily at 7:30 AM HKT")

    def _run_newsbot(self):
        """Execute NewsBot (called by scheduler)."""
        try:
            logger.info("Scheduled NewsBot run triggered")
            result = self.router.handle_news_request()
            if result.get("success"):
                logger.info(f"Scheduled NewsBot completed successfully. Headlines: {result.get('headlines_count')}")
            else:
                logger.error(f"Scheduled NewsBot failed: {result.get('error')}")
        except Exception as e:
            logger.error(f"Error in scheduled NewsBot run: {e}", exc_info=True)

    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("NewsScheduler started")
        else:
            logger.warning("Scheduler is already running")

    def stop(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("NewsScheduler stopped")
        else:
            logger.warning("Scheduler is not running")

    def get_next_run_time(self):
        """Get the next scheduled run time."""
        job = self.scheduler.get_job('daily_newsbot')
        if job:
            return job.next_run_time
        return None

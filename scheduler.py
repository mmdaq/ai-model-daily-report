import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from config import SCHEDULE_HOUR, SCHEDULE_MINUTE

logger = logging.getLogger(__name__)


def start_scheduler(job_func) -> None:
    scheduler = BlockingScheduler()
    scheduler.add_job(
        job_func,
        CronTrigger(hour=SCHEDULE_HOUR, minute=SCHEDULE_MINUTE),
        id="daily_report",
        replace_existing=True,
    )
    logger.info(
        "Scheduler started. Daily report at %02d:%02d",
        SCHEDULE_HOUR,
        SCHEDULE_MINUTE,
    )
    scheduler.start()

# cron_jobs.py

import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from typing import Callable, List, Any

logger = logging.getLogger(__name__)

class CronJobManager:
    """Class for managing scheduled cron jobs using APScheduler."""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        logger.info("Cron Job Manager initialized.")

    def close_scheduler(self):
        """Shutdown the scheduler gracefully."""
        self.scheduler.shutdown()
        logger.info("Cron Job Manager shut down.")

    def add_cron_job(self, job_id: str, job_func: Callable, trigger: str, **kwargs):
        """
        Add a cron job to the scheduler.
        :param job_id: Unique identifier for the cron job.
        :param job_func: The function to execute.
        :param trigger: Type of trigger (cron, interval, date, etc.).
        :param kwargs: Additional parameters for job configuration.
        """
        try:
            self.scheduler.add_job(
                func=job_func,
                id=job_id,
                trigger=trigger,
                **kwargs
            )
            logger.info(f"Cron job '{job_id}' added with trigger '{trigger}' and parameters {kwargs}.")
        except Exception as e:
            logger.error(f"Error adding cron job '{job_id}': {e}")
            raise

    def remove_cron_job(self, job_id: str):
        """Remove a scheduled cron job."""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Cron job '{job_id}' removed.")
        except Exception as e:
            logger.error(f"Error removing cron job '{job_id}': {e}")
            raise

    def list_cron_jobs(self) -> List[str]:
        """List all scheduled cron jobs."""
        try:
            jobs = self.scheduler.get_jobs()
            job_list = [job.id for job in jobs if job.id.startswith('cron_job_')]
            logger.info(f"Retrieved all cron jobs. Total: {len(job_list)}")
            return job_list
        except Exception as e:
            logger.error(f"Error listing cron jobs: {e}")
            return []

    def update_cron_job(self, job_id: str, **new_params):
        """Update the configuration of a scheduled cron job."""
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                job.modify(**new_params)
                logger.info(f"Cron job '{job_id}' updated with new parameters: {new_params}")
            else:
                logger.warning(f"Cron job '{job_id}' not found.")
        except Exception as e:
            logger.error(f"Error updating cron job '{job_id}': {e}")
            raise

# Example function to be used as a cron job
def sample_cron_task():
    logger.info("Executing sample cron task at " + str(datetime.now()))

# Example usage:
# cron_manager = CronJobManager()
# cron_manager.add_cron_job('sample_task', sample_cron_task, trigger='interval', minutes=30)
# cron_manager.add_cron_job('daily_report', daily_report_generation, trigger='cron', hour=8, minute=0)
# cron_manager.remove_cron_job('sample_task')
# cron_manager.list_cron_jobs()
# cron_manager.close_scheduler()

# Additional Recommendations:
# 1. Add logging for each cron job execution to capture outcomes.
# 2. Implement task prioritization.
# 3. Allow dynamic job modifications without restarting the scheduler.
# 4. Integrate monitoring for job health/status.
# 5. Enable retries for failed jobs.
# 6. Include audit trails for job changes.
# 7. Implement job chaining for sequential execution.
# 8. Provide visual UI/UX for managing cron jobs.
# 9. Offer support for cron jobs to run at random intervals.
# 10. Introduce pause/resume functionality for long-running jobs.

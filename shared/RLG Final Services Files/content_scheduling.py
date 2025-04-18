# content_scheduling.py

import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ContentScheduler:
    """Class for scheduling content publishing and reminders."""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        logger.info("Content scheduler initialized.")

    def close_scheduler(self):
        """Shutdown the scheduler gracefully."""
        self.scheduler.shutdown()
        logger.info("Content scheduler shut down.")

    def schedule_content(self, content_id: int, publish_time: datetime, callback_function):
        """
        Schedule the publishing of content.
        :param content_id: ID of the content to be published.
        :param publish_time: The time when the content should be published.
        :param callback_function: Function to be called upon publishing.
        """
        try:
            self.scheduler.add_job(
                func=callback_function,
                trigger='date',
                run_date=publish_time,
                args=[content_id],
                id=f'publish_job_{content_id}'
            )
            logger.info(f"Content ID {content_id} scheduled for publishing at {publish_time}.")
        except Exception as e:
            logger.error(f"Error scheduling content ID {content_id}: {e}")
            raise

    def remove_scheduled_content(self, content_id: int):
        """Remove a scheduled content publishing task."""
        try:
            self.scheduler.remove_job(f'publish_job_{content_id}')
            logger.info(f"Content ID {content_id} schedule removed.")
        except Exception as e:
            logger.error(f"Error removing schedule for content ID {content_id}: {e}")
            raise

    def get_scheduled_content(self) -> Dict[int, datetime]:
        """Retrieve all scheduled content and their publishing times."""
        try:
            jobs = self.scheduler.get_jobs()
            scheduled_content = {}
            for job in jobs:
                if job.id.startswith('publish_job_'):
                    content_id = int(job.id.split('_')[-1])
                    scheduled_content[content_id] = job.next_run_time
            logger.info(f"Retrieved all scheduled content. Total: {len(scheduled_content)}")
            return scheduled_content
        except Exception as e:
            logger.error(f"Error retrieving scheduled content: {e}")
            return {}

    def update_scheduled_content_time(self, content_id: int, new_publish_time: datetime):
        """Update the publish time for a scheduled content."""
        try:
            job = self.scheduler.get_job(f'publish_job_{content_id}')
            if job:
                job.reschedule(trigger='date', run_date=new_publish_time)
                logger.info(f"Content ID {content_id} rescheduled for {new_publish_time}.")
            else:
                logger.warning(f"Content ID {content_id} not found in schedule.")
        except Exception as e:
            logger.error(f"Error updating schedule for content ID {content_id}: {e}")
            raise

# Additional Recommendations:
# 1. Implement recurring scheduling options (daily, weekly, monthly).
# 2. Integrate external calendar APIs for syncing content schedules.
# 3. Add notifications/reminders for content scheduling.
# 4. Enable pause/resume functionality for scheduled content.
# 5. Introduce conflict detection to prevent multiple schedules for the same content.
# 6. Allow prioritization of content scheduling.
# 7. Implement logging for content scheduling events.
# 8. Integrate with user authentication to manage scheduling access.
# 9. Enable batch content scheduling for multiple items.
# 10. Improve UI/UX for content scheduling to enhance usability.


from celery import Celery
from celery.schedules import crontab
import logging

# Initialize Celery
app = Celery('scheduler', broker='redis://localhost:6379/0', backend='redis://localhost:6379/1')

# Configure Celery
app.conf.update(
    timezone='UTC',
    enable_utc=True,
    beat_schedule={
        # Example of a periodic task
        'update_social_media_metrics': {
            'task': 'tasks.update_metrics',
            'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
        },
        'send_subscription_reminders': {
            'task': 'tasks.send_reminders',
            'schedule': crontab(minute=0, hour=9),  # Every day at 9 AM UTC
        },
        'generate_daily_reports': {
            'task': 'tasks.generate_reports',
            'schedule': crontab(minute=0, hour=23),  # Every day at 11 PM UTC
        },
    }
)

# Set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@app.task
def update_metrics():
    """
    Periodic task to fetch and update social media metrics.
    """
    try:
        logger.info("Running update_metrics task...")
        # Add logic to fetch and update metrics here
        logger.info("Social media metrics updated successfully.")
    except Exception as e:
        logger.error(f"Error updating metrics: {e}", exc_info=True)

@app.task
def send_reminders():
    """
    Periodic task to send subscription reminders.
    """
    try:
        logger.info("Running send_reminders task...")
        # Add logic to send reminders to users
        logger.info("Subscription reminders sent successfully.")
    except Exception as e:
        logger.error(f"Error sending reminders: {e}", exc_info=True)

@app.task
def generate_reports():
    """
    Periodic task to generate and store daily reports.
    """
    try:
        logger.info("Running generate_reports task...")
        # Add logic to generate and store reports
        logger.info("Daily reports generated successfully.")
    except Exception as e:
        logger.error(f"Error generating reports: {e}", exc_info=True)

if __name__ == '__main__':
    # Run standalone scheduling if celery-beat is not used
    from celery import current_app
    from celery.utils.log import get_task_logger
    logger = get_task_logger(__name__)

    logger.info("Starting scheduler...")
    current_app.start(argv=['celery', '-A', 'scheduler', 'worker', '--loglevel=info'])

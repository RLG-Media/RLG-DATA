# celery_tasks.py - Shared Celery Tasks for RLG Data and RLG Fans

import os
import logging
from celery import Celery
from shared.services.email_service import send_email
from shared.analytics.analytics_engine import process_performance_metrics, analyze_trends
from shared.geolocation.geolocation_service import fetch_location_data
from shared.utils.database import save_task_results
from shared.scraping.scraper import scrape_content

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Celery app configuration
celery_app = Celery(
    'rlg_tasks',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

celery_app.conf.update({
    'task_serializer': 'json',
    'result_serializer': 'json',
    'accept_content': ['json'],
    'timezone': 'UTC',
    'enable_utc': True,
    'task_track_started': True,
    'worker_prefetch_multiplier': 1,  # Ensures fair task distribution
    'task_acks_late': True,  # Prevents losing tasks if workers fail
})

# -------------- TASKS --------------

@celery_app.task(bind=True, name='tasks.scrape_platform_content')
def scrape_platform_content(self, platform, username):
    """
    Scrapes content from the specified platform for the given username.
    """
    try:
        logger.info(f"Starting scraping for platform: {platform}, user: {username}")
        scraped_data = scrape_content(platform, username)
        save_task_results('scraping', platform, username, scraped_data)
        logger.info(f"Scraping completed for {username} on {platform}")
        return {'status': 'success', 'data': scraped_data}
    except Exception as e:
        logger.error(f"Error scraping content: {e}")
        self.retry(exc=e, countdown=60, max_retries=3)


@celery_app.task(bind=True, name='tasks.generate_user_report')
def generate_user_report(self, user_id, platform):
    """
    Generates a detailed performance report for a user on a specified platform.
    """
    try:
        logger.info(f"Generating report for user_id: {user_id} on platform: {platform}")
        report_data = process_performance_metrics(user_id, platform)
        save_task_results('report_generation', platform, user_id, report_data)
        logger.info(f"Report generation completed for user_id: {user_id}")
        return {'status': 'success', 'report': report_data}
    except Exception as e:
        logger.error(f"Error generating user report: {e}")
        self.retry(exc=e, countdown=60, max_retries=3)


@celery_app.task(bind=True, name='tasks.analyze_trending_content')
def analyze_trending_content(self, platform):
    """
    Analyzes trending content for a specific platform.
    """
    try:
        logger.info(f"Analyzing trending content for platform: {platform}")
        trends = analyze_trends(platform)
        save_task_results('trend_analysis', platform, None, trends)
        logger.info(f"Trend analysis completed for platform: {platform}")
        return {'status': 'success', 'trends': trends}
    except Exception as e:
        logger.error(f"Error analyzing trends: {e}")
        self.retry(exc=e, countdown=60, max_retries=3)


@celery_app.task(bind=True, name='tasks.send_email_notification')
def send_email_notification(self, recipient_email, subject, content):
    """
    Sends an email notification with the given content.
    """
    try:
        logger.info(f"Sending email to {recipient_email}")
        send_email(recipient_email, subject, content)
        logger.info(f"Email sent to {recipient_email}")
        return {'status': 'success', 'recipient': recipient_email}
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        self.retry(exc=e, countdown=60, max_retries=3)


@celery_app.task(bind=True, name='tasks.fetch_geolocation_data')
def fetch_geolocation_data(self, ip_address):
    """
    Fetches geolocation data for a given IP address.
    """
    try:
        logger.info(f"Fetching geolocation data for IP: {ip_address}")
        location_data = fetch_location_data(ip_address)
        logger.info(f"Geolocation data fetched for IP: {ip_address}")
        return {'status': 'success', 'location': location_data}
    except Exception as e:
        logger.error(f"Error fetching geolocation data: {e}")
        self.retry(exc=e, countdown=60, max_retries=3)


@celery_app.task(bind=True, name='tasks.cleanup_old_tasks')
def cleanup_old_tasks(self):
    """
    Cleans up old task results from the database to maintain scalability.
    """
    try:
        logger.info("Cleaning up old tasks from the database")
        deleted_count = save_task_results.cleanup_old_entries()
        logger.info(f"Cleaned up {deleted_count} old task entries")
        return {'status': 'success', 'deleted_entries': deleted_count}
    except Exception as e:
        logger.error(f"Error cleaning up old tasks: {e}")
        self.retry(exc=e, countdown=60, max_retries=3)

# -------------- TASK UTILITIES --------------

@celery_app.task(bind=True, name='tasks.log_error')
def log_error(self, message):
    """
    Logs an error message.
    """
    logger.error(message)
    return {'status': 'error_logged', 'message': message}

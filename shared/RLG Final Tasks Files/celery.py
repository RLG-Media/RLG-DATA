"""
celery.py

This module sets up the Celery application for asynchronous task processing for RLG Data and RLG Fans.
It provides:
  - Initialization of a Celery app with configuration (broker, backend, serialization, timezone).
  - Example tasks for data scraping and report generation.
  - Robust error handling with automatic retries.
  
Additional Recommendations:
  1. Extend the task definitions with additional functionality (e.g., model retraining, real-time alerts).
  2. Use environment variables or a secure configuration file for sensitive settings.
  3. For production, ensure the broker (e.g., Redis) is secured and consider connection pooling.
  4. Monitor task execution with Celery Flower or similar monitoring tools.
  5. Consider using Celery beat for scheduling periodic tasks.
"""

import os
import logging
from celery import Celery
from celery.exceptions import Retry

# Configure logging for Celery tasks
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("celery.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("CeleryApp")

# Load Celery configuration from environment variables (with default fallbacks)
BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Initialize Celery application
celery_app = Celery("rlg_app", broker=BROKER_URL, backend=RESULT_BACKEND)
celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    # Optional: Configure beat schedule for periodic tasks here.
    # beat_schedule = {
    #     'scrape-data-every-hour': {
    #         'task': 'celery_app.scrape_data_task',
    #         'schedule': 3600.0,
    #     },
    # },
)

# Example Task: Data Scraping
@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def scrape_data_task(self):
    """
    Task to scrape data for RLG Data and RLG Fans asynchronously.
    This task uses functions from the data_scraper module.
    """
    try:
        logger.info("Starting data scraping task...")
        # Import functions dynamically to ensure Celery app context.
        from data_scraper import scrape_data_for_rlg_data, scrape_data_for_rlg_fans

        # You can pass a region parameter if needed (default is "default")
        data_result = scrape_data_for_rlg_data(region="default")
        fans_result = scrape_data_for_rlg_fans(region="default")

        logger.info("Data scraping completed successfully.")
        return {"data": data_result, "fans": fans_result}
    except Exception as e:
        logger.error(f"Error in data scraping task: {e}")
        # Retry the task after 60 seconds up to 3 times.
        raise self.retry(exc=e)

# Example Task: Report Generation
@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def generate_report_task(self):
    """
    Task to generate a report asynchronously using the ReportGenerator.
    """
    try:
        logger.info("Starting report generation task...")
        from report_generator import ReportGenerator
        # Initialize ReportGenerator; you might pass region or other parameters if needed.
        generator = ReportGenerator(region="default")
        report_path = generator.generate_rlg_data_report()
        logger.info(f"Report generated at: {report_path}")
        return {"report_path": report_path}
    except Exception as e:
        logger.error(f"Error in report generation task: {e}")
        raise self.retry(exc=e)

# Optional: Additional Tasks can be defined here (e.g., model retraining, email notifications, etc.)

if __name__ == "__main__":
    logger.info("Starting Celery worker...")
    celery_app.start()

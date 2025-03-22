# task_scheduler.py

from datetime import timedelta
from celery import Celery
from celery.schedules import crontab
from app import create_app
from app.shared.scheduled_content_updates import scheduled_content_updates
from app.analytics.data_analysis import run_data_analysis
from app.services.notifications import send_summary_notifications
from app.data_processing.engagement_metrics import update_engagement_metrics
from app.services.platform_data_fetcher import fetch_all_platform_data
from app.services.recommendation_engine import generate_recommendations

# Initialize Celery with Flask app context
app = create_app()
celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Configure Celery Beat Schedule
celery.conf.beat_schedule = {
    "content_updates": {
        "task": "app.shared.scheduled_content_updates.scheduled_content_updates",
        "schedule": timedelta(hours=1),  # Runs every hour
        "args": (),
    },
    "run_data_analysis": {
        "task": "app.analytics.data_analysis.run_data_analysis",
        "schedule": crontab(hour=0, minute=0),  # Runs daily at midnight
        "args": (),
    },
    "send_summary_notifications": {
        "task": "app.services.notifications.send_summary_notifications",
        "schedule": crontab(hour=8, minute=0),  # Runs daily at 8 AM
        "args": (),
    },
    "update_engagement_metrics": {
        "task": "app.data_processing.engagement_metrics.update_engagement_metrics",
        "schedule": timedelta(minutes=30),  # Runs every 30 minutes
        "args": (),
    },
    "fetch_all_platform_data": {
        "task": "app.services.platform_data_fetcher.fetch_all_platform_data",
        "schedule": timedelta(minutes=45),  # Runs every 45 minutes
        "args": (),
    },
    "generate_recommendations": {
        "task": "app.services.recommendation_engine.generate_recommendations",
        "schedule": crontab(hour=9, minute=30),  # Runs daily at 9:30 AM
        "args": (),
    },
}

@celery.task
def scheduled_content_updates():
    """Triggers scheduled content updates for all platforms."""
    scheduled_content_updates()

@celery.task
def run_data_analysis():
    """Runs daily analytics on collected data."""
    run_data_analysis()
    app.logger.info("Daily data analysis completed.")

@celery.task
def send_summary_notifications():
    """Sends a summary of updates and analytics to admins and users."""
    send_summary_notifications()
    app.logger.info("Daily summary notifications sent.")

@celery.task
def update_engagement_metrics():
    """Updates engagement metrics and recalculates insights."""
    update_engagement_metrics()
    app.logger.info("Engagement metrics updated.")

@celery.task
def fetch_all_platform_data():
    """Fetches data from all integrated platforms."""
    fetch_all_platform_data()
    app.logger.info("Platform data fetched successfully.")

@celery.task
def generate_recommendations():
    """Generates content and engagement recommendations."""
    generate_recommendations()
    app.logger.info("Content recommendations generated.")

# Optional: Task for weekly deep analysis and report generation
@celery.task
def weekly_report():
    """Generates a detailed weekly report for all platforms."""
    run_data_analysis(weekly=True)
    send_summary_notifications(report_type="weekly")
    app.logger.info("Weekly report generated and sent.")

# Adding weekly report task to the beat schedule (every Sunday at 10 AM)
celery.conf.beat_schedule["weekly_report"] = {
    "task": "app.shared.task_scheduler.weekly_report",
    "schedule": crontab(day_of_week="sunday", hour=10, minute=0),
    "args": (),
}

if __name__ == "__main__":
    # Start the Celery Beat scheduler if running this file directly
    celery.start()

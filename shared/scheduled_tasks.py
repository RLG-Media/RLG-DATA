# scheduled_tasks.py

from celery import Celery
from datetime import datetime
import logging
from backend.RLGDATA_backend.data_collection import scrape_platform_data, track_trends
from backend.RLGDATA_backend.analytics import analyze_engagement, calculate_growth_metrics
from backend.RLGFANS_backend.utility.notifications import send_notification
from backend.RLGFANS_backend.utility.recommendation_engine import generate_recommendations
from shared.models import db, ScheduledTaskLog

# Initialize Celery
celery = Celery(__name__)
celery.config_from_object('config')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# List of all integrated platforms for scraping and analysis
PLATFORMS = [
    'OnlyFans', 'Fansly', 'Patreon', 'Sheer', 'Pornhub', 
    'FeetFinder', 'YouFanly', 'Alua', 'Fansify', 
    'Snapchat', 'TikTok', 'YouTube', 'Facebook'
]

@celery.task
def scheduled_scraping_task():
    """
    Scheduled task to scrape data from all integrated platforms.
    """
    try:
        logging.info("Starting scheduled scraping task...")
        
        for platform in PLATFORMS:
            data = scrape_platform_data(platform)
            logging.info(f"Data scraped for {platform}: {data}")

        log_task_execution('scheduled_scraping_task', 'Success')
        logging.info("Scheduled scraping task completed successfully.")
    except Exception as e:
        logging.error(f"Error during scheduled scraping task: {e}")
        log_task_execution('scheduled_scraping_task', 'Failed', str(e))

@celery.task
def scheduled_trend_analysis():
    """
    Scheduled task to analyze trending content across platforms.
    """
    try:
        logging.info("Starting scheduled trend analysis...")
        
        trend_data = track_trends(PLATFORMS)
        logging.info(f"Trend analysis completed. Trends found: {trend_data}")

        log_task_execution('scheduled_trend_analysis', 'Success')
        logging.info("Scheduled trend analysis completed successfully.")
    except Exception as e:
        logging.error(f"Error during scheduled trend analysis: {e}")
        log_task_execution('scheduled_trend_analysis', 'Failed', str(e))

@celery.task
def scheduled_engagement_analysis():
    """
    Scheduled task to analyze engagement metrics across platforms.
    """
    try:
        logging.info("Starting scheduled engagement analysis...")
        
        engagement_data = analyze_engagement(PLATFORMS)
        logging.info(f"Engagement analysis completed: {engagement_data}")

        log_task_execution('scheduled_engagement_analysis', 'Success')
        logging.info("Scheduled engagement analysis completed successfully.")
    except Exception as e:
        logging.error(f"Error during scheduled engagement analysis: {e}")
        log_task_execution('scheduled_engagement_analysis', 'Failed', str(e))

@celery.task
def scheduled_growth_calculation():
    """
    Scheduled task to calculate growth metrics for users and platforms.
    """
    try:
        logging.info("Starting scheduled growth calculation...")
        
        growth_data = calculate_growth_metrics(PLATFORMS)
        logging.info(f"Growth calculation completed: {growth_data}")

        log_task_execution('scheduled_growth_calculation', 'Success')
        logging.info("Scheduled growth calculation completed successfully.")
    except Exception as e:
        logging.error(f"Error during scheduled growth calculation: {e}")
        log_task_execution('scheduled_growth_calculation', 'Failed', str(e))

@celery.task
def scheduled_recommendations_update():
    """
    Scheduled task to generate and update content recommendations for users.
    """
    try:
        logging.info("Starting scheduled recommendations update...")
        
        recommendations = generate_recommendations()
        logging.info(f"Recommendations generated: {recommendations}")

        log_task_execution('scheduled_recommendations_update', 'Success')
        logging.info("Scheduled recommendations update completed successfully.")
    except Exception as e:
        logging.error(f"Error during scheduled recommendations update: {e}")
        log_task_execution('scheduled_recommendations_update', 'Failed', str(e))

@celery.task
def send_daily_summary():
    """
    Sends a daily summary to users, notifying them of key metrics, new trends,
    and other insights relevant to their platform usage.
    """
    try:
        logging.info("Starting daily summary notification task...")
        
        message = "Here's your daily update with recent metrics, trends, and insights."
        send_notification('Daily Summary', message)
        
        log_task_execution('send_daily_summary', 'Success')
        logging.info("Daily summary notification sent successfully.")
    except Exception as e:
        logging.error(f"Error during daily summary notification: {e}")
        log_task_execution('send_daily_summary', 'Failed', str(e))

def log_task_execution(task_name: str, status: str, error: str = None):
    """
    Log each scheduled task execution in the database.
    """
    log_entry = ScheduledTaskLog(
        task_name=task_name,
        status=status,
        error_message=error,
        executed_at=datetime.utcnow()
    )
    db.session.add(log_entry)
    db.session.commit()

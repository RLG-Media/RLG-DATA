from celery import Celery
from models import db, ContentData, TrendAnalysis, MonetizationStrategy, Campaign
from scraping_utils import scrape_platform_content, fetch_trending_keywords
from data_processing import analyze_content_performance, calculate_monetization_impact
from notifications import send_notification
from datetime import datetime
import logging

# Initialize Celery
celery_app = Celery('tasks', broker='redis://redis:6379/0')
celery_app.conf.result_backend = 'redis://redis:6379/0'

logging.basicConfig(level=logging.INFO)

@celery_app.task
def scrape_content_data(platform_id, user_id, platform_name):
    """
    Task to scrape content data from specified platform for a user.
    """
    try:
        logging.info(f"Starting data scrape for platform {platform_name} for user {user_id}")
        content_data = scrape_platform_content(platform_name)
        
        # Store scraped data in the database
        for data in content_data:
            new_content = ContentData(
                platform_id=platform_id,
                content_type=data['content_type'],
                engagement_score=data['engagement_score'],
                monetization_score=data['monetization_score'],
                views=data['views'],
                likes=data['likes'],
                comments=data['comments'],
                shares=data['shares'],
                posted_at=data['posted_at']
            )
            db.session.add(new_content)
        db.session.commit()
        logging.info(f"Scrape and data entry successful for platform {platform_name} for user {user_id}")
    except Exception as e:
        logging.error(f"Error in scrape_content_data: {e}")

@celery_app.task
def analyze_trends(platform_id):
    """
    Task to analyze trending keywords and topics for a platform.
    """
    try:
        logging.info(f"Starting trend analysis for platform {platform_id}")
        trends = fetch_trending_keywords(platform_id)
        
        for trend in trends:
            new_trend = TrendAnalysis(
                platform_id=platform_id,
                keyword=trend['keyword'],
                trend_score=trend['trend_score'],
                trend_analysis_report=trend['report']
            )
            db.session.add(new_trend)
        db.session.commit()
        logging.info(f"Trend analysis completed for platform {platform_id}")
    except Exception as e:
        logging.error(f"Error in analyze_trends: {e}")

@celery_app.task
def optimize_monetization_strategy(platform_id):
    """
    Task to calculate and update monetization strategies based on data.
    """
    try:
        logging.info(f"Optimizing monetization strategies for platform {platform_id}")
        strategies = calculate_monetization_impact(platform_id)
        
        for strategy in strategies:
            new_strategy = MonetizationStrategy(
                platform_id=platform_id,
                strategy_type=strategy['type'],
                suggestion=strategy['suggestion'],
                expected_impact=strategy['impact']
            )
            db.session.add(new_strategy)
        db.session.commit()
        logging.info(f"Monetization strategies updated for platform {platform_id}")
    except Exception as e:
        logging.error(f"Error in optimize_monetization_strategy: {e}")

@celery_app.task
def run_campaign_analysis(campaign_id):
    """
    Task to analyze a campaign's engagement and revenue performance.
    """
    try:
        logging.info(f"Running analysis for campaign {campaign_id}")
        campaign = Campaign.query.get(campaign_id)
        
        if campaign:
            engagement_data = analyze_content_performance(campaign_id)
            campaign.total_engagement = engagement_data['engagement']
            campaign.total_revenue = engagement_data['revenue']
            db.session.commit()
            logging.info(f"Campaign analysis updated for campaign {campaign_id}")
        else:
            logging.warning(f"Campaign {campaign_id} not found for analysis")
    except Exception as e:
        logging.error(f"Error in run_campaign_analysis: {e}")

@celery_app.task
def notify_user_of_updates(user_id, message):
    """
    Task to send notifications to users about updates or recommendations.
    """
    try:
        logging.info(f"Sending notification to user {user_id}")
        send_notification(user_id, message)
        logging.info(f"Notification sent to user {user_id}")
    except Exception as e:
        logging.error(f"Error in notify_user_of_updates: {e}")

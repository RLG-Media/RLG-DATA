# scheduled_content_updates.py

from datetime import datetime
from celery import Celery
from app.services import (
    facebook_service, twitter_service, youtube_service, instagram_service,
    snapchat_service, tiktok_service, onlyfans_service, fansly_service,
    patreon_service, stripchat_service, sheer_service, feetfinder_service,
    youfanly_service, alua_service, fansify_service, zapier_service
)
from app.shared.notifications import send_notification
from app.shared.recommendation_engine import generate_recommendations
from app.shared.analytics import track_performance_metrics
from app import create_app

# Initialize Celery with Flask app context
app = create_app()
celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@celery.task
def update_content(service_name, service_module):
    """Generic task to fetch and update content for a given service."""
    data = service_module.fetch_latest_content()
    if data:
        service_module.process_content(data)
        send_notification(f"{service_name} content updated successfully.")
        # Generate recommendations for the service
        generate_recommendations(service_name, data)
        # Track performance metrics
        track_performance_metrics(service_name, data)
    else:
        app.logger.warning(f"No new content from {service_name}.")

@celery.task
def scheduled_content_updates():
    """Runs all content update tasks periodically."""
    services = {
        "Facebook": facebook_service,
        "Twitter": twitter_service,
        "YouTube": youtube_service,
        "Instagram": instagram_service,
        "Snapchat": snapchat_service,
        "TikTok": tiktok_service,
        "OnlyFans": onlyfans_service,
        "Fansly": fansly_service,
        "Patreon": patreon_service,
        "Stripchat": stripchat_service,
        "Sheer": sheer_service,
        "Feetfinder": feetfinder_service,
        "YouFanly": youfanly_service,
        "Alua": alua_service,
        "Fansify": fansify_service,
    }

    # Iterate through all services and schedule updates
    for service_name, service_module in services.items():
        update_content.delay(service_name, service_module)

    # Notify when all updates are scheduled
    send_notification("All scheduled content updates have been initiated.")
    app.logger.info(f"Scheduled content updates executed at {datetime.now()}")

@celery.task
def trigger_zapier_automation():
    """Triggers Zapier workflows for additional automation."""
    zapier_response = zapier_service.trigger_workflows()
    if zapier_response['status'] == 'success':
        send_notification("Zapier workflows triggered successfully.")
    else:
        app.logger.warning("Failed to trigger Zapier workflows.")

# Optional: Integrate Celery Beat for periodic scheduling

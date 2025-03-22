from celery import Celery
from api_integration import fetch_twitter_data, fetch_facebook_data, fetch_instagram_data, fetch_linkedin_data
from models import SocialMediaData, Project
from app import db
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize Celery
celery = Celery('realtime_tasks', broker='redis://localhost:6379/0')

@celery.task(bind=True)
def fetch_realtime_data(self, project_id):
    """
    Fetch real-time data for a given project by querying social media APIs.
    
    :param project_id: The ID of the project to fetch real-time data for
    :return: None
    """
    try:
        # Fetch the project details from the database
        project = Project.query.get(project_id)
        if not project:
            logging.error(f"Project with ID {project_id} not found.")
            return
        
        # Extract the keywords from the project to monitor
        keywords = project.keywords.split(',')
        logging.info(f"Fetching real-time data for project: {project.name} with keywords: {keywords}")

        # Fetch data from Twitter, Facebook, Instagram, and LinkedIn APIs for each keyword
        for keyword in keywords:
            twitter_data = fetch_twitter_data(keyword)
            facebook_data = fetch_facebook_data(keyword)
            instagram_data = fetch_instagram_data(keyword)
            linkedin_data = fetch_linkedin_data(keyword)
            
            # Save the collected data to the database
            save_social_media_data('twitter', twitter_data, project.id)
            save_social_media_data('facebook', facebook_data, project.id)
            save_social_media_data('instagram', instagram_data, project.id)
            save_social_media_data('linkedin', linkedin_data, project.id)

        logging.info(f"Real-time data fetching completed for project: {project.name}")

    except Exception as e:
        logging.error(f"Error fetching real-time data for project {project_id}: {e}")

def save_social_media_data(platform, data, project_id):
    """
    Save real-time social media data to the database.
    
    :param platform: The social media platform (e.g., 'twitter', 'facebook')
    :param data: The data to save
    :param project_id: The ID of the project associated with the data
    :return: None
    """
    try:
        for item in data:
            # Create a new SocialMediaData entry for each item
            social_data = SocialMediaData(
                platform=platform,
                content=item.get('text', ''),
                raw_data=item,
                project_id=project_id
            )
            db.session.add(social_data)
        db.session.commit()

        logging.info(f"Saved real-time data for {platform} for project ID {project_id}")

    except Exception as e:
        logging.error(f"Error saving data from {platform} for project {project_id}: {e}")

def start_realtime_monitoring(project_id, interval=60):
    """
    Start real-time monitoring for a given project at regular intervals.
    
    :param project_id: The ID of the project to monitor
    :param interval: The interval (in seconds) to fetch real-time data
    :return: None
    """
    try:
        while True:
            # Trigger the Celery task to fetch real-time data
            fetch_realtime_data.delay(project_id)
            logging.info(f"Scheduled real-time data fetch for project ID {project_id}")
            time.sleep(interval)  # Wait for the specified interval before fetching data again

    except Exception as e:
        logging.error(f"Error during real-time monitoring for project {project_id}: {e}")

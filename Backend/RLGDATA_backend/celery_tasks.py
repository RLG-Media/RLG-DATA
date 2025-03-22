from celery import Celery
from adaptive_scraper import adaptive_scrape
from flask_mail import Message
from app import mail
import logging

# Celery configuration
celery = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

# Configure logging
logging.basicConfig(level=logging.INFO)

@celery.task(bind=True, max_retries=3)
def scrape_website(self, url, model, recipient_email=None):
    """
    Celery task for scraping a website using the adaptive scraper model.
    Handles retries and sends notifications when scraping is complete.
    
    :param url: URL to scrape
    :param model: The trained model used for adaptive scraping
    :param recipient_email: Email address to notify upon task completion (optional)
    :return: Scraped data or failure message
    """
    try:
        logging.info(f"Starting scraping for {url}...")
        
        # Perform the scraping using the adaptive scraper
        scraped_data = adaptive_scrape(url, model)

        # Notify the user via email (if email provided)
        if recipient_email:
            send_scraping_notification(recipient_email, url)

        logging.info(f"Scraping completed for {url}.")
        return scraped_data

    except Exception as e:
        logging.error(f"Error occurred while scraping {url}: {e}")
        
        # Retry the task if it fails
        try:
            self.retry(countdown=60, exc=e)
        except Exception as retry_error:
            logging.error(f"Retry failed for {url}: {retry_error}")

        return f"Scraping failed for {url}. Error: {str(e)}"

def send_scraping_notification(recipient_email, url):
    """
    Sends an email notification to the user when the scraping task is complete.
    
    :param recipient_email: The email address to send the notification to
    :param url: The URL that was scraped
    """
    msg = Message("Scraping Completed", sender='your_email@gmail.com', recipients=[recipient_email])
    msg.body = f"The scraping task for {url} has completed successfully."
    mail.send(msg)
    logging.info(f"Notification sent to {recipient_email} for {url}.")

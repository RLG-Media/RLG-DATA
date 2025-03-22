from celery import Celery
from flask import current_app
from flask_mail import Message
from app import mail
import logging
from backend.adaptive_scraper import load_model
from pdf_generator import generate_pdf_report
from visualization import create_mentions_graph, create_sentiment_graph
from backend.email_utils import send_email

# Configure logging
logging.basicConfig(level=logging.INFO)

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

# Celery instance is created in app.py
celery = make_celery(current_app)

@celery.task
def scrape_website(url, model_name):
    """
    Scrapes data from the given URL and processes it with a machine learning model.
    """
    try:
        model = load_model(model_name)
        data = model.scrape_data(url)
        logging.info(f"Successfully scraped data from {url}")
        return data
    except Exception as e:
        logging.error(f"Error scraping data from {url}: {e}")
        return None

@celery.task
def send_notification_email(recipient, subject, body):
    """
    Sends a notification email to the specified recipient.
    """
    try:
        message = Message(subject=subject, recipients=[recipient])
        message.body = body
        mail.send(message)
        logging.info(f"Notification email sent to {recipient}")
    except Exception as e:
        logging.error(f"Error sending email to {recipient}: {e}")

@celery.task
def generate_report_and_send(user_email, project_name):
    """
    Generates a PDF report for the specified project and emails it to the user.
    """
    try:
        pdf_path = generate_pdf_report(project_name)
        subject = f"{project_name} Report"
        body = f"Attached is the latest report for {project_name}."
        send_email(subject, user_email, body, attachments=[pdf_path])
        logging.info(f"Report for {project_name} sent to {user_email}")
    except Exception as e:
        logging.error(f"Error generating report for {project_name} or sending to {user_email}: {e}")

@celery.task
def generate_visualizations(project_id):
    """
    Creates mentions and sentiment analysis visualizations for a project.
    """
    try:
        mentions_graph = create_mentions_graph(project_id)
        sentiment_graph = create_sentiment_graph(project_id)
        logging.info(f"Visualizations generated for project ID {project_id}")
        return {"mentions_graph": mentions_graph, "sentiment_graph": sentiment_graph}
    except Exception as e:
        logging.error(f"Error generating visualizations for project ID {project_id}: {e}")
        return None

@celery.task
def run_periodic_data_refresh():
    """
    Task that periodically refreshes data for active projects.
    """
    try:
        active_projects = get_active_projects()  # Custom function to fetch active projects
        for project in active_projects:
            scrape_website.delay(project.url, project.model_name)
        logging.info("Periodic data refresh completed.")
    except Exception as e:
        logging.error(f"Error during periodic data refresh: {e}")


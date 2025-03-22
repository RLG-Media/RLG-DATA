# tasks.py - Defines background tasks for RLG Fans using Celery

from celery import shared_task, current_task
from datetime import datetime
import logging
from database import db_session
from models import ScrapingTask, ReportGenerationTask
from scraping_utils import scrape_content, analyze_content
from notifications import send_task_notification
from pdf_generator import generate_pdf_report
from recommendations import generate_content_recommendations

# Set up logging for task processing
logging.basicConfig(filename='tasks.log',
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')


@shared_task(bind=True)
def scrape_platform_content(self, platform_name, url, user_id):
    """
    Task to scrape content from a specific platform URL for a user.
    """
    task_id = self.request.id
    logging.info(f"Starting scraping task {task_id} for platform: {platform_name}, URL: {url}")

    # Create a new scraping task record
    scraping_task = ScrapingTask(task_id=task_id, platform=platform_name, url=url, user_id=user_id, status="in-progress")
    db_session.add(scraping_task)
    db_session.commit()

    try:
        # Perform scraping
        scraped_data = scrape_content(platform_name, url)
        scraping_task.result = scraped_data
        scraping_task.status = "completed"
        db_session.commit()
        
        logging.info(f"Scraping task {task_id} completed successfully.")
        send_task_notification(user_id, f"Scraping completed for {platform_name}. Check your dashboard for insights.")
        
        # Trigger analysis on scraped data
        analyze_platform_content.delay(scraped_data, user_id, platform_name)
        
    except Exception as e:
        scraping_task.status = "failed"
        db_session.commit()
        logging.error(f"Scraping task {task_id} failed: {str(e)}")
        send_task_notification(user_id, f"Scraping task failed for {platform_name}. Error: {str(e)}")

    return scraping_task.result


@shared_task(bind=True)
def analyze_platform_content(self, scraped_data, user_id, platform_name):
    """
    Task to analyze scraped content and generate insights.
    """
    task_id = self.request.id
    logging.info(f"Starting analysis for task {task_id} on platform: {platform_name}")

    try:
        analysis_results = analyze_content(scraped_data)
        # Generate a report based on analysis
        report_task = ReportGenerationTask(task_id=task_id, platform=platform_name, user_id=user_id, status="in-progress")
        db_session.add(report_task)
        db_session.commit()

        # Generate PDF report
        pdf_path = generate_pdf_report(analysis_results, f"{platform_name}_analysis_{datetime.now().strftime('%Y%m%d')}.pdf")
        report_task.status = "completed"
        report_task.result_path = pdf_path
        db_session.commit()
        
        logging.info(f"Analysis task {task_id} completed and report generated.")
        send_task_notification(user_id, f"Analysis completed for {platform_name}. Your report is ready.")

    except Exception as e:
        report_task.status = "failed"
        db_session.commit()
        logging.error(f"Analysis task {task_id} failed: {str(e)}")
        send_task_notification(user_id, f"Analysis failed for {platform_name}. Error: {str(e)}")


@shared_task(bind=True)
def generate_content_recommendations_task(self, user_id):
    """
    Task to generate content recommendations based on user account data and analytics.
    """
    task_id = self.request.id
    logging.info(f"Generating content recommendations for user {user_id}.")

    try:
        recommendations = generate_content_recommendations(user_id)
        logging.info(f"Content recommendations generated successfully for user {user_id}.")
        send_task_notification(user_id, "New content recommendations are available in your dashboard.")
        return recommendations

    except Exception as e:
        logging.error(f"Failed to generate content recommendations for user {user_id}: {str(e)}")
        send_task_notification(user_id, f"Failed to generate content recommendations. Error: {str(e)}")
        return None


@shared_task(bind=True)
def generate_performance_report(self, user_id, start_date, end_date):
    """
    Task to generate a performance report for a specified period.
    """
    task_id = self.request.id
    logging.info(f"Starting performance report generation for user {user_id}, period: {start_date} to {end_date}")

    try:
        # Generate report content (this could involve aggregating multiple datasets)
        report_data = analyze_performance(user_id, start_date, end_date)
        pdf_path = generate_pdf_report(report_data, f"performance_report_{user_id}_{start_date}_{end_date}.pdf")
        
        # Save the report in the database (assuming ReportGenerationTask model)
        report_task = ReportGenerationTask(task_id=task_id, user_id=user_id, status="completed", result_path=pdf_path)
        db_session.add(report_task)
        db_session.commit()

        logging.info(f"Performance report generated for user {user_id}.")
        send_task_notification(user_id, "Your performance report is ready.")

    except Exception as e:
        logging.error(f"Failed to generate performance report for user {user_id}: {str(e)}")
        send_task_notification(user_id, f"Failed to generate performance report. Error: {str(e)}")


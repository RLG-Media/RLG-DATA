"""
celeryconfig.py

Celery Configuration for RLG Data & RLG Fans

This file configures Celery to process background tasks across the platform. It ensures
that our system can handle tasks such as:
  - Data scraping jobs
  - AI-driven analysis and insights
  - Compliance checks and reporting
  - Monetization strategies and report generation
  - Newsletter distribution and agent chat bot interactions

Key Features:
  - Loads broker and backend URLs from environment variables.
  - Sets common serialization settings and timezone.
  - Imports all necessary task modules related to scraping, AI analysis, compliance, reporting, newsletter, and chat bot.
  - Defines a beat schedule for periodic tasks.
  
Note: Update the task module paths as needed based on your project structure.
"""

import os
from celery import Celery

# Broker and result backend (using Redis by default)
BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Set timezone (adjust as necessary)
TIMEZONE = 'UTC'

# List of modules containing Celery tasks
TASK_MODULES = [
    'scraper_engine.tasks',
    'ai_analysis.tasks',
    'compliance_services.tasks',
    'reports.tasks',
    'newsletter.tasks',
    'agent_chat.tasks'
]

# Celery configuration settings
celery_config = {
    'broker_url': BROKER_URL,
    'result_backend': RESULT_BACKEND,
    'timezone': TIMEZONE,
    'imports': TASK_MODULES,
    'task_serializer': 'json',
    'result_serializer': 'json',
    'accept_content': ['json'],
    'beat_schedule': {
        # Example: Run a scraping job every hour
        'run-scraping-every-hour': {
            'task': 'scraper_engine.tasks.run_scraping_job',  # update with your real task path
            'schedule': 3600.0,
            'args': ()
        },
        # Example: Run daily AI analysis every day
        'run-ai-analysis-every-day': {
            'task': 'ai_analysis.tasks.run_daily_analysis',  # update with your real task path
            'schedule': 86400.0,
            'args': ()
        },
        # Additional periodic tasks can be added here
    },
}

# Create a new Celery application
celery_app = Celery('rlg_data_celery')
celery_app.config_from_object(celery_config)

if __name__ == '__main__':
    celery_app.start()

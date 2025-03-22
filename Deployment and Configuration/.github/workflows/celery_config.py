from celery import Celery
from celery.schedules import crontab
import os

# Load environment variables
REDIS_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
TASK_DEFAULT_QUEUE = os.getenv("CELERY_DEFAULT_QUEUE", "default")

# Initialize the Celery application
celery_app = Celery(
    "rlg_tasks",
    broker=REDIS_URL,
    backend=RESULT_BACKEND,
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_default_queue=TASK_DEFAULT_QUEUE,
    task_acks_late=True,  # Ensure tasks are not acknowledged until completed
    worker_prefetch_multiplier=1,  # Prevent worker starvation
    beat_schedule={
        # Example scheduled task
        "daily_task_example": {
            "task": "tasks.example_task",
            "schedule": crontab(hour=0, minute=0),  # Runs daily at midnight UTC
            "args": (),
        },
    },
)

# Define a default task route
celery_app.conf.task_routes = {
    "tasks.email_notification": {"queue": "email"},
    "tasks.data_cleanup": {"queue": "maintenance"},
}

# Auto-discover tasks from registered apps
celery_app.autodiscover_tasks(packages=["rlgdata", "rlgfans", "shared"])

@celery_app.task(bind=True)
def debug_task(self):
    """A simple debug task to verify Celery is working."""
    print(f"Request: {self.request!r}")

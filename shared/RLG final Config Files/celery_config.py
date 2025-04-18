"""
celery_config.py
Centralized Celery configuration for task management in RLG Data and RLG Fans.
"""

from celery import Celery
from celery.schedules import crontab
from config import settings
from logging_service import logger

# Celery app initialization
celery_app = Celery(
    "rlg_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone=settings.TIMEZONE,
    enable_utc=True,
    worker_concurrency=settings.CELERY_WORKER_CONCURRENCY,
    task_annotations={"*": {"rate_limit": settings.CELERY_TASK_RATE_LIMIT}},
    result_expires=settings.CELERY_RESULT_EXPIRES,  # Default expiry for task results
)

# Task Routes
celery_app.conf.task_routes = {
    "tasks.send_email": {"queue": "email"},
    "tasks.data_processing": {"queue": "data"},
    "tasks.notification_dispatch": {"queue": "notifications"},
    # Add additional task-specific routes as needed
}

# Periodic Task Schedule (Optional, for beat integration)
celery_app.conf.beat_schedule = {
    "daily-data-sync": {
        "task": "tasks.data_sync",
        "schedule": crontab(hour=2, minute=0),  # Runs daily at 2 AM
        "args": (),
    },
    "hourly-report-generation": {
        "task": "tasks.generate_reports",
        "schedule": crontab(minute=0),  # Runs every hour
        "args": (),
    },
    "clear-expired-cache": {
        "task": "tasks.clear_cache",
        "schedule": crontab(hour="*/6"),  # Runs every 6 hours
        "args": (),
    },
}

# Monitoring (e.g., Flower)
if settings.FLOWER_ENABLED:
    celery_app.conf.update(
        flower_basic_auth=settings.FLOWER_BASIC_AUTH,
    )

# Error Handlers
@celery_app.task(bind=True)
def error_handler(self, exc, task_id, args, kwargs, einfo):
    """
    Global error handler for Celery tasks.
    Logs the error details.
    """
    logger.error(
        f"Task {task_id} failed.\n"
        f"Exception: {exc}\n"
        f"Arguments: {args}\n"
        f"Keyword Arguments: {kwargs}\n"
        f"Traceback: {einfo}"
    )

# Default Task Example
@celery_app.task(bind=True, name="tasks.default_task")
def default_task(self, *args, **kwargs):
    """
    A placeholder default task.
    """
    logger.info(f"Executing default task with args: {args} and kwargs: {kwargs}")
    return {"status": "success", "args": args, "kwargs": kwargs}

# Hooks
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    Hook to dynamically configure periodic tasks after Celery is initialized.
    """
    sender.add_periodic_task(
        crontab(minute="0", hour="0"),  # Midnight task example
        default_task.s(),
        name="Midnight Default Task",
    )

# Custom Utilities
def is_worker_ready() -> bool:
    """
    Checks if the Celery worker is ready to accept tasks.
    """
    try:
        inspector = celery_app.control.inspect()
        active_workers = inspector.active()
        if not active_workers:
            logger.warning("No active Celery workers found.")
            return False
        logger.info(f"Active workers: {list(active_workers.keys())}")
        return True
    except Exception as e:
        logger.error(f"Error checking Celery worker readiness: {e}")
        return False

def run_adhoc_task(task_name: str, *args, **kwargs):
    """
    Runs an ad-hoc Celery task dynamically.
    """
    try:
        task = celery_app.send_task(task_name, args=args, kwargs=kwargs)
        logger.info(f"Task {task_name} triggered with ID {task.id}.")
        return task.id
    except Exception as e:
        logger.error(f"Failed to trigger task {task_name}: {e}")
        return None

# Example Ad-Hoc Task Trigger
if __name__ == "__main__":
    logger.info("Starting Celery configuration test...")
    if is_worker_ready():
        run_adhoc_task("tasks.default_task", {"test": "data"})


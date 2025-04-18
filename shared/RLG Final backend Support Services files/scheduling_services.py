import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError
from typing import Callable, Optional, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("scheduling_services.log"),
        logging.StreamHandler()
    ]
)

class SchedulingService:
    """
    Service class for managing scheduled tasks for RLG Data and RLG Fans.
    Handles task scheduling, execution, and monitoring.
    """

    def __init__(self):
        """
        Initialize the scheduling service with a background scheduler.
        """
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        logging.info("Scheduler initialized and started.")

    def add_task(self, task_id: str, func: Callable, trigger: str, 
                 trigger_args: Dict, args: Optional[tuple] = None, kwargs: Optional[dict] = None):
        """
        Add a new task to the scheduler.

        Args:
            task_id: A unique identifier for the task.
            func: The function to execute.
            trigger: The type of trigger (e.g., 'interval', 'cron', 'date').
            trigger_args: Arguments for the trigger (e.g., interval or cron settings).
            args: Positional arguments for the function.
            kwargs: Keyword arguments for the function.

        Returns:
            None
        """
        try:
            self.scheduler.add_job(
                func=func,
                trigger=trigger,
                id=task_id,
                args=args or (),
                kwargs=kwargs or {},
                **trigger_args
            )
            logging.info("Task '%s' added to the scheduler.", task_id)
        except Exception as e:
            logging.error("Failed to add task '%s': %s", task_id, e)
            raise

    def remove_task(self, task_id: str):
        """
        Remove a task from the scheduler.

        Args:
            task_id: The unique identifier for the task to remove.

        Returns:
            None
        """
        try:
            self.scheduler.remove_job(task_id)
            logging.info("Task '%s' removed from the scheduler.", task_id)
        except JobLookupError:
            logging.warning("Task '%s' not found.", task_id)
        except Exception as e:
            logging.error("Failed to remove task '%s': %s", task_id, e)
            raise

    def get_all_tasks(self):
        """
        Retrieve all scheduled tasks.

        Returns:
            A list of job objects.
        """
        tasks = self.scheduler.get_jobs()
        logging.info("Retrieved %d tasks from the scheduler.", len(tasks))
        return tasks

    def shutdown(self):
        """
        Shutdown the scheduler.

        Returns:
            None
        """
        self.scheduler.shutdown()
        logging.info("Scheduler shut down.")

# Example usage
if __name__ == "__main__":
    def sample_task(task_name):
        logging.info("Executing task: %s", task_name)

    scheduling_service = SchedulingService()

    # Add an interval-based task
    scheduling_service.add_task(
        task_id="example_interval_task",
        func=sample_task,
        trigger="interval",
        trigger_args={"seconds": 10},
        args=("Interval Task",)
    )

    # Add a cron-based task
    scheduling_service.add_task(
        task_id="example_cron_task",
        func=sample_task,
        trigger="cron",
        trigger_args={"hour": 14, "minute": 30},
        args=("Cron Task",)
    )

    # Run for 60 seconds to demonstrate
    try:
        logging.info("Scheduler running. Press Ctrl+C to exit.")
        import time
        time.sleep(60)
    except KeyboardInterrupt:
        logging.info("Scheduler interrupted by user.")
    finally:
        scheduling_service.shutdown()

import pytz
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

class MultiTimezoneScheduler:
    """
    Multi-timezone-aware scheduler for managing tasks across different time zones.
    Supports scheduling and managing tasks for RLG Data and RLG Fans.
    """

    def __init__(self, db_url: str):
        self.scheduler = BackgroundScheduler(
            jobstores={
                'default': SQLAlchemyJobStore(url=db_url)
            },
            executors={
                'default': ThreadPoolExecutor(20)
            },
            timezone=pytz.utc
        )
        self.scheduler.start()

    def add_task(self, func, run_time: datetime, timezone: str, args: list = None, kwargs: dict = None):
        """
        Add a task to the scheduler in a specific timezone.

        :param func: Callable function to execute.
        :param run_time: Datetime object specifying when to run the task.
        :param timezone: String timezone (e.g., 'America/New_York').
        :param args: List of positional arguments for the function.
        :param kwargs: Dictionary of keyword arguments for the function.
        """
        tz = pytz.timezone(timezone)
        localized_time = tz.localize(run_time).astimezone(pytz.utc)

        self.scheduler.add_job(
            func,
            trigger='date',
            run_date=localized_time,
            args=args or [],
            kwargs=kwargs or {}
        )

    def add_recurring_task(self, func, interval_minutes: int, timezone: str, args: list = None, kwargs: dict = None):
        """
        Add a recurring task to the scheduler with an interval in a specific timezone.

        :param func: Callable function to execute.
        :param interval_minutes: Time interval in minutes between executions.
        :param timezone: String timezone (e.g., 'Asia/Tokyo').
        :param args: List of positional arguments for the function.
        :param kwargs: Dictionary of keyword arguments for the function.
        """
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)

        self.scheduler.add_job(
            func,
            trigger='interval',
            minutes=interval_minutes,
            start_date=now,
            timezone=tz,
            args=args or [],
            kwargs=kwargs or {}
        )

    def remove_task(self, job_id: str):
        """
        Remove a task from the scheduler using its job ID.

        :param job_id: Unique identifier of the job.
        """
        self.scheduler.remove_job(job_id)

    def list_scheduled_tasks(self):
        """
        List all scheduled tasks in the scheduler.

        :return: List of scheduled jobs.
        """
        return self.scheduler.get_jobs()

    def shutdown(self):
        """
        Shut down the scheduler.
        """
        self.scheduler.shutdown()

# Example function to demonstrate scheduled tasks
def example_task(message):
    print(f"[Task Executed at {datetime.now()}] {message}")

# Example usage
if __name__ == "__main__":
    db_url = 'sqlite:///scheduler_jobs.db'  # Example database for job persistence
    scheduler = MultiTimezoneScheduler(db_url=db_url)

    try:
        # Add a one-time task in New York timezone
        scheduler.add_task(
            func=example_task,
            run_time=datetime(2025, 1, 31, 10, 0, 0),
            timezone='America/New_York',
            args=["Run this task once in New York timezone"]
        )

        # Add a recurring task in Tokyo timezone every 15 minutes
        scheduler.add_recurring_task(
            func=example_task,
            interval_minutes=15,
            timezone='Asia/Tokyo',
            args=["Recurring task in Tokyo timezone"]
        )

        # List all scheduled tasks
        for job in scheduler.list_scheduled_tasks():
            print(f"Scheduled Job: {job}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        scheduler.shutdown()

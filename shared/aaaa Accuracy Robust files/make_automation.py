import os
import logging
import schedule
import time
from datetime import datetime
from typing import Callable, Dict, List, Optional
import threading
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("automation.log")],
)

class AutomationTask:
    """
    Represents a single automation task with its configuration.
    """

    def __init__(self, name: str, function: Callable, schedule_type: str, schedule_value: Optional[str] = None):
        """
        Initialize an AutomationTask.

        Args:
            name: The name of the automation task.
            function: The callable function for the task.
            schedule_type: Type of scheduling ('daily', 'interval', 'cron', etc.).
            schedule_value: Scheduling value (e.g., time for 'daily', interval duration).
        """
        self.name = name
        self.function = function
        self.schedule_type = schedule_type
        self.schedule_value = schedule_value
        self.job = None

    def __repr__(self):
        return f"AutomationTask(name={self.name}, schedule_type={self.schedule_type}, schedule_value={self.schedule_value})"


class AutomationManager:
    """
    A manager to handle automated tasks and their scheduling.
    """

    def __init__(self):
        """
        Initialize the AutomationManager.
        """
        self.tasks: Dict[str, AutomationTask] = {}
        self.scheduler = BackgroundScheduler()

    def add_task(self, name: str, function: Callable, schedule_type: str, schedule_value: Optional[str] = None):
        """
        Add a new automation task.

        Args:
            name: Task name.
            function: Callable function to execute.
            schedule_type: Type of scheduling ('daily', 'interval', 'cron', etc.).
            schedule_value: Scheduling value.
        """
        if name in self.tasks:
            logging.warning(f"Task with name '{name}' already exists. Overwriting.")
        
        task = AutomationTask(name, function, schedule_type, schedule_value)
        self.tasks[name] = task
        self._schedule_task(task)
        logging.info(f"Added task: {task}")

    def _schedule_task(self, task: AutomationTask):
        """
        Internal method to schedule a task.

        Args:
            task: AutomationTask object.
        """
        if task.schedule_type == "daily" and task.schedule_value:
            hour, minute = map(int, task.schedule_value.split(":"))
            task.job = self.scheduler.add_job(task.function, "cron", hour=hour, minute=minute)
        elif task.schedule_type == "interval" and task.schedule_value:
            interval = int(task.schedule_value)
            task.job = self.scheduler.add_job(task.function, "interval", seconds=interval)
        elif task.schedule_type == "cron" and task.schedule_value:
            task.job = self.scheduler.add_job(task.function, "cron", **self._parse_cron_schedule(task.schedule_value))
        else:
            logging.error(f"Invalid schedule_type or schedule_value for task: {task}")

    def _parse_cron_schedule(self, cron_value: str) -> Dict[str, str]:
        """
        Parse cron-style scheduling value into arguments.

        Args:
            cron_value: Cron-style string (e.g., '*/5 * * * *').

        Returns:
            Dictionary of cron parameters.
        """
        parts = cron_value.split()
        if len(parts) != 5:
            raise ValueError("Invalid cron value. Must have 5 parts.")
        return {
            "minute": parts[0],
            "hour": parts[1],
            "day": parts[2],
            "month": parts[3],
            "day_of_week": parts[4],
        }

    def start(self):
        """
        Start the scheduler.
        """
        logging.info("Starting the automation scheduler...")
        self.scheduler.start()

    def stop(self):
        """
        Stop the scheduler.
        """
        logging.info("Stopping the automation scheduler...")
        self.scheduler.shutdown()

    def remove_task(self, name: str):
        """
        Remove a task by name.

        Args:
            name: The name of the task to remove.
        """
        if name in self.tasks:
            task = self.tasks.pop(name)
            if task.job:
                self.scheduler.remove_job(task.job.id)
            logging.info(f"Removed task: {name}")
        else:
            logging.warning(f"No task found with name '{name}'.")

    def list_tasks(self) -> List[str]:
        """
        List all scheduled tasks.

        Returns:
            List of task names.
        """
        return list(self.tasks.keys())


# Example Tasks
def example_task_one():
    logging.info("Executing Example Task One.")

def example_task_two():
    logging.info("Executing Example Task Two.")


# Example Usage
if __name__ == "__main__":
    manager = AutomationManager()

    # Add daily task
    manager.add_task("Daily Task", example_task_one, "daily", "10:00")

    # Add interval task
    manager.add_task("Interval Task", example_task_two, "interval", "30")

    # Start the manager
    manager.start()

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        manager.stop()

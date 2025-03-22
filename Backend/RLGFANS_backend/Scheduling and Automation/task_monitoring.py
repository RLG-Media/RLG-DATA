# task_monitoring.py - Monitors and logs status of scheduled tasks in RLG Fans

from celery.result import AsyncResult
from celery import current_app as celery_app
import logging
from datetime import datetime
from notifications import send_task_notification

# Configure logging for task monitoring
logging.basicConfig(filename='task_monitoring.log',
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')

class TaskMonitor:
    """
    Monitors the status of tasks scheduled through Celery in RLG Fans.
    """

    @staticmethod
    def get_task_status(task_id):
        """
        Fetch the status of a task by its ID.
        Args:
            task_id (str): The ID of the task.
        Returns:
            dict: Task status information, including ID, status, and result/error if any.
        """
        result = AsyncResult(task_id, app=celery_app)
        status_info = {
            "task_id": task_id,
            "status": result.status,
            "result": None,
            "error": None
        }

        if result.status == "SUCCESS":
            status_info["result"] = result.result
        elif result.status in ["FAILURE", "REVOKED"]:
            status_info["error"] = str(result.result)
            logging.error(f"Task {task_id} failed: {result.result}")

        logging.info(f"Checked task {task_id} - Status: {result.status}")
        return status_info

    @staticmethod
    def notify_task_completion(task_id, user_id, notification_type="completion"):
        """
        Notify the user about task completion or failure.
        Args:
            task_id (str): The ID of the task.
            user_id (int): The ID of the user to notify.
            notification_type (str): Type of notification ("completion" or "failure").
        """
        task_info = TaskMonitor.get_task_status(task_id)
        message = ""

        if notification_type == "completion" and task_info["status"] == "SUCCESS":
            message = f"Task {task_id} completed successfully."
            logging.info(message)
        elif notification_type == "failure" and task_info["status"] in ["FAILURE", "REVOKED"]:
            message = f"Task {task_id} failed. Error: {task_info['error']}"
            logging.warning(message)

        # Send a notification to the user (through email, dashboard, etc.)
        if message:
            send_task_notification(user_id, message)

    @staticmethod
    def retry_failed_task(task_id):
        """
        Retry a failed task based on its ID.
        Args:
            task_id (str): The ID of the failed task.
        Returns:
            str: New task ID if the retry was scheduled successfully, otherwise None.
        """
        result = AsyncResult(task_id, app=celery_app)
        if result.status in ["FAILURE", "REVOKED"]:
            try:
                # Reschedule the failed task
                new_task = result.apply_async()
                logging.info(f"Retried task {task_id}. New task ID: {new_task.id}")
                return new_task.id
            except Exception as e:
                logging.error(f"Failed to retry task {task_id}: {str(e)}")
        else:
            logging.info(f"Task {task_id} is not eligible for retry (status: {result.status})")
        return None

    @staticmethod
    def log_scheduled_tasks():
        """
        Logs a summary of all active and recently completed tasks.
        """
        i = celery_app.control.inspect()
        scheduled = i.scheduled() or {}
        active = i.active() or {}
        reserved = i.reserved() or {}

        logging.info("Scheduled Tasks Summary:")
        for task_set, tasks in {"Scheduled": scheduled, "Active": active, "Reserved": reserved}.items():
            logging.info(f"{task_set} Tasks:")
            for worker, worker_tasks in tasks.items():
                for task in worker_tasks:
                    logging.info(f"Worker: {worker} - Task: {task['name']} - ID: {task['id']} - ETA: {task.get('eta')}")

    @staticmethod
    def get_task_execution_time(task_id):
        """
        Calculate the execution time of a task.
        Args:
            task_id (str): The ID of the task.
        Returns:
            timedelta: Execution time of the task, or None if not available.
        """
        result = AsyncResult(task_id, app=celery_app)
        start_time = result.date_created
        end_time = result.date_done

        if start_time and end_time:
            execution_time = end_time - start_time
            logging.info(f"Task {task_id} execution time: {execution_time}")
            return execution_time
        else:
            logging.info(f"Execution time for task {task_id} is not available.")
            return None

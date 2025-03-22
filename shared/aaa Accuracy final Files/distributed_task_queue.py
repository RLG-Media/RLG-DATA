import logging
from celery import Celery
from celery.result import AsyncResult
from typing import Callable, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("task_queue.log")]
)

class DistributedTaskQueue:
    """
    A distributed task queue for RLG Data and RLG Fans, supporting task execution across social media platforms and services.
    Uses Celery with a broker (e.g., RabbitMQ or Redis) and supports real-time task monitoring and management.
    """

    def __init__(self, broker_url: str, backend_url: str):
        """
        Initialize the distributed task queue.

        Args:
            broker_url: The URL of the broker (e.g., Redis or RabbitMQ).
            backend_url: The URL of the result backend for task tracking.
        """
        self.celery_app = Celery('RLG_Task_Queue', broker=broker_url, backend=backend_url)
        logging.info("DistributedTaskQueue initialized with broker: %s and backend: %s", broker_url, backend_url)

    def register_task(self, func: Callable):
        """
        Register a function as a Celery task.

        Args:
            func: The function to register as a task.

        Returns:
            The registered Celery task.
        """
        task = self.celery_app.task(func)
        logging.info("Task registered: %s", func.__name__)
        return task

    def execute_task(self, task_name: str, *args, **kwargs) -> AsyncResult:
        """
        Execute a registered task asynchronously.

        Args:
            task_name: The name of the task to execute.
            *args: Positional arguments for the task.
            **kwargs: Keyword arguments for the task.

        Returns:
            An AsyncResult object for tracking the task.
        """
        task = self.celery_app.tasks.get(task_name)
        if not task:
            logging.error("Task not found: %s", task_name)
            raise ValueError(f"Task '{task_name}' is not registered.")

        result = task.apply_async(args=args, kwargs=kwargs)
        logging.info("Task executed: %s, Task ID: %s", task_name, result.id)
        return result

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Retrieve the status of a specific task.

        Args:
            task_id: The ID of the task to query.

        Returns:
            A dictionary containing the task status and result (if completed).
        """
        result = AsyncResult(task_id, app=self.celery_app)
        status = {
            "task_id": task_id,
            "state": result.state,
            "result": result.result if result.ready() else None
        }
        logging.info("Task status retrieved: %s", status)
        return status

    def revoke_task(self, task_id: str, terminate: bool = False) -> None:
        """
        Revoke a task.

        Args:
            task_id: The ID of the task to revoke.
            terminate: Whether to terminate the task if it's running.
        """
        self.celery_app.control.revoke(task_id, terminate=terminate)
        logging.info("Task revoked: %s, terminate: %s", task_id, terminate)

# Example usage
def sample_task(x, y):
    """A sample task for demonstration."""
    return x + y

if __name__ == "__main__":
    # Initialize the task queue
    broker = "redis://localhost:6379/0"
    backend = "redis://localhost:6379/0"
    task_queue = DistributedTaskQueue(broker, backend)

    # Register tasks
    registered_task = task_queue.register_task(sample_task)

    # Execute a task
    result = task_queue.execute_task(registered_task.name, 10, 20)
    print(f"Task submitted. Task ID: {result.id}")

    # Check task status
    status = task_queue.get_task_status(result.id)
    print(f"Task status: {status}")

    # Optionally revoke a task
    # task_queue.revoke_task(result.id, terminate=True)

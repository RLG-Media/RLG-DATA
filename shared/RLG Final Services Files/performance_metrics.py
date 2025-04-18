"""
performance_metrics.py
A comprehensive module for monitoring, analyzing, and reporting performance metrics
for RLG Data and RLG Fans.
"""

import time
import logging
import psutil
import platform
import os
from typing import Dict, Any
from functools import wraps
from datetime import datetime

# Initialize logging
logging.basicConfig(
    filename="performance_metrics.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

class PerformanceMetrics:
    """
    A class for collecting and analyzing system and application performance metrics.
    """

    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Gather detailed system information."""
        system_info = {
            "OS": platform.system(),
            "OS Version": platform.version(),
            "Architecture": platform.architecture()[0],
            "Processor": platform.processor(),
            "CPU Cores": psutil.cpu_count(logical=False),
            "Logical CPUs": psutil.cpu_count(logical=True),
            "Memory": f"{round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB",
        }
        logging.info(f"System Info: {system_info}")
        return system_info

    @staticmethod
    def monitor_resource_usage() -> Dict[str, Any]:
        """Monitor CPU, memory, and disk usage."""
        resource_usage = {
            "CPU Usage (%)": psutil.cpu_percent(interval=1),
            "Memory Usage (%)": psutil.virtual_memory().percent,
            "Disk Usage (%)": psutil.disk_usage('/').percent,
        }
        logging.info(f"Resource Usage: {resource_usage}")
        return resource_usage

    @staticmethod
    def log_execution_time(func):
        """
        Decorator to log the execution time of functions.
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            logging.info(
                f"Function `{func.__name__}` executed in {execution_time:.2f} seconds."
            )
            return result

        return wrapper

    @staticmethod
    def log_event(event: str, level: str = "info"):
        """
        Log custom events with varying levels.
        :param event: Description of the event.
        :param level: Log level ('info', 'warning', 'error').
        """
        levels = {
            "info": logging.info,
            "warning": logging.warning,
            "error": logging.error,
        }
        log_func = levels.get(level, logging.info)
        log_func(event)

    @staticmethod
    def calculate_throughput(start_time: float, end_time: float, operations: int) -> float:
        """
        Calculate throughput in operations per second.
        :param start_time: Start timestamp.
        :param end_time: End timestamp.
        :param operations: Total number of operations performed.
        :return: Throughput value.
        """
        elapsed_time = end_time - start_time
        throughput = operations / elapsed_time if elapsed_time > 0 else 0
        logging.info(
            f"Throughput: {throughput:.2f} operations per second "
            f"over {elapsed_time:.2f} seconds."
        )
        return throughput

    @staticmethod
    def error_tracker(func):
        """
        Decorator to track errors in functions.
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_message = f"Error in `{func.__name__}`: {str(e)}"
                logging.error(error_message)
                raise

        return wrapper

    @staticmethod
    def save_metrics_to_file(metrics: Dict[str, Any], filename: str = "metrics.json"):
        """
        Save collected metrics to a JSON file.
        :param metrics: Dictionary of metrics to save.
        :param filename: Output file name.
        """
        import json

        try:
            with open(filename, "w") as file:
                json.dump(metrics, file, indent=4)
            logging.info(f"Metrics saved to {filename}")
        except Exception as e:
            logging.error(f"Failed to save metrics to file: {e}")

# Example usage
if __name__ == "__main__":
    metrics = PerformanceMetrics()

    # Log system information
    system_info = metrics.get_system_info()
    print("System Info:", system_info)

    # Monitor resource usage
    resource_usage = metrics.monitor_resource_usage()
    print("Resource Usage:", resource_usage)

    # Measure throughput
    start = time.time()
    time.sleep(2)  # Simulate some processing
    end = time.time()
    throughput = metrics.calculate_throughput(start, end, operations=100)
    print(f"Throughput: {throughput:.2f} ops/sec")

    # Save metrics
    all_metrics = {"System Info": system_info, "Resource Usage": resource_usage}
    metrics.save_metrics_to_file(all_metrics)

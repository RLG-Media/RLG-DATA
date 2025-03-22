import psutil
import time
import logging
from datetime import datetime
from typing import Dict

class PerformanceMonitor:
    """
    PerformanceMonitor class to monitor system performance metrics including CPU usage,
    memory usage, disk usage, and network I/O. It logs these metrics at configurable intervals.
    """

    def __init__(self, interval: int = 60, log_file: str = 'performance_log.txt') -> None:
        """
        Initializes the PerformanceMonitor with a monitoring interval and a log file.

        Args:
            interval (int): The interval in seconds at which metrics should be collected.
            log_file (str): The file path where performance logs will be stored.
        """
        self.interval = interval
        self.log_file = log_file
        self.setup_logger()

    def setup_logger(self) -> None:
        """
        Configures the logger to record performance metrics.
        """
        self.logger = logging.getLogger('PerformanceMonitor')
        self.logger.setLevel(logging.INFO)
        # Clear any existing handlers to avoid duplicate logs
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        handler = logging.FileHandler(self.log_file)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.info("PerformanceMonitor logger initialized.")

    def get_cpu_usage(self) -> float:
        """
        Retrieves the current CPU usage percentage.

        Returns:
            float: The CPU usage percentage.
        """
        return psutil.cpu_percent(interval=1)

    def get_memory_usage(self) -> Dict[str, float]:
        """
        Retrieves current memory usage statistics.

        Returns:
            Dict[str, float]: A dictionary with keys 'total_memory', 'used_memory',
                              'available_memory', and 'memory_percent'.
        """
        memory = psutil.virtual_memory()
        return {
            'total_memory': memory.total,
            'used_memory': memory.used,
            'available_memory': memory.available,
            'memory_percent': memory.percent
        }

    def get_disk_usage(self) -> Dict[str, float]:
        """
        Retrieves current disk usage statistics.

        Returns:
            Dict[str, float]: A dictionary with keys 'total_disk', 'used_disk',
                              'free_disk', and 'disk_percent'.
        """
        disk = psutil.disk_usage('/')
        return {
            'total_disk': disk.total,
            'used_disk': disk.used,
            'free_disk': disk.free,
            'disk_percent': disk.percent
        }

    def get_network_usage(self) -> Dict[str, int]:
        """
        Retrieves current network I/O statistics.

        Returns:
            Dict[str, int]: A dictionary with keys 'bytes_sent' and 'bytes_received'.
        """
        network = psutil.net_io_counters()
        return {
            'bytes_sent': network.bytes_sent,
            'bytes_received': network.bytes_recv
        }

    def log_performance(self) -> None:
        """
        Logs the current system performance metrics.
        """
        try:
            cpu_usage = self.get_cpu_usage()
            memory_usage = self.get_memory_usage()
            disk_usage = self.get_disk_usage()
            network_usage = self.get_network_usage()

            log_message = (
                f"CPU Usage: {cpu_usage}% | "
                f"Memory: {memory_usage['used_memory']}/{memory_usage['total_memory']} bytes "
                f"({memory_usage['memory_percent']}%) | "
                f"Disk: {disk_usage['used_disk']}/{disk_usage['total_disk']} bytes "
                f"({disk_usage['disk_percent']}%) | "
                f"Network Sent: {network_usage['bytes_sent']} bytes, "
                f"Network Received: {network_usage['bytes_received']} bytes"
            )
            self.logger.info(log_message)
        except Exception as e:
            self.logger.error(f"Failed to log performance: {e}")

    def start_monitoring(self) -> None:
        """
        Starts the continuous monitoring of system performance metrics.
        Runs indefinitely until interrupted (e.g., via KeyboardInterrupt).
        """
        try:
            self.logger.info("Starting performance monitoring.")
            while True:
                self.log_performance()
                time.sleep(self.interval)
        except KeyboardInterrupt:
            self.logger.info("Performance monitoring stopped by user.")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during monitoring: {e}")

# Example usage:
if __name__ == '__main__':
    monitor = PerformanceMonitor(interval=60)
    monitor.start_monitoring()

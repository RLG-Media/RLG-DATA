"""
monitoring_services.py
Comprehensive monitoring services for RLG Data and RLG Fans.
Includes health checks, performance monitoring, logging, and alerting integrations.
"""

import os
import psutil
import time
import socket
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from prometheus_client import Gauge, start_http_server

# Initialize logging
from logging_config import get_logger

logger = get_logger("Monitoring Services")

# Metrics for Prometheus
METRIC_CPU_USAGE = Gauge("cpu_usage", "CPU Usage percentage")
METRIC_MEMORY_USAGE = Gauge("memory_usage", "Memory Usage percentage")
METRIC_DISK_USAGE = Gauge("disk_usage", "Disk Usage percentage")
METRIC_ACTIVE_CONNECTIONS = Gauge("active_connections", "Active Network Connections")
METRIC_APP_HEALTH = Gauge("application_health", "Application Health Status (0=Down, 1=Up)")

# Constants
PROMETHEUS_PORT = 8001
ALERT_THRESHOLD_CPU = 90  # CPU usage percentage
ALERT_THRESHOLD_MEMORY = 85  # Memory usage percentage
ALERT_THRESHOLD_DISK = 90  # Disk usage percentage
CHECK_INTERVAL = 60  # Time in seconds between monitoring checks

class MonitoringService:
    """
    A class to manage monitoring services for RLG Data and RLG Fans.
    """
    def __init__(self):
        self.hostname = socket.gethostname()
        self.ip_address = socket.gethostbyname(self.hostname)

    def system_health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the system's key resources.

        Returns:
            Dict[str, Any]: A dictionary containing system health metrics.
        """
        logger.info("Performing system health check...")
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            active_connections = len(psutil.net_connections(kind="inet"))

            metrics = {
                "cpu_usage": cpu_usage,
                "memory_usage": memory.percent,
                "disk_usage": disk.percent,
                "active_connections": active_connections,
                "timestamp": datetime.utcnow().isoformat(),
            }

            logger.debug(f"Health check metrics: {metrics}")

            # Update Prometheus metrics
            METRIC_CPU_USAGE.set(cpu_usage)
            METRIC_MEMORY_USAGE.set(memory.percent)
            METRIC_DISK_USAGE.set(disk.percent)
            METRIC_ACTIVE_CONNECTIONS.set(active_connections)

            return metrics
        except Exception as e:
            logger.error(f"Error during health check: {e}")
            return {"error": str(e)}

    def application_health_status(self, status: bool) -> None:
        """
        Update the health status of the application.

        Args:
            status (bool): True if the application is healthy, False otherwise.
        """
        logger.info(f"Updating application health status to {'UP' if status else 'DOWN'}.")
        METRIC_APP_HEALTH.set(1 if status else 0)

    def alert_on_thresholds(self, metrics: Dict[str, Any]) -> None:
        """
        Sends alerts if resource usage exceeds predefined thresholds.

        Args:
            metrics (Dict[str, Any]): System metrics from the health check.
        """
        if metrics.get("cpu_usage", 0) > ALERT_THRESHOLD_CPU:
            logger.warning(f"High CPU usage detected: {metrics['cpu_usage']}%")

        if metrics.get("memory_usage", 0) > ALERT_THRESHOLD_MEMORY:
            logger.warning(f"High memory usage detected: {metrics['memory_usage']}%")

        if metrics.get("disk_usage", 0) > ALERT_THRESHOLD_DISK:
            logger.warning(f"High disk usage detected: {metrics['disk_usage']}%")

    def monitor_system(self) -> None:
        """
        Continuously monitor the system's health and log alerts when necessary.
        """
        logger.info("Starting system monitoring service...")
        while True:
            metrics = self.system_health_check()
            self.alert_on_thresholds(metrics)
            time.sleep(CHECK_INTERVAL)

def start_prometheus_server(port: int = PROMETHEUS_PORT) -> None:
    """
    Start the Prometheus HTTP server to expose metrics.

    Args:
        port (int): The port number to serve Prometheus metrics on.
    """
    logger.info(f"Starting Prometheus metrics server on port {port}...")
    try:
        start_http_server(port)
        logger.info("Prometheus metrics server started successfully.")
    except Exception as e:
        logger.error(f"Failed to start Prometheus server: {e}")

if __name__ == "__main__":
    monitoring_service = MonitoringService()

    # Start Prometheus server
    start_prometheus_server()

    # Update initial application health
    monitoring_service.application_health_status(True)

    # Start monitoring loop
    try:
        monitoring_service.monitor_system()
    except KeyboardInterrupt:
        logger.info("Monitoring service interrupted by user.")
    except Exception as e:
        logger.error(f"Monitoring service encountered an error: {e}")
        monitoring_service.application_health_status(False)

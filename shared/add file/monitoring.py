# monitoring.py - System Monitoring and Performance Tracking for RLG Data and RLG Fans

import os
import psutil
import logging
from datetime import datetime
from flask import current_app
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

class SystemMonitor:
    """
    A utility class for monitoring system performance and application health.
    """

    def __init__(self, db_url):
        self.db_url = db_url

    def get_cpu_usage(self):
        """
        Get the current CPU usage as a percentage.
        """
        return psutil.cpu_percent(interval=1)

    def get_memory_usage(self):
        """
        Get the current memory usage.
        """
        memory = psutil.virtual_memory()
        return {
            "total": memory.total,
            "used": memory.used,
            "percent": memory.percent,
        }

    def get_disk_usage(self):
        """
        Get the current disk usage.
        """
        disk = psutil.disk_usage('/')
        return {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent,
        }

    def get_active_connections(self):
        """
        Get the current number of active network connections.
        """
        connections = psutil.net_connections()
        return len(connections)

    def get_database_stats(self):
        """
        Fetch database statistics like total tables and row counts.
        """
        engine = create_engine(self.db_url)
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT table_schema, table_name, table_rows FROM information_schema.tables WHERE table_schema='public'")
            )
            tables = result.fetchall()
            return tables

    def log_system_metrics(self):
        """
        Log CPU, memory, disk usage, and active connections.
        """
        cpu_usage = self.get_cpu_usage()
        memory_usage = self.get_memory_usage()
        disk_usage = self.get_disk_usage()
        active_connections = self.get_active_connections()

        logger.info(f"System Metrics at {datetime.now()}:")
        logger.info(f"CPU Usage: {cpu_usage}%")
        logger.info(f"Memory Usage: {memory_usage['percent']}% (Used: {memory_usage['used']} MB, Total: {memory_usage['total']} MB)")
        logger.info(f"Disk Usage: {disk_usage['percent']}% (Used: {disk_usage['used']} MB, Total: {disk_usage['total']} MB)")
        logger.info(f"Active Network Connections: {active_connections}")

    def monitor_database_performance(self, query, threshold_ms=500):
        """
        Monitor the performance of a specific database query.
        
        Args:
            query: SQL query to execute.
            threshold_ms: The threshold in milliseconds to log if query takes too long.
        """
        engine = create_engine(self.db_url)
        with engine.connect() as connection:
            start_time = datetime.now()
            result = connection.execute(text(query))
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds() * 1000  # convert to ms

            if execution_time > threshold_ms:
                logger.warning(f"Slow database query detected! Time: {execution_time} ms | Query: {query}")
            return result.fetchall()

    def monitor_application_health(self):
        """
        Monitor overall application health by checking critical services, DB connections, and active users.
        """
        try:
            # Check database connectivity
            engine = create_engine(self.db_url)
            with engine.connect() as connection:
                logger.info("Database connection: SUCCESS")

            # Example: Check if the app service is running
            # In a production setup, this can be more extensive, such as checking HTTP endpoints.
            if os.system("systemctl is-active --quiet app_name") == 0:
                logger.info("Application service: RUNNING")
            else:
                logger.warning("Application service: NOT RUNNING")

            # Further checks can include verifying the status of external APIs, etc.
            self.log_system_metrics()  # Log system metrics

        except Exception as e:
            logger.error(f"Application Health Check FAILED: {e}")

    def start_periodic_monitoring(self, interval_seconds=60):
        """
        Start periodic monitoring using Flask's background task or a separate cron job.
        
        Args:
            interval_seconds: Interval in seconds between each monitoring check.
        """
        from flask import current_app
        from celery import Celery

        # Celery app configuration
        celery = Celery(current_app.name, broker=current_app.config['CELERY_BROKER_URL'])
        
        @celery.task
        def periodic_monitor():
            self.monitor_application_health()
        
        # Start periodic tasks using Celery
        periodic_monitor.apply_async((), countdown=interval_seconds)

        logger.info(f"Periodic monitoring started with an interval of {interval_seconds} seconds.")


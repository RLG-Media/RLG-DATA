# system_health_check.py

import psutil
import os
import logging
import time
from datetime import datetime
from your_project_name.config import SYSTEM_HEALTH_CHECK_CONFIG
from your_project_name.error_handling import handle_error
from your_project_name.notification_system import send_notification

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration parameters
CPU_THRESHOLD = SYSTEM_HEALTH_CHECK_CONFIG['CPU_THRESHOLD']
MEMORY_THRESHOLD = SYSTEM_HEALTH_CHECK_CONFIG['MEMORY_THRESHOLD']
DISK_THRESHOLD = SYSTEM_HEALTH_CHECK_CONFIG['DISK_THRESHOLD']
NETWORK_THRESHOLD = SYSTEM_HEALTH_CHECK_CONFIG['NETWORK_THRESHOLD']
HEALTH_CHECK_INTERVAL = SYSTEM_HEALTH_CHECK_CONFIG['HEALTH_CHECK_INTERVAL']

# Critical system services to check
CRITICAL_SERVICES = SYSTEM_HEALTH_CHECK_CONFIG['CRITICAL_SERVICES']


def check_cpu_usage():
    """
    Monitors CPU usage and raises an alert if it exceeds the defined threshold.
    """
    try:
        cpu_usage = psutil.cpu_percent(interval=1)  # Get the CPU usage over 1 second
        logger.info(f"CPU Usage: {cpu_usage}%")
        
        if cpu_usage > CPU_THRESHOLD:
            logger.warning(f"High CPU Usage detected: {cpu_usage}%")
            send_notification("High CPU Usage Alert", f"CPU usage exceeded threshold: {cpu_usage}%")
        else:
            logger.info(f"CPU usage is within the acceptable limit.")
    except Exception as e:
        handle_error(e)
        logger.error("Error occurred while checking CPU usage.")


def check_memory_usage():
    """
    Monitors memory usage and raises an alert if it exceeds the defined threshold.
    """
    try:
        memory_info = psutil.virtual_memory()
        memory_usage = memory_info.percent
        logger.info(f"Memory Usage: {memory_usage}%")
        
        if memory_usage > MEMORY_THRESHOLD:
            logger.warning(f"High Memory Usage detected: {memory_usage}%")
            send_notification("High Memory Usage Alert", f"Memory usage exceeded threshold: {memory_usage}%")
        else:
            logger.info(f"Memory usage is within the acceptable limit.")
    except Exception as e:
        handle_error(e)
        logger.error("Error occurred while checking memory usage.")


def check_disk_usage():
    """
    Monitors disk usage and raises an alert if it exceeds the defined threshold.
    """
    try:
        disk_usage = psutil.disk_usage('/')
        logger.info(f"Disk Usage: {disk_usage.percent}%")
        
        if disk_usage.percent > DISK_THRESHOLD:
            logger.warning(f"High Disk Usage detected: {disk_usage.percent}%")
            send_notification("High Disk Usage Alert", f"Disk usage exceeded threshold: {disk_usage.percent}%")
        else:
            logger.info(f"Disk usage is within the acceptable limit.")
    except Exception as e:
        handle_error(e)
        logger.error("Error occurred while checking disk usage.")


def check_network_activity():
    """
    Monitors network activity and raises an alert if the usage exceeds the defined threshold.
    """
    try:
        network_info = psutil.net_io_counters()
        logger.info(f"Bytes Sent: {network_info.bytes_sent}, Bytes Received: {network_info.bytes_recv}")
        
        if network_info.bytes_sent > NETWORK_THRESHOLD or network_info.bytes_recv > NETWORK_THRESHOLD:
            logger.warning(f"High Network Activity detected. Sent: {network_info.bytes_sent}, Received: {network_info.bytes_recv}")
            send_notification("High Network Activity Alert", f"Network activity exceeded threshold. Sent: {network_info.bytes_sent}, Received: {network_info.bytes_recv}")
        else:
            logger.info(f"Network usage is within the acceptable limits.")
    except Exception as e:
        handle_error(e)
        logger.error("Error occurred while checking network activity.")


def check_critical_services():
    """
    Checks the status of critical system services and raises an alert if any service is down.
    """
    try:
        for service in CRITICAL_SERVICES:
            service_status = check_service_status(service)
            if not service_status:
                logger.error(f"Critical service {service} is down.")
                send_notification(f"Critical Service Down: {service}", f"The service {service} is not running.")
            else:
                logger.info(f"Service {service} is running fine.")
    except Exception as e:
        handle_error(e)
        logger.error("Error occurred while checking critical services.")


def check_service_status(service_name):
    """
    Checks the status of a given system service.
    """
    try:
        # On Linux, we can use the systemctl to check service status (this may need to be adjusted for other OS)
        status = os.system(f"systemctl is-active --quiet {service_name}")
        return status == 0  # Return True if the service is active
    except Exception as e:
        handle_error(e)
        logger.error(f"Error occurred while checking status of service: {service_name}")
        return False


def run_health_check():
    """
    Runs the system health check by checking CPU, memory, disk, network, and critical services.
    """
    try:
        logger.info(f"Starting health check at {datetime.now()}")
        
        check_cpu_usage()
        check_memory_usage()
        check_disk_usage()
        check_network_activity()
        check_critical_services()

        logger.info(f"Health check completed at {datetime.now()}")
    except Exception as e:
        handle_error(e)
        logger.error("Error occurred while running the health check.")


def monitor_system_health():
    """
    Continuously monitors system health at regular intervals.
    """
    try:
        while True:
            run_health_check()
            time.sleep(HEALTH_CHECK_INTERVAL)
    except Exception as e:
        handle_error(e)
        logger.error("System health monitoring stopped due to an error.")


if __name__ == "__main__":
    monitor_system_health()

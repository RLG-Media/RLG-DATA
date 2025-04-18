# performance_monitoring.py

import psutil
import os
import time
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from your_project_name.config import PERFORMANCE_MONITORING_CONFIG
from your_project_name.error_handling import handle_error

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Thresholds for system resource usage
CPU_THRESHOLD = PERFORMANCE_MONITORING_CONFIG['CPU_THRESHOLD']
MEMORY_THRESHOLD = PERFORMANCE_MONITORING_CONFIG['MEMORY_THRESHOLD']
DISK_THRESHOLD = PERFORMANCE_MONITORING_CONFIG['DISK_THRESHOLD']
NETWORK_THRESHOLD = PERFORMANCE_MONITORING_CONFIG['NETWORK_THRESHOLD']

# Email configuration for alerts
ALERT_EMAIL = PERFORMANCE_MONITORING_CONFIG['ALERT_EMAIL']
ALERT_PASSWORD = PERFORMANCE_MONITORING_CONFIG['ALERT_PASSWORD']
ALERT_RECIPIENT = PERFORMANCE_MONITORING_CONFIG['ALERT_RECIPIENT']

# Define the file for logging performance data
PERFORMANCE_LOG_FILE = PERFORMANCE_MONITORING_CONFIG['PERFORMANCE_LOG_FILE']


def send_alert(subject, body):
    """
    Sends an alert email when performance metrics exceed defined thresholds.

    Args:
        subject (str): The subject of the email.
        body (str): The body content of the email.
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = ALERT_EMAIL
        msg['To'] = ALERT_RECIPIENT
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        # Establish a connection to the email server and send the email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(ALERT_EMAIL, ALERT_PASSWORD)
        text = msg.as_string()
        server.sendmail(ALERT_EMAIL, ALERT_RECIPIENT, text)
        server.quit()

        logger.info(f"Alert sent: {subject}")
    except Exception as e:
        handle_error(e)
        logger.error("Failed to send email alert.")


def log_performance_metrics(cpu_usage, memory_usage, disk_usage, network_usage):
    """
    Logs the system performance metrics to a log file.

    Args:
        cpu_usage (float): CPU usage as a percentage.
        memory_usage (float): Memory usage as a percentage.
        disk_usage (float): Disk usage as a percentage.
        network_usage (float): Network usage in bytes.
    """
    try:
        # Log the performance data to the specified log file
        with open(PERFORMANCE_LOG_FILE, 'a') as log_file:
            log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}, {cpu_usage}%, {memory_usage}%, {disk_usage}%, {network_usage} Bytes\n")
        logger.info("Performance metrics logged successfully.")
    except Exception as e:
        handle_error(e)
        logger.error("Failed to log performance metrics.")


def check_performance():
    """
    Checks the system's performance and monitors resource usage. Alerts and logs are generated
    if any resource usage exceeds the defined thresholds.
    """
    try:
        # Get system resource usage using psutil
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        network_usage = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv

        logger.info(f"CPU Usage: {cpu_usage}% | Memory Usage: {memory_usage}% | Disk Usage: {disk_usage}% | Network Usage: {network_usage} bytes")

        # Log the performance metrics
        log_performance_metrics(cpu_usage, memory_usage, disk_usage, network_usage)

        # Check if any resource usage exceeds thresholds and send alert if necessary
        if cpu_usage > CPU_THRESHOLD:
            subject = "CPU Usage Alert!"
            body = f"Warning: CPU usage exceeded the threshold. Current CPU usage is {cpu_usage}%."
            send_alert(subject, body)

        if memory_usage > MEMORY_THRESHOLD:
            subject = "Memory Usage Alert!"
            body = f"Warning: Memory usage exceeded the threshold. Current memory usage is {memory_usage}%."
            send_alert(subject, body)

        if disk_usage > DISK_THRESHOLD:
            subject = "Disk Usage Alert!"
            body = f"Warning: Disk usage exceeded the threshold. Current disk usage is {disk_usage}%. "
            send_alert(subject, body)

        if network_usage > NETWORK_THRESHOLD:
            subject = "Network Usage Alert!"
            body = f"Warning: Network usage exceeded the threshold. Current network usage is {network_usage} bytes."
            send_alert(subject, body)

    except Exception as e:
        handle_error(e)
        logger.error("Failed to check system performance.")


def monitor_performance():
    """
    Monitors system performance continuously and performs the checks at regular intervals.
    """
    try:
        logger.info("Starting performance monitoring...")
        while True:
            check_performance()
            time.sleep(PERFORMANCE_MONITORING_CONFIG['CHECK_INTERVAL'])  # Check every specified interval in seconds
    except Exception as e:
        handle_error(e)
        logger.error("Performance monitoring stopped due to an error.")


if __name__ == "__main__":
    monitor_performance()

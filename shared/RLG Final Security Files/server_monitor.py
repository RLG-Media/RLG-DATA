"""
server_monitor.py

This module monitors the server's performance and health for both RLG Data and RLG Fans.
It captures key system metrics such as CPU usage, memory usage, disk usage, and network I/O
using the psutil library. The module logs these metrics and can be extended to trigger alerts
if thresholds are exceeded.

Run this module as a standalone service or integrate it into your monitoring framework.
"""

import time
import logging
import psutil
import socket
import json
from datetime import datetime

# Configure logging
logger = logging.getLogger("ServerMonitor")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

# Optional: Define thresholds for alerts (customize per region if necessary)
THRESHOLDS = {
    "cpu_usage_percent": 90,       # Alert if CPU usage exceeds 90%
    "memory_usage_percent": 90,    # Alert if Memory usage exceeds 90%
    "disk_usage_percent": 90       # Alert if Disk usage exceeds 90%
}

def get_server_metrics() -> dict:
    """
    Collects current server metrics including CPU, memory, disk, and network I/O.

    Returns:
        dict: A dictionary containing collected system metrics.
    """
    try:
        # CPU usage (percentage)
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # Memory usage
        virtual_mem = psutil.virtual_memory()
        memory_usage = virtual_mem.percent
        
        # Disk usage (for root partition)
        disk_usage = psutil.disk_usage("/").percent
        
        # Network I/O statistics since boot
        net_io = psutil.net_io_counters()
        network_data = {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv
        }
        
        # Uptime (seconds since boot)
        uptime_seconds = time.time() - psutil.boot_time()
        
        # Hostname
        hostname = socket.gethostname()
        
        metrics = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "hostname": hostname,
            "cpu_usage_percent": cpu_usage,
            "memory_usage_percent": memory_usage,
            "disk_usage_percent": disk_usage,
            "network_data": network_data,
            "uptime_seconds": uptime_seconds
        }
        
        logger.debug("Collected server metrics: %s", json.dumps(metrics, indent=2))
        return metrics

    except Exception as e:
        logger.error("Error collecting server metrics: %s", e)
        return {}

def check_thresholds(metrics: dict) -> dict:
    """
    Checks the collected metrics against predefined thresholds and flags any breaches.

    Parameters:
        metrics (dict): The system metrics dictionary.

    Returns:
        dict: A dictionary with alert flags for each metric if thresholds are exceeded.
    """
    alerts = {}
    try:
        if metrics.get("cpu_usage_percent", 0) > THRESHOLDS["cpu_usage_percent"]:
            alerts["cpu_usage"] = "High"
        if metrics.get("memory_usage_percent", 0) > THRESHOLDS["memory_usage_percent"]:
            alerts["memory_usage"] = "High"
        if metrics.get("disk_usage_percent", 0) > THRESHOLDS["disk_usage_percent"]:
            alerts["disk_usage"] = "High"
    except Exception as e:
        logger.error("Error checking thresholds: %s", e)
    return alerts

def log_metrics(metrics: dict, alerts: dict) -> None:
    """
    Logs the collected metrics and any triggered alerts.

    Parameters:
        metrics (dict): The system metrics dictionary.
        alerts (dict): Dictionary containing any threshold alerts.
    """
    log_entry = {
        "metrics": metrics,
        "alerts": alerts
    }
    logger.info("Server Metrics Report:\n%s", json.dumps(log_entry, indent=2))

def run_server_monitor(poll_interval: int = 60) -> None:
    """
    Runs the server monitor in a continuous loop, polling system metrics at defined intervals.

    Parameters:
        poll_interval (int): Time interval (in seconds) between metric collections.
    """
    logger.info("Starting server monitor with poll interval of %d seconds.", poll_interval)
    try:
        while True:
            metrics = get_server_metrics()
            alerts = check_thresholds(metrics)
            log_metrics(metrics, alerts)
            
            # Optionally, trigger alert notifications here if alerts dict is not empty.
            if alerts:
                logger.warning("Threshold alerts triggered: %s", alerts)
                # e.g., call email_alerts.send_alert(...) or integrate with an external alerting system.
            
            time.sleep(poll_interval)
    except KeyboardInterrupt:
        logger.info("Server monitor interrupted by user. Shutting down.")
    except Exception as e:
        logger.error("Server monitor encountered an error: %s", e)

# -------------------------------
# Additional Recommendations:
# -------------------------------
# 1. **Persistent Logging:** For long-term monitoring, consider logging metrics to a file or a time-series database.
# 2. **Alerting Integration:** Integrate with an alerting system (e.g., email, Slack, Prometheus) to notify administrators
#    when critical thresholds are breached.
# 3. **Web Dashboard:** Consider exposing a web API endpoint (e.g., via Flask or FastAPI) to serve real-time metrics to a dashboard.
# 4. **Asynchronous/Parallel Processing:** If monitoring multiple servers or high-frequency sampling is needed, consider asynchronous processing.
# 5. **Security:** Ensure that any exposed monitoring endpoints are secured and that logs do not contain sensitive information.
# 6. **Region-Specific Adjustments:** Adapt threshold values based on region-specific performance baselines if necessary.

# -------------------------------
# Standalone Testing
# -------------------------------
if __name__ == "__main__":
    # Run the server monitor continuously with a 60-second poll interval.
    run_server_monitor(poll_interval=60)

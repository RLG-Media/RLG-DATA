import time
import psutil
import logging
from datetime import datetime
from threading import Thread
from collections import deque
from .database import db_session
from .models import ApplicationPerformance
from .exceptions import PerformanceMonitoringError

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for performance monitoring
MONITOR_INTERVAL = 60  # Seconds between each monitoring check
PERFORMANCE_HISTORY_SIZE = 100  # Store the last N performance data points

# Performance data queue for tracking metrics
cpu_usage_history = deque(maxlen=PERFORMANCE_HISTORY_SIZE)
memory_usage_history = deque(maxlen=PERFORMANCE_HISTORY_SIZE)
disk_usage_history = deque(maxlen=PERFORMANCE_HISTORY_SIZE)

# Function to record system performance metrics (CPU, memory, disk)
def record_performance_metrics():
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        
        # Append metrics to history queues
        cpu_usage_history.append(cpu_usage)
        memory_usage_history.append(memory_usage)
        disk_usage_history.append(disk_usage)
        
        # Log the collected metrics
        logger.info(f"Performance Metrics - CPU: {cpu_usage}% | Memory: {memory_usage}% | Disk: {disk_usage}%")
        
        # Store metrics in the database
        store_performance_metrics(cpu_usage, memory_usage, disk_usage)
    
    except Exception as e:
        logger.error(f"Error recording performance metrics: {str(e)}")
        raise PerformanceMonitoringError("Error recording performance metrics.")

# Function to store performance data in the database
def store_performance_metrics(cpu_usage: float, memory_usage: float, disk_usage: float):
    try:
        # Create a new performance record for the database
        performance_record = ApplicationPerformance(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            timestamp=datetime.utcnow()
        )

        db_session.add(performance_record)
        db_session.commit()
        
        logger.info("Performance metrics stored successfully.")
    
    except Exception as e:
        logger.error(f"Error storing performance metrics in database: {str(e)}")
        raise PerformanceMonitoringError("Error storing performance metrics in database.")

# Function to start the performance monitoring thread
def start_performance_monitoring():
    logger.info("Starting application performance monitoring...")
    while True:
        record_performance_metrics()
        time.sleep(MONITOR_INTERVAL)

# Function to get the latest performance data from the database
def get_latest_performance_data() -> dict:
    try:
        # Fetch the latest performance record from the database
        performance_record = db_session.query(ApplicationPerformance).order_by(ApplicationPerformance.timestamp.desc()).first()
        
        if performance_record:
            return {
                "cpu_usage": performance_record.cpu_usage,
                "memory_usage": performance_record.memory_usage,
                "disk_usage": performance_record.disk_usage,
                "timestamp": performance_record.timestamp.isoformat()
            }
        else:
            logger.warning("No performance data available.")
            return None
    
    except Exception as e:
        logger.error(f"Error retrieving latest performance data: {str(e)}")
        raise PerformanceMonitoringError("Error retrieving latest performance data.")

# Function to retrieve performance metrics history
def get_performance_history() -> dict:
    """Get historical performance metrics for analysis and visualization."""
    try:
        return {
            "cpu_usage": list(cpu_usage_history),
            "memory_usage": list(memory_usage_history),
            "disk_usage": list(disk_usage_history),
        }
    
    except Exception as e:
        logger.error(f"Error retrieving performance history: {str(e)}")
        raise PerformanceMonitoringError("Error retrieving performance history.")

# Function to monitor system health and alert if critical thresholds are reached
def monitor_system_health():
    try:
        # Check if any metric exceeds critical thresholds (example thresholds)
        cpu_threshold = 90  # CPU usage over 90% is considered critical
        memory_threshold = 90  # Memory usage over 90% is considered critical
        disk_threshold = 90  # Disk usage over 90% is considered critical
        
        if (cpu_usage_history and cpu_usage_history[-1] > cpu_threshold) or \
           (memory_usage_history and memory_usage_history[-1] > memory_threshold) or \
           (disk_usage_history and disk_usage_history[-1] > disk_threshold):
            
            logger.warning("Critical system health issue detected!")
            send_alert("Critical system health alert", "One or more system metrics have exceeded the defined thresholds.")
        
    except Exception as e:
        logger.error(f"Error monitoring system health: {str(e)}")
        raise PerformanceMonitoringError("Error monitoring system health.")

# Function to send system health alerts (via email, Slack, etc.)
def send_alert(subject: str, message: str):
    try:
        # This is a placeholder for actual alert functionality (e.g., sending an email or Slack message)
        logger.warning(f"ALERT: {subject} - {message}")
    
    except Exception as e:
        logger.error(f"Error sending alert: {str(e)}")
        raise PerformanceMonitoringError("Error sending system health alert.")

# Function to start the health monitoring thread
def start_system_health_monitoring():
    logger.info("Starting system health monitoring...")
    while True:
        monitor_system_health()
        time.sleep(MONITOR_INTERVAL)

# Function to initialize the performance monitoring and health check threads
def initialize_monitoring():
    try:
        performance_thread = Thread(target=start_performance_monitoring, daemon=True)
        health_thread = Thread(target=start_system_health_monitoring, daemon=True)

        # Start threads
        performance_thread.start()
        health_thread.start()
        
        logger.info("Performance monitoring and health check initialized.")

    except Exception as e:
        logger.error(f"Error initializing monitoring: {str(e)}")
        raise PerformanceMonitoringError("Error initializing monitoring system.")


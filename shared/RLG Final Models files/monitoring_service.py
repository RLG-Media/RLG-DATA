import os
import time
import logging
import psutil
import requests
import json
import redis
import smtplib
import traceback
from email.mime.text import MIMEText
from datetime import datetime
from kubernetes import client, config

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")
SYSTEM_CHECK_INTERVAL = int(os.getenv("SYSTEM_CHECK_INTERVAL", 60))

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MonitoringService")

# Initialize Redis
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Initialize Kubernetes API
try:
    config.load_kube_config()
    v1 = client.CoreV1Api()
except Exception as e:
    logger.warning("Kubernetes configuration not found, skipping cluster monitoring.")
    v1 = None


def send_alert(subject, message):
    """Send an email and Slack alert."""
    try:
        # Email alert
        if ADMIN_EMAIL:
            msg = MIMEText(message)
            msg["Subject"] = subject
            msg["From"] = SMTP_USERNAME
            msg["To"] = ADMIN_EMAIL

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.sendmail(SMTP_USERNAME, ADMIN_EMAIL, msg.as_string())
        
        # Slack alert
        if SLACK_WEBHOOK:
            requests.post(SLACK_WEBHOOK, json={"text": f"*{subject}*\n{message}"})
        
        logger.info(f"Alert sent: {subject}")
    except Exception as e:
        logger.error(f"Failed to send alert: {e}")


def monitor_system():
    """Monitor CPU, memory, and disk usage."""
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage("/").percent
    
    logger.info(f"CPU: {cpu_usage}%, Memory: {memory_usage}%, Disk: {disk_usage}%")
    
    if cpu_usage > 85 or memory_usage > 90 or disk_usage > 90:
        send_alert("System Resource Alert", f"CPU: {cpu_usage}%, Memory: {memory_usage}%, Disk: {disk_usage}%")


def monitor_kubernetes():
    """Monitor Kubernetes pod statuses."""
    if v1:
        try:
            pods = v1.list_pod_for_all_namespaces(watch=False)
            for pod in pods.items:
                if pod.status.phase not in ["Running", "Succeeded"]:
                    send_alert("Kubernetes Pod Alert", f"Pod {pod.metadata.name} is in {pod.status.phase} state.")
        except Exception as e:
            logger.error(f"Kubernetes monitoring error: {e}")


def monitor_redis():
    """Monitor Redis connection and performance."""
    try:
        ping = redis_client.ping()
        if not ping:
            send_alert("Redis Alert", "Redis server is unresponsive!")
        
        memory_usage = redis_client.info("memory")["used_memory"] / (1024 * 1024)
        if memory_usage > 500:
            send_alert("Redis Memory Alert", f"Redis is using {memory_usage:.2f} MB of memory.")
    except Exception as e:
        send_alert("Redis Connection Error", f"Error connecting to Redis: {e}")


def monitor_external_services():
    """Monitor third-party API health."""
    services = {
        "Google": "https://www.google.com",
        "Stripe": "https://api.stripe.com/v1",
        "PayPal": "https://api.paypal.com",
        "RLG API": "https://api.rlgdata.com/health"
    }
    
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                send_alert(f"{name} API Alert", f"{name} API returned status code {response.status_code}")
        except Exception as e:
            send_alert(f"{name} API Error", f"Error connecting to {name}: {e}")


def main():
    """Main loop to continuously monitor services."""
    while True:
        try:
            monitor_system()
            monitor_kubernetes()
            monitor_redis()
            monitor_external_services()
        except Exception as e:
            send_alert("Monitoring Service Error", f"Unexpected error: {traceback.format_exc()}")
        
        time.sleep(SYSTEM_CHECK_INTERVAL)


if __name__ == "__main__":
    logger.info("Starting Monitoring Service for RLG Data & RLG Fans...")
    main()

import requests
import time
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

# Configuration for monitoring
THIRD_PARTY_SERVICES = {
    'Facebook': 'https://graph.facebook.com/v11.0',
    'Instagram': 'https://graph.instagram.com',
    'Twitter': 'https://api.twitter.com',
    'Patreon': 'https://www.patreon.com/api/oauth2',
    'YouTube': 'https://www.googleapis.com/youtube/v3',
    'Shopify': 'https://api.shopify.com',
    'TikTok': 'https://www.tiktok.com/api/v1',
    # Add more services as needed
}

MONITOR_INTERVAL = 5  # Time interval (in minutes) to check the services

# Logging setup
logging.basicConfig(filename='service_monitoring.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_service_health(service_name, url):
    """
    Check the health of a third-party service.
    Returns True if the service is up and running, False otherwise.
    """
    try:
        # Send a GET request to the service's health endpoint
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            logging.info(f'{service_name} is UP. Response time: {response.elapsed.total_seconds()} seconds')
            return True
        else:
            logging.error(f'{service_name} is DOWN. Status code: {response.status_code}')
            return False

    except requests.RequestException as e:
        logging.error(f'{service_name} is DOWN. Error: {str(e)}')
        return False

def log_service_status():
    """
    Logs the status of all third-party services at the specified interval.
    """
    for service_name, url in THIRD_PARTY_SERVICES.items():
        is_up = check_service_health(service_name, url)
        # Here you could integrate with your internal monitoring system or notify users if necessary
        if not is_up:
            send_alert(service_name)

def send_alert(service_name):
    """
    Sends an alert (e.g., email or notification) when a service goes down.
    """
    # Placeholder for sending notifications. You can integrate with email, Slack, etc.
    logging.warning(f'ALERT: {service_name} is down! Immediate action is required.')

def start_monitoring():
    """
    Starts monitoring the third-party services periodically.
    """
    # Set up a background scheduler to monitor services at regular intervals
    scheduler = BackgroundScheduler()
    scheduler.add_job(log_service_status, 'interval', minutes=MONITOR_INTERVAL)
    scheduler.start()

    logging.info("Started third-party service monitoring.")
    
    try:
        # Keep the script running to allow background jobs to continue executing
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        # Gracefully shut down the scheduler when the script is terminated
        scheduler.shutdown()
        logging.info("Third-party service monitoring stopped.")

if __name__ == "__main__":
    start_monitoring()


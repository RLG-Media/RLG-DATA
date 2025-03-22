import logging
import psutil
import time
import requests
from datetime import datetime
from threading import Thread

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("network_monitoring.log"), logging.StreamHandler()]
)

class NetworkMonitoringService:
    """
    A service to monitor network health, performance, and activity for RLG Data and RLG Fans.
    Includes tracking for API uptime, latency, bandwidth usage, and real-time alerts.
    """

    def __init__(self, monitored_urls=None, alert_webhook=None):
        """
        Initialize the network monitoring service.

        Args:
            monitored_urls (list): List of URLs to monitor for uptime and performance.
            alert_webhook (str): Webhook URL to send alerts in case of issues.
        """
        self.monitored_urls = monitored_urls or []
        self.alert_webhook = alert_webhook
        self.network_stats = []

    def monitor_bandwidth(self):
        """
        Monitor network bandwidth usage in real-time.
        """
        try:
            while True:
                stats = psutil.net_io_counters()
                bandwidth_data = {
                    "timestamp": datetime.now().isoformat(),
                    "bytes_sent": stats.bytes_sent,
                    "bytes_received": stats.bytes_recv
                }
                self.network_stats.append(bandwidth_data)
                logging.info("Bandwidth usage: Sent=%s bytes, Received=%s bytes", stats.bytes_sent, stats.bytes_recv)
                time.sleep(5)
        except Exception as e:
            logging.error("Error monitoring bandwidth: %s", e)

    def check_url_health(self, url):
        """
        Check the health of a URL by measuring response time and status.

        Args:
            url (str): The URL to check.

        Returns:
            dict: Health data for the URL.
        """
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            latency = time.time() - start_time

            health_data = {
                "url": url,
                "status_code": response.status_code,
                "latency": latency,
                "timestamp": datetime.now().isoformat()
            }

            logging.info("URL health: %s, Status=%s, Latency=%.2f seconds", url, response.status_code, latency)

            if response.status_code != 200:
                self.send_alert(f"URL {url} returned status {response.status_code}.")

            return health_data
        except requests.RequestException as e:
            logging.error("Error checking URL %s: %s", url, e)
            self.send_alert(f"URL {url} is unreachable: {e}")
            return {
                "url": url,
                "status_code": None,
                "latency": None,
                "timestamp": datetime.now().isoformat()
            }

    def monitor_urls(self):
        """
        Continuously monitor all configured URLs.
        """
        try:
            while True:
                for url in self.monitored_urls:
                    self.check_url_health(url)
                time.sleep(60)
        except Exception as e:
            logging.error("Error in URL monitoring: %s", e)

    def send_alert(self, message):
        """
        Send an alert to the configured webhook.

        Args:
            message (str): The alert message to send.
        """
        if not self.alert_webhook:
            logging.warning("Alert webhook not configured. Skipping alert.")
            return

        try:
            payload = {"text": message}
            response = requests.post(self.alert_webhook, json=payload)

            if response.status_code == 200:
                logging.info("Alert sent successfully: %s", message)
            else:
                logging.error("Failed to send alert: %s", response.text)
        except requests.RequestException as e:
            logging.error("Error sending alert: %s", e)

    def start(self):
        """
        Start network monitoring tasks in separate threads.
        """
        try:
            Thread(target=self.monitor_bandwidth, daemon=True).start()
            Thread(target=self.monitor_urls, daemon=True).start()
            logging.info("Network monitoring service started.")
        except Exception as e:
            logging.error("Error starting network monitoring service: %s", e)

# Example usage
if __name__ == "__main__":
    monitored_urls = [
        "https://rlgdata.com/api/health",
        "https://rlgfans.com/api/health"
    ]
    alert_webhook = "https://hooks.example.com/webhook"

    network_service = NetworkMonitoringService(monitored_urls=monitored_urls, alert_webhook=alert_webhook)
    network_service.start()

    # Keep the main thread alive
    while True:
        time.sleep(1)

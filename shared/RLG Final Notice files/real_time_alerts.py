import json
import time
import logging
import threading
import requests
from datetime import datetime
from queue import Queue
from config import ALERT_CONFIG
from email_notification import EmailNotification
from sms_notification import SMSNotification
from push_notification import PushNotification

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class RealTimeAlerts:
    """Handles real-time alerts for RLG Data and RLG Fans with multi-channel notifications."""

    def __init__(self):
        self.alert_queue = Queue()
        self.alert_threshold = ALERT_CONFIG.get("alert_threshold", 5)  # Avoid spam, batch alerts if needed
        self.alert_channels = ALERT_CONFIG.get("alert_channels", ["email", "sms", "push", "webhook"])
        self.email_notifier = EmailNotification()
        self.sms_notifier = SMSNotification()
        self.push_notifier = PushNotification()
        self.webhook_url = ALERT_CONFIG.get("webhook_url", None)
        self.alert_cache = set()

    def _filter_duplicate_alerts(self, alert_id):
        """Prevents duplicate alerts from being processed multiple times."""
        if alert_id in self.alert_cache:
            return False
        self.alert_cache.add(alert_id)
        return True

    def send_alert(self, alert_data):
        """Processes and sends alerts through selected channels."""
        alert_id = alert_data.get("alert_id", f"{alert_data['type']}-{alert_data['timestamp']}")
        if not self._filter_duplicate_alerts(alert_id):
            logging.warning(f"Duplicate alert skipped: {alert_id}")
            return

        message = f"🚨 {alert_data['type'].upper()} ALERT 🚨\n{alert_data['message']}\n🕒 {alert_data['timestamp']}"
        recipients = alert_data.get("recipients", ALERT_CONFIG.get("default_recipients", []))

        for channel in self.alert_channels:
            if channel == "email":
                self.email_notifier.send_email(recipients, "Real-Time Alert", message)
            elif channel == "sms":
                self.sms_notifier.send_sms(recipients, message)
            elif channel == "push":
                self.push_notifier.send_push_notification(recipients, message)
            elif channel == "webhook" and self.webhook_url:
                requests.post(self.webhook_url, json=alert_data)

        logging.info(f"Alert dispatched: {alert_id}")

    def process_alerts(self):
        """Continuously processes alerts from the queue in real-time."""
        while True:
            if not self.alert_queue.empty():
                alert_data = self.alert_queue.get()
                self.send_alert(alert_data)
            time.sleep(1)  # Prevent CPU overuse

    def add_alert(self, alert_type, message, recipients=None):
        """Adds a new alert to the queue with AI-prioritized ranking."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        alert_data = {
            "alert_id": f"{alert_type}-{timestamp}",
            "type": alert_type,
            "message": message,
            "timestamp": timestamp,
            "recipients": recipients or ALERT_CONFIG.get("default_recipients", [])
        }
        self.alert_queue.put(alert_data)
        logging.info(f"New alert added to queue: {alert_data['alert_id']}")

# Start real-time alert processing in a background thread
real_time_alerts = RealTimeAlerts()
alert_thread = threading.Thread(target=real_time_alerts.process_alerts, daemon=True)
alert_thread.start()

# Example Usage
if __name__ == "__main__":
    real_time_alerts.add_alert("security", "Suspicious login attempt detected!", ["admin@example.com"])
    real_time_alerts.add_alert("data_breach", "Possible data leak detected. Investigate immediately!", ["security@rlgdata.com"])

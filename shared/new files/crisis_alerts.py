import smtplib
import logging
from typing import List, Dict, Callable, Optional
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from textblob import TextBlob
import json

# --- Logger Configuration ---
logging.basicConfig(
    filename="crisis_alerts.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class CrisisAlerts:
    """
    A robust system for detecting and managing crisis alerts.
    """

    def __init__(self, email_config: Dict[str, str], alert_channels: Optional[List[str]] = None):
        """
        Initializes the crisis alert system.
        :param email_config: Configuration for sending email alerts.
        :param alert_channels: List of active alert channels (e.g., 'email', 'sms', 'slack').
        """
        self.email_config = email_config
        self.alert_channels = alert_channels or ["email"]
        self.crisis_keywords = ["crisis", "emergency", "urgent", "issue", "problem"]
        self.sentiment_threshold = -0.3  # Negative sentiment threshold

    # --- Crisis Detection ---
    def detect_crisis(self, content: str) -> bool:
        """
        Detects if a piece of content indicates a crisis.
        :param content: The content to analyze.
        :return: True if a crisis is detected, False otherwise.
        """
        # Check for crisis keywords
        for keyword in self.crisis_keywords:
            if keyword in content.lower():
                logging.info(f"Crisis keyword detected: {keyword}")
                return True

        # Analyze sentiment
        sentiment_score = self.analyze_sentiment(content)
        if sentiment_score < self.sentiment_threshold:
            logging.info(f"Negative sentiment detected: {sentiment_score}")
            return True

        return False

    def analyze_sentiment(self, content: str) -> float:
        """
        Analyzes the sentiment of a given text.
        :param content: The text to analyze.
        :return: Sentiment score (-1.0 to 1.0).
        """
        analysis = TextBlob(content)
        return analysis.sentiment.polarity

    # --- Alert Dispatch ---
    def dispatch_alert(self, alert_message: str):
        """
        Dispatches an alert through active channels.
        :param alert_message: The alert message to send.
        """
        for channel in self.alert_channels:
            if channel == "email":
                self.send_email(alert_message)
            elif channel == "sms":
                self.send_sms(alert_message)
            elif channel == "slack":
                self.send_slack_notification(alert_message)
            else:
                logging.warning(f"Unsupported alert channel: {channel}")

    def send_email(self, message: str):
        """
        Sends an email alert.
        :param message: The email message.
        """
        try:
            msg = MIMEMultipart()
            msg["From"] = self.email_config["from"]
            msg["To"] = self.email_config["to"]
            msg["Subject"] = "Crisis Alert"

            msg.attach(MIMEText(message, "plain"))

            with smtplib.SMTP(self.email_config["server"], self.email_config["port"]) as server:
                server.starttls()
                server.login(self.email_config["username"], self.email_config["password"])
                server.send_message(msg)
            logging.info("Email alert sent successfully.")
        except Exception as e:
            logging.error(f"Failed to send email alert: {e}")

    def send_sms(self, message: str):
        """
        Sends an SMS alert (placeholder for SMS API integration).
        :param message: The SMS message.
        """
        try:
            # Example: Twilio API integration
            # Replace with actual SMS API logic
            logging.info(f"SMS alert sent: {message}")
        except Exception as e:
            logging.error(f"Failed to send SMS alert: {e}")

    def send_slack_notification(self, message: str):
        """
        Sends a Slack notification.
        :param message: The Slack message.
        """
        try:
            webhook_url = "https://hooks.slack.com/services/your/webhook/url"
            payload = {"text": message}
            response = requests.post(webhook_url, data=json.dumps(payload), headers={"Content-Type": "application/json"})
            if response.status_code == 200:
                logging.info("Slack notification sent successfully.")
            else:
                logging.error(f"Failed to send Slack notification: {response.text}")
        except Exception as e:
            logging.error(f"Failed to send Slack notification: {e}")

    # --- Incident Logging ---
    def log_incident(self, message: str, severity: str = "High"):
        """
        Logs a crisis incident.
        :param message: The incident message.
        :param severity: Severity level of the incident.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {"timestamp": timestamp, "message": message, "severity": severity}
        logging.info(f"Incident logged: {log_entry}")
        # Append to external log file if needed

    # --- Example Use Case ---
    def monitor_content(self, contents: List[str]):
        """
        Monitors a list of content for potential crises.
        :param contents: List of content to monitor.
        """
        for content in contents:
            if self.detect_crisis(content):
                alert_message = f"Crisis detected in content: {content}"
                self.dispatch_alert(alert_message)
                self.log_incident(alert_message)


# Example Usage
if __name__ == "__main__":
    email_config = {
        "from": "alerts@rlgdata.com",
        "to": "team@rlgdata.com",
        "server": "smtp.gmail.com",
        "port": 587,
        "username": "your-email@gmail.com",
        "password": "your-password",
    }

    crisis_alerts = CrisisAlerts(email_config=email_config, alert_channels=["email", "slack"])
    sample_contents = [
        "Our servers are down! This is a crisis.",
        "User sentiment is dropping rapidly on Twitter.",
        "Everything is running smoothly today.",
    ]
    crisis_alerts.monitor_content(sample_contents)

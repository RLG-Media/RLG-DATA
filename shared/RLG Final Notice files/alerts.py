import smtplib
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Alerts:
    """
    A utility class for managing alerts and notifications for RLG Data and RLG Fans.
    """

    def __init__(self, smtp_config: Dict[str, str], twilio_config: Dict[str, str], webhook_url: str):
        """
        Initialize the Alerts system with required configurations.

        Args:
            smtp_config (Dict[str, str]): SMTP settings for sending emails.
            twilio_config (Dict[str, str]): Twilio API credentials for sending SMS.
            webhook_url (str): Default webhook URL for push notifications.
        """
        self.smtp_config = smtp_config
        self.twilio_config = twilio_config
        self.webhook_url = webhook_url
        self.alert_log = []

    def send_email(self, recipient: str, subject: str, message: str) -> bool:
        """
        Sends an email alert.

        Args:
            recipient (str): Recipient email address.
            subject (str): Subject of the email.
            message (str): Message body of the email.

        Returns:
            bool: True if email is sent successfully, False otherwise.
        """
        try:
            msg = MIMEMultipart()
            msg["From"] = self.smtp_config["sender_email"]
            msg["To"] = recipient
            msg["Subject"] = subject
            msg.attach(MIMEText(message, "plain"))

            with smtplib.SMTP(self.smtp_config["smtp_server"], self.smtp_config["smtp_port"]) as server:
                server.starttls()
                server.login(self.smtp_config["sender_email"], self.smtp_config["password"])
                server.sendmail(self.smtp_config["sender_email"], recipient, msg.as_string())
            self.log_alert("email", recipient, subject, message)
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def send_sms(self, recipient: str, message: str) -> bool:
        """
        Sends an SMS alert using Twilio.

        Args:
            recipient (str): Recipient phone number.
            message (str): Message body.

        Returns:
            bool: True if SMS is sent successfully, False otherwise.
        """
        try:
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_config['account_sid']}/Messages.json"
            payload = {
                "From": self.twilio_config["from_number"],
                "To": recipient,
                "Body": message,
            }
            auth = (self.twilio_config["account_sid"], self.twilio_config["auth_token"])
            response = requests.post(url, data=payload, auth=auth)
            if response.status_code == 201:
                self.log_alert("sms", recipient, None, message)
                return True
            else:
                print(f"Twilio error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False

    def send_webhook(self, payload: Dict[str, Union[str, int, float]]) -> bool:
        """
        Sends a webhook notification.

        Args:
            payload (Dict[str, Union[str, int, float]]): Payload to send.

        Returns:
            bool: True if the webhook is sent successfully, False otherwise.
        """
        try:
            response = requests.post(self.webhook_url, json=payload)
            if response.status_code == 200:
                self.log_alert("webhook", self.webhook_url, None, json.dumps(payload))
                return True
            else:
                print(f"Webhook error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Error sending webhook: {e}")
            return False

    def log_alert(self, alert_type: str, recipient: str, subject: Optional[str], message: str):
        """
        Logs an alert for monitoring and auditing.

        Args:
            alert_type (str): Type of alert (e.g., 'email', 'sms', 'webhook').
            recipient (str): Recipient of the alert.
            subject (Optional[str]): Subject of the alert (if applicable).
            message (str): Message body of the alert.
        """
        timestamp = datetime.utcnow().isoformat()
        self.alert_log.append({
            "timestamp": timestamp,
            "type": alert_type,
            "recipient": recipient,
            "subject": subject,
            "message": message,
        })
        print(f"Logged alert: {alert_type} to {recipient} at {timestamp}")

    def schedule_alert(self, alert_type: str, recipient: str, message: str, delay_minutes: int = 0):
        """
        Schedules an alert to be sent after a specified delay.

        Args:
            alert_type (str): Type of alert (e.g., 'email', 'sms', 'webhook').
            recipient (str): Recipient of the alert.
            message (str): Message body of the alert.
            delay_minutes (int): Delay in minutes before sending the alert.
        """
        scheduled_time = datetime.utcnow() + timedelta(minutes=delay_minutes)
        print(f"Scheduled {alert_type} alert to {recipient} at {scheduled_time.isoformat()}")
        # Simulate delayed execution for demonstration (use Celery/Task Queue in production)

    def generate_alert_report(self) -> List[Dict[str, Union[str, int]]]:
        """
        Generates a report of all logged alerts.

        Returns:
            List[Dict[str, Union[str, int]]]: List of logged alerts.
        """
        return self.alert_log

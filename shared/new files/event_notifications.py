import logging
import smtplib
from email.mime.text import MIMEText
from typing import List, Dict, Any
import requests
import json
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("event_notifications.log"),
        logging.StreamHandler()
    ]
)

class EventNotifier:
    """
    Handles sending event notifications through various channels.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        logging.info("EventNotifier initialized.")

    # --- Email Notifications ---
    def send_email(self, recipients: List[str], subject: str, body: str):
        """
        Sends an email notification.
        :param recipients: List of email addresses.
        :param subject: Subject of the email.
        :param body: Body of the email.
        """
        try:
            email_settings = self.config.get("email_settings")
            if not email_settings:
                logging.warning("Email settings not configured.")
                return

            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = email_settings["sender"]
            msg["To"] = ", ".join(recipients)

            with smtplib.SMTP(email_settings["smtp_server"], email_settings["smtp_port"]) as server:
                server.starttls()
                server.login(email_settings["username"], email_settings["password"])
                server.sendmail(email_settings["sender"], recipients, msg.as_string())
            logging.info(f"Email sent to {recipients}.")
        except Exception as e:
            logging.error(f"Failed to send email: {e}")

    # --- SMS Notifications ---
    def send_sms(self, phone_numbers: List[str], message: str):
        """
        Sends an SMS notification.
        :param phone_numbers: List of phone numbers.
        :param message: SMS message content.
        """
        try:
            sms_settings = self.config.get("sms_settings")
            if not sms_settings:
                logging.warning("SMS settings not configured.")
                return

            for phone_number in phone_numbers:
                response = requests.post(
                    sms_settings["api_url"],
                    data={
                        "to": phone_number,
                        "message": message,
                        "api_key": sms_settings["api_key"]
                    }
                )
                if response.status_code == 200:
                    logging.info(f"SMS sent to {phone_number}.")
                else:
                    logging.error(f"Failed to send SMS to {phone_number}: {response.status_code} - {response.text}")
        except Exception as e:
            logging.error(f"Failed to send SMS: {e}")

    # --- Slack Notifications ---
    def send_slack_notification(self, message: str):
        """
        Sends a notification to Slack.
        :param message: Message to send to Slack.
        """
        try:
            slack_webhook_url = self.config.get("slack_webhook_url")
            if not slack_webhook_url:
                logging.warning("Slack webhook URL not configured.")
                return

            response = requests.post(
                slack_webhook_url,
                json={"text": message},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                logging.info("Slack notification sent successfully.")
            else:
                logging.error(f"Failed to send Slack notification: {response.status_code} - {response.text}")
        except Exception as e:
            logging.error(f"Error sending Slack notification: {e}")

    # --- Push Notifications ---
    def send_push_notification(self, user_ids: List[str], title: str, message: str):
        """
        Sends a push notification using Firebase.
        :param user_ids: List of user IDs to send the notification to.
        :param title: Notification title.
        :param message: Notification body.
        """
        try:
            firebase_settings = self.config.get("firebase_settings")
            if not firebase_settings:
                logging.warning("Firebase settings not configured.")
                return

            payload = {
                "registration_ids": user_ids,
                "notification": {
                    "title": title,
                    "body": message
                }
            }
            headers = {
                "Authorization": f"key={firebase_settings['server_key']}",
                "Content-Type": "application/json"
            }
            response = requests.post(firebase_settings["api_url"], data=json.dumps(payload), headers=headers)
            if response.status_code == 200:
                logging.info("Push notification sent successfully.")
            else:
                logging.error(f"Failed to send push notification: {response.status_code} - {response.text}")
        except Exception as e:
            logging.error(f"Error sending push notification: {e}")

    # --- Scheduled Notifications ---
    def schedule_notification(self, notification_type: str, time: datetime, **kwargs):
        """
        Schedules a notification for a later time.
        :param notification_type: Type of notification ('email', 'sms', 'slack', 'push').
        :param time: Time to send the notification.
        :param kwargs: Additional parameters for the notification.
        """
        try:
            if notification_type == "email":
                self.scheduler.add_job(self.send_email, 'date', run_date=time, kwargs=kwargs)
            elif notification_type == "sms":
                self.scheduler.add_job(self.send_sms, 'date', run_date=time, kwargs=kwargs)
            elif notification_type == "slack":
                self.scheduler.add_job(self.send_slack_notification, 'date', run_date=time, kwargs=kwargs)
            elif notification_type == "push":
                self.scheduler.add_job(self.send_push_notification, 'date', run_date=time, kwargs=kwargs)
            else:
                logging.warning(f"Unsupported notification type: {notification_type}")
            logging.info(f"Notification scheduled: {notification_type} at {time}.")
        except Exception as e:
            logging.error(f"Error scheduling notification: {e}")

    # --- Event Notification ---
    def notify_event(self, event_type: str, recipients: List[str], message: str, **kwargs):
        """
        Sends a notification for a specific event type.
        :param event_type: Type of event ('update', 'alert', 'promotion', 'warning').
        :param recipients: List of recipients.
        :param message: Notification message.
        :param kwargs: Additional parameters for the notification.
        """
        try:
            if event_type == "update":
                self.send_email(recipients, "System Update", message)
            elif event_type == "alert":
                self.send_slack_notification(message)
            elif event_type == "promotion":
                self.send_push_notification(recipients, "Promotion", message)
            elif event_type == "warning":
                self.send_sms(recipients, message)
            else:
                logging.warning(f"Unsupported event type: {event_type}")
            logging.info(f"Event notification sent: {event_type}.")
        except Exception as e:
            logging.error(f"Error sending event notification: {e}")


# Example Usage
if __name__ == "__main__":
    config = {
        "email_settings": {
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "username": "user@example.com",
            "password": "password",
            "sender": "noreply@example.com",
            "recipients": ["admin@example.com"]
        },
        "sms_settings": {
            "api_url": "https://sms.example.com/api",
            "api_key": "your_api_key"
        },
        "slack_webhook_url": "https://hooks.slack.com/services/...",
        "firebase_settings": {
            "api_url": "https://fcm.googleapis.com/fcm/send",
            "server_key": "your_server_key"
        }
    }

    notifier = EventNotifier(config)
    notifier.notify_event("alert", ["admin@example.com"], "Critical system alert!")

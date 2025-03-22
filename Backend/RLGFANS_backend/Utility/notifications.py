# notifications.py - Handles notification management for RLG Fans

import logging
from smtplib import SMTP, SMTPException
from twilio.rest import Client as TwilioClient
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .config import Config
from .models import Notification
from .database import db
from datetime import datetime

# Set up logging for notifications
logger = logging.getLogger("RLG_Fans.Notifications")

class NotificationManager:
    """
    Manages sending email, SMS, and in-app notifications.
    """

    def __init__(self):
        # Twilio setup for SMS notifications
        self.twilio_client = TwilioClient(
            Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN
        )

    def send_email(self, to_email, subject, body):
        """
        Sends an email notification.
        """
        try:
            logger.info(f"Attempting to send email to {to_email} with subject '{subject}'")

            # Prepare the message
            message = MIMEMultipart()
            message['From'] = Config.MAIL_DEFAULT_SENDER
            message['To'] = to_email
            message['Subject'] = subject
            message.attach(MIMEText(body, 'html'))

            # Connect to the server and send the email
            with SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
                server.starttls()
                server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
                server.sendmail(
                    Config.MAIL_DEFAULT_SENDER, to_email, message.as_string()
                )
            
            logger.info(f"Email sent successfully to {to_email}")
            self.save_notification(to_email, "email", subject, body)

        except SMTPException as e:
            logger.error(f"Failed to send email to {to_email}: {e}")

    def send_sms(self, to_number, body):
        """
        Sends an SMS notification using Twilio.
        """
        try:
            logger.info(f"Attempting to send SMS to {to_number}")

            message = self.twilio_client.messages.create(
                body=body, from_=Config.TWILIO_PHONE_NUMBER, to=to_number
            )
            logger.info(f"SMS sent successfully to {to_number}, SID: {message.sid}")
            self.save_notification(to_number, "sms", "", body)

        except Exception as e:
            logger.error(f"Failed to send SMS to {to_number}: {e}")

    def send_in_app_notification(self, user_id, title, message):
        """
        Creates an in-app notification for the user.
        """
        try:
            logger.info(f"Creating in-app notification for User ID {user_id}")

            notification = Notification(
                user_id=user_id, title=title, message=message, type="in-app"
            )
            db.session.add(notification)
            db.session.commit()
            logger.info(f"In-app notification created for User ID {user_id}")

        except Exception as e:
            logger.error(f"Failed to create in-app notification for User ID {user_id}: {e}")

    def save_notification(self, recipient, type_, subject, message):
        """
        Saves the notification to the database for tracking.
        """
        try:
            logger.debug(f"Saving {type_} notification for {recipient}")

            notification = Notification(
                recipient=recipient,
                type=type_,
                subject=subject,
                message=message,
                created_at=datetime.utcnow()
            )
            db.session.add(notification)
            db.session.commit()
            logger.info(f"Notification saved for {recipient}")

        except Exception as e:
            logger.error(f"Failed to save notification for {recipient}: {e}")

    def schedule_notification(self, recipient, type_, subject, message, send_at):
        """
        Schedules a notification to be sent at a specific time.
        """
        # Here, integrate Celery or a similar task scheduler
        logger.info(f"Scheduling {type_} notification for {recipient} at {send_at}")
        # Task scheduling code goes here


# Initialize the NotificationManager
notification_manager = NotificationManager()


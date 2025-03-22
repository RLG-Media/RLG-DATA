import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
import firebase_admin
from firebase_admin import messaging, credentials
import logging
import os
from typing import List, Dict, Optional


class NotificationSystem:
    """
    A system for sending notifications through email, SMS, and push notifications.
    """

    def __init__(self):
        """
        Initialize the NotificationSystem with required configurations.
        """
        self.email_server = os.getenv("EMAIL_SERVER", "smtp.gmail.com")
        self.email_port = int(os.getenv("EMAIL_PORT", 587))
        self.email_username = os.getenv("EMAIL_USERNAME")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.twilio_sid = os.getenv("TWILIO_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.firebase_credentials_path = os.getenv("FIREBASE_CREDENTIALS")

        # Initialize Firebase app for push notifications
        if self.firebase_credentials_path:
            cred = credentials.Certificate(self.firebase_credentials_path)
            firebase_admin.initialize_app(cred)

        # Set up logging
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

    def send_email(self, recipient: str, subject: str, body: str, html: Optional[str] = None) -> bool:
        """
        Send an email notification.

        Args:
            recipient: The recipient's email address.
            subject: The subject of the email.
            body: The plain text body of the email.
            html: Optional HTML content for the email.

        Returns:
            True if the email is sent successfully, False otherwise.
        """
        try:
            msg = MIMEMultipart()
            msg["From"] = self.email_username
            msg["To"] = recipient
            msg["Subject"] = subject

            msg.attach(MIMEText(body, "plain"))
            if html:
                msg.attach(MIMEText(html, "html"))

            with smtplib.SMTP(self.email_server, self.email_port) as server:
                server.starttls()
                server.login(self.email_username, self.email_password)
                server.send_message(msg)

            logging.info(f"Email sent to {recipient}")
            return True
        except Exception as e:
            logging.error(f"Failed to send email: {e}")
            return False

    def send_sms(self, recipient: str, message: str) -> bool:
        """
        Send an SMS notification.

        Args:
            recipient: The recipient's phone number.
            message: The message to be sent.

        Returns:
            True if the SMS is sent successfully, False otherwise.
        """
        try:
            client = Client(self.twilio_sid, self.twilio_auth_token)
            client.messages.create(
                to=recipient, from_=self.twilio_phone_number, body=message
            )
            logging.info(f"SMS sent to {recipient}")
            return True
        except Exception as e:
            logging.error(f"Failed to send SMS: {e}")
            return False

    def send_push_notification(self, device_token: str, title: str, body: str, data: Optional[Dict] = None) -> bool:
        """
        Send a push notification.

        Args:
            device_token: The recipient's device token.
            title: The title of the notification.
            body: The body of the notification.
            data: Optional additional data to include.

        Returns:
            True if the notification is sent successfully, False otherwise.
        """
        try:
            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                data=data or {},
                token=device_token,
            )
            response = messaging.send(message)
            logging.info(f"Push notification sent: {response}")
            return True
        except Exception as e:
            logging.error(f"Failed to send push notification: {e}")
            return False

    def bulk_send_email(self, recipients: List[str], subject: str, body: str, html: Optional[str] = None) -> Dict[str, bool]:
        """
        Send emails to multiple recipients.

        Args:
            recipients: List of recipient email addresses.
            subject: The subject of the email.
            body: The plain text body of the email.
            html: Optional HTML content for the email.

        Returns:
            A dictionary with recipient email addresses as keys and success status as values.
        """
        results = {}
        for recipient in recipients:
            results[recipient] = self.send_email(recipient, subject, body, html)
        return results

    def bulk_send_sms(self, recipients: List[str], message: str) -> Dict[str, bool]:
        """
        Send SMS to multiple recipients.

        Args:
            recipients: List of recipient phone numbers.
            message: The message to be sent.

        Returns:
            A dictionary with recipient phone numbers as keys and success status as values.
        """
        results = {}
        for recipient in recipients:
            results[recipient] = self.send_sms(recipient, message)
        return results

    def bulk_send_push_notifications(self, device_tokens: List[str], title: str, body: str, data: Optional[Dict] = None) -> Dict[str, bool]:
        """
        Send push notifications to multiple devices.

        Args:
            device_tokens: List of device tokens.
            title: The title of the notification.
            body: The body of the notification.
            data: Optional additional data to include.

        Returns:
            A dictionary with device tokens as keys and success status as values.
        """
        results = {}
        for token in device_tokens:
            results[token] = self.send_push_notification(token, title, body, data)
        return results


# Example Usage
if __name__ == "__main__":
    notification_system = NotificationSystem()

    # Email example
    notification_system.send_email(
        recipient="example@example.com",
        subject="Test Email",
        body="This is a test email.",
        html="<p>This is a <strong>test</strong> email.</p>"
    )

    # SMS example
    notification_system.send_sms(recipient="+1234567890", message="This is a test SMS.")

    # Push Notification example
    notification_system.send_push_notification(
        device_token="example_device_token",
        title="Test Notification",
        body="This is a test notification.",
        data={"key": "value"}
    )

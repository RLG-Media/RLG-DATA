import os
import smtplib
import logging
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import EMAIL_CONFIG
from celery import Celery
import sendgrid
from sendgrid.helpers.mail import Mail
import boto3

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Celery for async email sending
celery_app = Celery("email_tasks", broker=EMAIL_CONFIG["celery_broker"])

class EmailNotification:
    """Handles automated email notifications for RLG Data and RLG Fans."""

    def __init__(self):
        self.email_provider = EMAIL_CONFIG.get("provider", "SMTP")
        self.smtp_server = EMAIL_CONFIG.get("smtp_server", "")
        self.smtp_port = EMAIL_CONFIG.get("smtp_port", 587)
        self.smtp_username = EMAIL_CONFIG.get("smtp_username", "")
        self.smtp_password = EMAIL_CONFIG.get("smtp_password", "")
        self.sendgrid_api_key = EMAIL_CONFIG.get("sendgrid_api_key", "")
        self.ses_region = EMAIL_CONFIG.get("ses_region", "us-east-1")

    def send_email(self, to_email, subject, message, is_html=True):
        """Sends an email using the configured provider."""
        if self.email_provider == "SMTP":
            return self._send_smtp_email(to_email, subject, message, is_html)
        elif self.email_provider == "SendGrid":
            return self._send_sendgrid_email(to_email, subject, message)
        elif self.email_provider == "SES":
            return self._send_ses_email(to_email, subject, message)
        else:
            logging.error("Invalid email provider selected.")
            return False

    def _send_smtp_email(self, to_email, subject, message, is_html):
        """Sends an email using an SMTP server (e.g., Gmail, Outlook)."""
        try:
            msg = MIMEMultipart()
            msg["From"] = self.smtp_username
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(message, "html" if is_html else "plain"))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.smtp_username, to_email, msg.as_string())

            logging.info(f"Email successfully sent to {to_email} via SMTP.")
            return True
        except Exception as e:
            logging.error(f"Failed to send SMTP email: {str(e)}")
            return False

    def _send_sendgrid_email(self, to_email, subject, message):
        """Sends an email using SendGrid."""
        try:
            sg = sendgrid.SendGridAPIClient(api_key=self.sendgrid_api_key)
            mail = Mail(
                from_email=self.smtp_username,
                to_emails=to_email,
                subject=subject,
                html_content=message
            )
            response = sg.send(mail)
            if response.status_code in [200, 202]:
                logging.info(f"Email successfully sent to {to_email} via SendGrid.")
                return True
            else:
                logging.error(f"SendGrid email failed: {response.body}")
                return False
        except Exception as e:
            logging.error(f"Failed to send SendGrid email: {str(e)}")
            return False

    def _send_ses_email(self, to_email, subject, message):
        """Sends an email using Amazon SES."""
        try:
            ses_client = boto3.client("ses", region_name=self.ses_region)
            response = ses_client.send_email(
                Source=self.smtp_username,
                Destination={"ToAddresses": [to_email]},
                Message={
                    "Subject": {"Data": subject},
                    "Body": {"Html": {"Data": message}}
                }
            )
            logging.info(f"Email successfully sent to {to_email} via SES.")
            return True
        except Exception as e:
            logging.error(f"Failed to send SES email: {str(e)}")
            return False

@celery_app.task
def send_email_async(to_email, subject, message, is_html=True):
    """Asynchronous task for sending emails."""
    email_service = EmailNotification()
    return email_service.send_email(to_email, subject, message, is_html)

# Example Usage
if __name__ == "__main__":
    email_service = EmailNotification()
    email_subject = "Welcome to RLG Data & RLG Fans!"
    email_body = "<h3>Thank you for joining us!</h3><p>We're excited to have you.</p>"
    recipient_email = "user@example.com"

    # Send email synchronously
    email_service.send_email(recipient_email, email_subject, email_body)

    # Send email asynchronously using Celery
    send_email_async.delay(recipient_email, email_subject, email_body)

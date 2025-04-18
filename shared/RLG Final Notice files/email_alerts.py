"""
email_alerts.py

This module defines the EmailAlerts class to send automated email alerts for both
RLG Data and RLG Fans. It uses Python's built-in smtplib and email libraries to create
and send MIME messages. The configuration (SMTP server, port, credentials, etc.) should
be provided via environment variables or a secure configuration file in production.
"""

import os
import smtplib
import logging
from email.message import EmailMessage
from email.utils import formataddr
from typing import List, Optional

# Configure logging
logger = logging.getLogger("EmailAlerts")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

class EmailAlerts:
    def __init__(self,
                 smtp_server: Optional[str] = None,
                 smtp_port: Optional[int] = None,
                 smtp_user: Optional[str] = None,
                 smtp_password: Optional[str] = None,
                 sender_name: Optional[str] = None,
                 sender_email: Optional[str] = None,
                 use_tls: bool = True):
        """
        Initialize the EmailAlerts object with SMTP configuration.

        Parameters:
            smtp_server (str): SMTP server address. If not provided, read from env var SMTP_SERVER.
            smtp_port (int): SMTP port number. If not provided, read from env var SMTP_PORT.
            smtp_user (str): SMTP username. If not provided, read from env var SMTP_USER.
            smtp_password (str): SMTP password. If not provided, read from env var SMTP_PASSWORD.
            sender_name (str): The display name of the sender.
            sender_email (str): The email address of the sender.
            use_tls (bool): Whether to use TLS for the connection.
        """
        self.smtp_server = smtp_server or os.getenv("SMTP_SERVER", "smtp.example.com")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = smtp_user or os.getenv("SMTP_USER", "your_username")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD", "your_password")
        self.sender_name = sender_name or os.getenv("SENDER_NAME", "RLG Alerts")
        self.sender_email = sender_email or os.getenv("SENDER_EMAIL", "alerts@example.com")
        self.use_tls = use_tls

        logger.info("EmailAlerts initialized with SMTP server: %s, port: %s", self.smtp_server, self.smtp_port)

    def _create_message(self,
                        subject: str,
                        body: str,
                        to_emails: List[str],
                        html_body: Optional[str] = None) -> EmailMessage:
        """
        Creates an EmailMessage object.

        Parameters:
            subject (str): The subject of the email.
            body (str): The plain text body of the email.
            to_emails (List[str]): List of recipient email addresses.
            html_body (str, optional): HTML version of the email body.

        Returns:
            EmailMessage: The constructed email message.
        """
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = formataddr((self.sender_name, self.sender_email))
        msg["To"] = ", ".join(to_emails)

        # Set plain text content
        msg.set_content(body)

        # If HTML content is provided, add it as an alternative.
        if html_body:
            msg.add_alternative(html_body, subtype="html")
        return msg

    def send_alert(self,
                   subject: str,
                   body: str,
                   to_emails: List[str],
                   html_body: Optional[str] = None) -> bool:
        """
        Sends an email alert to the specified recipients.

        Parameters:
            subject (str): The email subject.
            body (str): The plain text email body.
            to_emails (List[str]): A list of recipient email addresses.
            html_body (str, optional): HTML formatted email body.

        Returns:
            bool: True if the email was sent successfully, False otherwise.
        """
        msg = self._create_message(subject, body, to_emails, html_body)
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.ehlo()
                if self.use_tls:
                    server.starttls()
                    server.ehlo()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
                logger.info("Email sent successfully to %s with subject '%s'.", to_emails, subject)
            return True
        except Exception as e:
            logger.error("Failed to send email to %s: %s", to_emails, e)
            return False

# -------------------------------
# Additional Recommendations:
# -------------------------------
# 1. **Secure Credentials:** Ensure that SMTP credentials and sensitive configurations are stored in environment variables
#    or a secure configuration file, and never hardcoded.
# 2. **Error Handling & Alerts:** You may wish to integrate a retry mechanism or alert a secondary channel if emails fail to send.
# 3. **Asynchronous Sending:** For high throughput, consider sending emails asynchronously using a task queue (e.g., Celery).
# 4. **HTML Templates:** For rich email content, consider using a templating engine (e.g., Jinja2) to generate HTML emails.
# 5. **Regional Customization:** If needed, extend the configuration to handle region-specific templates or recipient lists.

# -------------------------------
# Standalone Testing
# -------------------------------
if __name__ == "__main__":
    # For standalone testing, set sample environment variables or pass parameters.
    # Ensure you replace these with valid credentials and server details for testing.
    email_alerts = EmailAlerts(
        smtp_server="smtp.example.com",
        smtp_port=587,
        smtp_user="your_username",
        smtp_password="your_password",
        sender_name="RLG Alerts",
        sender_email="alerts@example.com"
    )

    # Test sending a plain text email.
    subject = "Test Alert: RLG Data Update"
    body = "This is a test alert for RLG Data. The system has completed its latest update."
    recipients = ["recipient@example.com"]

    if email_alerts.send_alert(subject, body, recipients):
        print("Test email sent successfully.")
    else:
        print("Failed to send test email.")

    # Optionally, test with HTML content.
    html_content = """
    <html>
        <body>
            <h2>Test Alert: RLG Fans Update</h2>
            <p>This is a test alert for <b>RLG Fans</b>. The system has completed its latest update.</p>
        </body>
    </html>
    """
    subject_html = "Test Alert: RLG Fans Update"
    if email_alerts.send_alert(subject_html, body, recipients, html_body=html_content):
        print("Test HTML email sent successfully.")
    else:
        print("Failed to send test HTML email.")

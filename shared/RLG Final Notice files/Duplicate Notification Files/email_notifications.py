# email_notifications.py - Email Notifications Utility for RLG Data and RLG Fans

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formataddr
from backend.error_handlers import NotificationError

# Logger configuration
logger = logging.getLogger("email_notifications")
logger.setLevel(logging.INFO)

# Email server configurations (update based on your environment)
SMTP_SERVER = "smtp.your-email-provider.com"
SMTP_PORT = 587
SMTP_USER = "your_email@example.com"
SMTP_PASSWORD = "your_password"
DEFAULT_SENDER_NAME = "RLG Notifications"
DEFAULT_SENDER_EMAIL = SMTP_USER

# Email templates folder (optional, for loading HTML templates)
TEMPLATES_FOLDER = "email_templates/"

def send_email(
    recipients,
    subject,
    body,
    sender_email=DEFAULT_SENDER_EMAIL,
    sender_name=DEFAULT_SENDER_NAME,
    is_html=False,
    attachments=None,
    cc=None,
    bcc=None,
):
    """
    Sends an email to the specified recipients.

    Args:
        recipients (list): List of recipient email addresses.
        subject (str): Subject of the email.
        body (str): Body of the email (plain text or HTML).
        sender_email (str): Sender's email address.
        sender_name (str): Sender's display name.
        is_html (bool): Whether the email body is HTML.
        attachments (list): List of file paths to attach.
        cc (list): List of CC email addresses.
        bcc (list): List of BCC email addresses.

    Raises:
        NotificationError: If email sending fails.
    """
    try:
        # Validate recipients
        if not recipients or not isinstance(recipients, list):
            raise ValueError("Invalid recipients list provided.")

        # Set up email
        msg = MIMEMultipart()
        msg["From"] = formataddr((sender_name, sender_email))
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject

        if cc:
            msg["Cc"] = ", ".join(cc)
        all_recipients = recipients + (cc or []) + (bcc or [])

        # Attach the email body
        if is_html:
            msg.attach(MIMEText(body, "html"))
        else:
            msg.attach(MIMEText(body, "plain"))

        # Attach files if provided
        if attachments:
            for file_path in attachments:
                try:
                    with open(file_path, "rb") as file:
                        part = MIMEApplication(file.read(), Name=file_path.split("/")[-1])
                        part["Content-Disposition"] = f'attachment; filename="{file_path.split("/")[-1]}"'
                        msg.attach(part)
                except Exception as e:
                    logger.warning(f"Failed to attach file {file_path}: {e}")

        # Connect to SMTP server and send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(sender_email, all_recipients, msg.as_string())

        logger.info(f"Email sent successfully to {', '.join(recipients)}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise NotificationError("An error occurred while sending the email.") from e


def load_template(template_name, placeholders=None):
    """
    Load and render an email template from the templates folder.

    Args:
        template_name (str): Name of the template file (e.g., 'welcome_email.html').
        placeholders (dict): Dictionary of placeholders to replace in the template.

    Returns:
        str: Rendered template as a string.

    Raises:
        NotificationError: If the template cannot be loaded.
    """
    try:
        template_path = f"{TEMPLATES_FOLDER}/{template_name}"
        with open(template_path, "r", encoding="utf-8") as file:
            template = file.read()

        if placeholders:
            for key, value in placeholders.items():
                template = template.replace(f"{{{{ {key} }}}}", value)

        return template
    except Exception as e:
        logger.error(f"Failed to load template {template_name}: {e}")
        raise NotificationError(f"Could not load email template: {template_name}") from e


def send_welcome_email(recipient, user_name):
    """
    Send a welcome email to a new user.

    Args:
        recipient (str): Recipient's email address.
        user_name (str): User's name for personalization.

    Raises:
        NotificationError: If email sending fails.
    """
    try:
        subject = "Welcome to RLG!"
        placeholders = {"user_name": user_name}
        body = load_template("welcome_email.html", placeholders)
        send_email(
            recipients=[recipient],
            subject=subject,
            body=body,
            is_html=True,
        )
    except Exception as e:
        logger.error(f"Failed to send welcome email to {recipient}: {e}")
        raise


def send_system_alert(subject, message):
    """
    Send a system alert to the admin email.

    Args:
        subject (str): Subject of the alert.
        message (str): Message body of the alert.

    Raises:
        NotificationError: If email sending fails.
    """
    try:
        admin_email = "admin@example.com"  # Update with actual admin email
        send_email(
            recipients=[admin_email],
            subject=f"System Alert: {subject}",
            body=message,
        )
    except Exception as e:
        logger.error(f"Failed to send system alert: {e}")
        raise


def schedule_email(recipients, subject, body, delay_seconds, is_html=False):
    """
    Schedule an email to be sent after a delay using Celery.

    Args:
        recipients (list): List of recipient email addresses.
        subject (str): Subject of the email.
        body (str): Body of the email (plain text or HTML).
        delay_seconds (int): Delay in seconds before sending the email.
        is_html (bool): Whether the email body is HTML.
    """
    from backend.celery_tasks import send_email_task  # Celery task for email sending

    try:
        send_email_task.apply_async(
            args=[recipients, subject, body, is_html], countdown=delay_seconds
        )
        logger.info(f"Email scheduled successfully to {', '.join(recipients)}")
    except Exception as e:
        logger.error(f"Failed to schedule email: {e}")
        raise NotificationError("Failed to schedule email.")


# Health Check
def check_email_service_health():
    """
    Check the health of the email service by sending a test email.

    Returns:
        bool: True if the email service is healthy, False otherwise.
    """
    try:
        send_email(
            recipients=["health_check@example.com"],
            subject="Email Service Health Check",
            body="This is a test email to verify email service functionality.",
        )
        logger.info("Email service is healthy.")
        return True
    except NotificationError:
        logger.error("Email service health check failed.")
        return False

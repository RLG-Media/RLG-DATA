# email_service.py - Shared Email Service for RLG Data and RLG Fans

import os
import logging
from smtplib import SMTPException
from flask_mail import Message, Mail
from jinja2 import Template
from shared.utils.templates import get_email_template

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask-Mail
mail = Mail()

def init_mail(app):
    """
    Initializes Flask-Mail with the given Flask app configuration.
    :param app: Flask application instance
    """
    mail.init_app(app)
    logger.info("Flask-Mail initialized successfully")

def send_email(recipient_email, subject, body, html_body=None, attachments=None):
    """
    Sends an email to the specified recipient.
    :param recipient_email: Email address of the recipient
    :param subject: Subject of the email
    :param body: Plain text body of the email
    :param html_body: (Optional) HTML content for the email
    :param attachments: (Optional) List of attachments in the format [{'filename': 'file.txt', 'data': b'content'}]
    :return: None
    """
    try:
        # Create email message
        msg = Message(
            subject=subject,
            recipients=[recipient_email],
            body=body,
            html=html_body,
            sender=os.getenv('MAIL_DEFAULT_SENDER')
        )

        # Attach files if provided
        if attachments:
            for attachment in attachments:
                msg.attach(
                    filename=attachment.get('filename'),
                    content_type=attachment.get('content_type', 'application/octet-stream'),
                    data=attachment.get('data')
                )

        # Send email
        with mail.connect() as conn:
            conn.send(msg)
            logger.info(f"Email sent successfully to {recipient_email} with subject: {subject}")
    except SMTPException as e:
        logger.error(f"SMTPException occurred: {e}")
        raise
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise

def send_template_email(recipient_email, subject, template_name, context, attachments=None):
    """
    Sends an email using a pre-defined HTML template.
    :param recipient_email: Email address of the recipient
    :param subject: Subject of the email
    :param template_name: Name of the email template
    :param context: Dictionary containing variables for template rendering
    :param attachments: (Optional) List of attachments
    :return: None
    """
    try:
        # Load and render the template
        template = get_email_template(template_name)
        html_body = Template(template).render(context)

        # Generate plain text fallback
        body = Template(template).render({**context, "strip_html": True})

        # Send the email
        send_email(recipient_email, subject, body, html_body, attachments)
        logger.info(f"Template email sent to {recipient_email} with template: {template_name}")
    except Exception as e:
        logger.error(f"Error sending template email: {e}")
        raise

def test_email(recipient_email):
    """
    Sends a test email to verify the email service configuration.
    :param recipient_email: Email address of the recipient
    :return: None
    """
    try:
        subject = "Test Email - RLG Services"
        body = "This is a test email to verify the email service configuration."
        send_email(recipient_email, subject, body)
        logger.info(f"Test email sent successfully to {recipient_email}")
    except Exception as e:
        logger.error(f"Error sending test email: {e}")
        raise

# Example of a shared email template renderer
def render_dynamic_email(template_path, context):
    """
    Renders a dynamic email template using Jinja2 and returns the content.
    :param template_path: Path to the email template
    :param context: Context variables for rendering
    :return: Rendered HTML and plain text content
    """
    try:
        with open(template_path, 'r') as template_file:
            template_content = template_file.read()

        # Render HTML and plain text content
        template = Template(template_content)
        html_body = template.render(context)
        plain_text_body = template.render({**context, "strip_html": True})

        return html_body, plain_text_body
    except Exception as e:
        logger.error(f"Error rendering email template from {template_path}: {e}")
        raise

# Utility to handle common email use cases
def notify_user_account_activity(user_email, activity_type, metadata=None):
    """
    Sends an account activity notification email to the user.
    :param user_email: User's email address
    :param activity_type: Type of activity (e.g., 'login', 'password_reset')
    :param metadata: Optional metadata about the activity
    :return: None
    """
    try:
        subject = f"Account Activity: {activity_type.capitalize()}"
        context = {"activity_type": activity_type, "metadata": metadata}
        send_template_email(user_email, subject, 'account_activity.html', context)
        logger.info(f"Account activity notification sent to {user_email} for {activity_type}")
    except Exception as e:
        logger.error(f"Error sending account activity notification: {e}")
        raise

# email_service.py - Shared Email Service for RLG Data and RLG Fans

import os
import logging
from smtplib import SMTPException
from flask_mail import Message, Mail
from jinja2 import Template
from shared.utils.templates import get_email_template

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask-Mail
mail = Mail()

def init_mail(app):
    """
    Initializes Flask-Mail with the given Flask app configuration.
    :param app: Flask application instance
    """
    mail.init_app(app)
    logger.info("Flask-Mail initialized successfully")

def send_email(recipient_email, subject, body, html_body=None, attachments=None):
    """
    Sends an email to the specified recipient.
    :param recipient_email: Email address of the recipient
    :param subject: Subject of the email
    :param body: Plain text body of the email
    :param html_body: (Optional) HTML content for the email
    :param attachments: (Optional) List of attachments in the format [{'filename': 'file.txt', 'data': b'content'}]
    :return: None
    """
    try:
        # Create email message
        msg = Message(
            subject=subject,
            recipients=[recipient_email],
            body=body,
            html=html_body,
            sender=os.getenv('MAIL_DEFAULT_SENDER')
        )

        # Attach files if provided
        if attachments:
            for attachment in attachments:
                msg.attach(
                    filename=attachment.get('filename'),
                    content_type=attachment.get('content_type', 'application/octet-stream'),
                    data=attachment.get('data')
                )

        # Send email
        with mail.connect() as conn:
            conn.send(msg)
            logger.info(f"Email sent successfully to {recipient_email} with subject: {subject}")
    except SMTPException as e:
        logger.error(f"SMTPException occurred: {e}")
        raise
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise

def send_template_email(recipient_email, subject, template_name, context, attachments=None):
    """
    Sends an email using a pre-defined HTML template.
    :param recipient_email: Email address of the recipient
    :param subject: Subject of the email
    :param template_name: Name of the email template
    :param context: Dictionary containing variables for template rendering
    :param attachments: (Optional) List of attachments
    :return: None
    """
    try:
        # Load and render the template
        template = get_email_template(template_name)
        html_body = Template(template).render(context)

        # Generate plain text fallback
        body = Template(template).render({**context, "strip_html": True})

        # Send the email
        send_email(recipient_email, subject, body, html_body, attachments)
        logger.info(f"Template email sent to {recipient_email} with template: {template_name}")
    except Exception as e:
        logger.error(f"Error sending template email: {e}")
        raise

def test_email(recipient_email):
    """
    Sends a test email to verify the email service configuration.
    :param recipient_email: Email address of the recipient
    :return: None
    """
    try:
        subject = "Test Email - RLG Services"
        body = "This is a test email to verify the email service configuration."
        send_email(recipient_email, subject, body)
        logger.info(f"Test email sent successfully to {recipient_email}")
    except Exception as e:
        logger.error(f"Error sending test email: {e}")
        raise

# Example of a shared email template renderer
def render_dynamic_email(template_path, context):
    """
    Renders a dynamic email template using Jinja2 and returns the content.
    :param template_path: Path to the email template
    :param context: Context variables for rendering
    :return: Rendered HTML and plain text content
    """
    try:
        with open(template_path, 'r') as template_file:
            template_content = template_file.read()

        # Render HTML and plain text content
        template = Template(template_content)
        html_body = template.render(context)
        plain_text_body = template.render({**context, "strip_html": True})

        return html_body, plain_text_body
    except Exception as e:
        logger.error(f"Error rendering email template from {template_path}: {e}")
        raise

# Utility to handle common email use cases
def notify_user_account_activity(user_email, activity_type, metadata=None):
    """
    Sends an account activity notification email to the user.
    :param user_email: User's email address
    :param activity_type: Type of activity (e.g., 'login', 'password_reset')
    :param metadata: Optional metadata about the activity
    :return: None
    """
    try:
        subject = f"Account Activity: {activity_type.capitalize()}"
        context = {"activity_type": activity_type, "metadata": metadata}
        send_template_email(user_email, subject, 'account_activity.html', context)
        logger.info(f"Account activity notification sent to {user_email} for {activity_type}")
    except Exception as e:
        logger.error(f"Error sending account activity notification: {e}")
        raise

send_template_email(
    recipient_email="user@example.com",
    subject="Your Weekly Performance Report",
    template_name="weekly_report.html",
    context={"username": "JohnDoe", "views": 1200, "likes": 350}
)

test_email("user@example.com")

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, jsonify, request, redirect, url_for

# Configure logging if not already configured
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("alerting_services.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AlertingService:
    """
    Service for managing alerts and notifications for RLG Data and RLG Fans.
    
    Supports sending email notifications, in-app notifications, and triggering alerts
    based on specific events. The service is designed to be robust and scalable, and it 
    can be extended with additional channels (e.g., SMS, push notifications) as needed.
    """

    def __init__(self, smtp_config: Dict[str, str], in_app_client: Optional[Any] = None) -> None:
        """
        Initialize the AlertingService.

        Args:
            smtp_config (Dict[str, str]): Dictionary containing SMTP server configurations.
                Example:
                {
                    'server': 'smtp.example.com',
                    'port': 587,
                    'username': 'alert@example.com',
                    'password': 'securepassword'
                }
            in_app_client (Optional[Any]): Optional client for in-app notifications.
        """
        self.smtp_config = smtp_config
        self.in_app_client = in_app_client
        logger.info("AlertingService initialized with SMTP configuration.")

    def send_email_alert(self, recipients: List[str], subject: str, message: str) -> Dict[str, str]:
        """
        Send email alerts to specified recipients.

        Args:
            recipients (List[str]): List of recipient email addresses.
            subject (str): Subject of the email.
            message (str): Body of the email.

        Returns:
            Dict[str, str]: A dictionary indicating the status and message of the operation.
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config['username']
            msg['To'] = ", ".join(recipients)
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))

            with smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port']) as server:
                server.starttls()
                server.login(self.smtp_config['username'], self.smtp_config['password'])
                server.sendmail(self.smtp_config['username'], recipients, msg.as_string())

            logger.info("Email alert sent to %s", recipients)
            return {"status": "success", "message": "Email alert sent successfully."}
        except Exception as e:
            logger.error("Failed to send email alert: %s", e)
            return {"status": "error", "message": "Failed to send email alert."}

    def send_in_app_notification(self, user_id: int, title: str, message: str) -> Dict[str, str]:
        """
        Send an in-app notification to a specific user.

        Args:
            user_id (int): The ID of the user to notify.
            title (str): Title of the notification.
            message (str): Body of the notification.

        Returns:
            Dict[str, str]: A dictionary indicating the status and message of the operation.
        """
        if not self.in_app_client:
            logger.error("In-app notification client is not configured.")
            return {"status": "error", "message": "In-app notification client is not configured."}

        try:
            self.in_app_client.send_notification(user_id, title, message)
            logger.info("In-app notification sent to user %d", user_id)
            return {"status": "success", "message": "In-app notification sent successfully."}
        except Exception as e:
            logger.error("Failed to send in-app notification: %s", e)
            return {"status": "error", "message": "Failed to send in-app notification."}

    def trigger_alert(self, alert_type: str, details: Dict[str, Any]) -> Dict[str, str]:
        """
        Trigger an alert based on the specified alert type and details.

        Args:
            alert_type (str): Type of alert ("email" or "in_app").
            details (Dict[str, Any]): Dictionary containing alert-specific details.

        Returns:
            Dict[str, str]: A dictionary indicating the status and message of the operation.
        """
        if alert_type == "email":
            return self.send_email_alert(
                recipients=details.get("recipients", []),
                subject=details.get("subject", "Alert"),
                message=details.get("message", "No message provided.")
            )
        elif alert_type == "in_app":
            return self.send_in_app_notification(
                user_id=details.get("user_id"),
                title=details.get("title", "Alert"),
                message=details.get("message", "No message provided.")
            )
        else:
            logger.error("Unsupported alert type: %s", alert_type)
            return {"status": "error", "message": "Unsupported alert type."}

# -------------------------------
# Example Usage (for testing purposes)
# -------------------------------
if __name__ == "__main__":
    # Example SMTP configuration; replace with actual values or load from a secure configuration.
    smtp_config = {
        'server': 'smtp.example.com',
        'port': 587,
        'username': 'alert@example.com',
        'password': 'securepassword'
    }

    # Example in-app notification client (a mock for testing purposes).
    class MockInAppClient:
        def send_notification(self, user_id, title, message):
            print(f"In-app notification sent to user {user_id}: {title} - {message}")

    alert_service = AlertingService(smtp_config, in_app_client=MockInAppClient())

    # Send email alert
    email_result = alert_service.send_email_alert(
        recipients=["user1@example.com", "user2@example.com"],
        subject="Test Alert",
        message="This is a test email alert."
    )
    print("Email Alert Result:", email_result)

    # Send in-app notification
    in_app_result = alert_service.send_in_app_notification(
        user_id=1,
        title="Test Notification",
        message="This is a test in-app notification."
    )
    print("In-App Notification Result:", in_app_result)

    # Trigger alert (email)
    trigger_result = alert_service.trigger_alert(
        alert_type="email",
        details={
            "recipients": ["user3@example.com"],
            "subject": "Triggered Alert",
            "message": "This alert was triggered automatically."
        }
    )
    print("Triggered Alert Result:", trigger_result)

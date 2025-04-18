import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
import requests
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("alerting_services.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NotificationService:
    """
    NotificationService provides a centralized system for managing notifications,
    including email, SMS, push, and in-app notifications.
    
    This service is designed for RLG Data and RLG Fans, with the flexibility to extend
    functionality for region, country, city, and town-specific notifications.
    """

    def __init__(self, email_config: Dict[str, str], sms_config: Dict[str, str], push_config: Dict[str, str]) -> None:
        """
        Initialize the NotificationService with configuration for email, SMS, and push notifications.
        
        Args:
            email_config (Dict[str, str]): SMTP configuration for email notifications.
                Example: {
                    'from_email': 'admin@example.com',
                    'smtp_server': 'smtp.gmail.com',
                    'smtp_port': 587,
                    'smtp_user': 'admin@example.com',
                    'smtp_password': 'securepassword'
                }
            sms_config (Dict[str, str]): Configuration for SMS notifications.
                Example: {
                    'api_url': 'https://api.smsprovider.com/send',
                    'api_key': 'sms-api-key'
                }
            push_config (Dict[str, str]): Configuration for push notifications.
                Example: {
                    'api_url': 'https://api.pushprovider.com/send',
                    'api_key': 'push-api-key'
                }
        """
        self.email_config = email_config
        self.sms_config = sms_config
        self.push_config = push_config
        logger.info("NotificationService initialized with provided configurations.")

    # ---------------- EMAIL NOTIFICATIONS ---------------- #
    def send_email(self, recipient: str, subject: str, body: str, is_html: bool = False) -> bool:
        """
        Send an email notification.
        
        Args:
            recipient (str): Recipient email address.
            subject (str): Subject line of the email.
            body (str): Body of the email.
            is_html (bool): Whether the email body is HTML (default: False).
        
        Returns:
            bool: True if the email was sent successfully, False otherwise.
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_email']
            msg['To'] = recipient
            msg['Subject'] = subject

            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['smtp_user'], self.email_config['smtp_password'])
                server.sendmail(self.email_config['from_email'], recipient, msg.as_string())

            logger.info("Email sent to %s", recipient)
            return True
        except Exception as e:
            logger.error("Failed to send email: %s", e)
            return False

    # ---------------- SMS NOTIFICATIONS ---------------- #
    def send_sms(self, phone_number: str, message: str) -> bool:
        """
        Send an SMS notification.
        
        Args:
            phone_number (str): Recipient's phone number.
            message (str): Message content.
        
        Returns:
            bool: True if SMS was sent successfully, False otherwise.
        """
        try:
            payload = {
                "to": phone_number,
                "message": message,
                "api_key": self.sms_config["api_key"]
            }
            response = requests.post(self.sms_config["api_url"], json=payload, timeout=10)
            response_data = response.json()

            if response.status_code == 200 and response_data.get("success"):
                logger.info("SMS sent to %s", phone_number)
                return True
            else:
                logger.error("SMS failed: %s", response_data.get("error", "Unknown error"))
                return False
        except Exception as e:
            logger.error("Failed to send SMS: %s", e)
            return False

    # ---------------- PUSH NOTIFICATIONS ---------------- #
    def send_push_notification(self, user_id: str, title: str, message: str, extra_data: Optional[Dict] = None) -> bool:
        """
        Send a push notification.
        
        Args:
            user_id (str): Identifier for the target user.
            title (str): Title of the notification.
            message (str): Message content.
            extra_data (Optional[Dict]): Additional data to send with the notification.
        
        Returns:
            bool: True if the push notification was sent successfully, False otherwise.
        """
        try:
            payload = {
                "user_id": user_id,
                "title": title,
                "message": message,
                "extra_data": extra_data or {},
                "api_key": self.push_config["api_key"]
            }
            response = requests.post(self.push_config["api_url"], json=payload, timeout=10)
            response_data = response.json()

            if response.status_code == 200 and response_data.get("success"):
                logger.info("Push notification sent to user %s", user_id)
                return True
            else:
                logger.error("Push notification failed: %s", response_data.get("error", "Unknown error"))
                return False
        except Exception as e:
            logger.error("Failed to send push notification: %s", e)
            return False

    # ---------------- IN-APP NOTIFICATIONS ---------------- #
    def create_in_app_notification(self, user_id: str, message: str, notification_type: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Create an in-app notification.
        
        Args:
            user_id (str): Identifier for the target user.
            message (str): Notification content.
            notification_type (str): Type of notification (e.g., "alert", "info").
            metadata (Optional[Dict]): Additional metadata for the notification.
        
        Returns:
            Dict[str, Any]: A dictionary representing the created notification.
        """
        notification = {
            "user_id": user_id,
            "message": message,
            "type": notification_type,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat()
        }
        logger.info("In-app notification created for user %s: %s", user_id, notification)
        return notification

    # ---------------- GENERIC ALERT TRIGGER ---------------- #
    def trigger_alert(self, alert_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Trigger an alert using a specified alert type.
        
        Args:
            alert_type (str): Type of alert ("email", "sms", "push", "in_app").
            details (Dict[str, Any]): Details needed to send the alert.
        
        Returns:
            Dict[str, Any]: A dictionary indicating success or failure of the alert operation.
        """
        if alert_type == "email":
            success = self.send_email(
                recipient=details.get("recipient"),
                subject=details.get("subject", "Alert"),
                body=details.get("message", "No message provided."),
                is_html=details.get("is_html", False)
            )
            return {"status": "success" if success else "error", "channel": "email"}
        elif alert_type == "sms":
            success = self.send_sms(
                phone_number=details.get("phone_number"),
                message=details.get("message", "No message provided.")
            )
            return {"status": "success" if success else "error", "channel": "sms"}
        elif alert_type == "push":
            success = self.send_push_notification(
                user_id=details.get("user_id"),
                title=details.get("title", "Alert"),
                message=details.get("message", "No message provided."),
                extra_data=details.get("extra_data")
            )
            return {"status": "success" if success else "error", "channel": "push"}
        elif alert_type == "in_app":
            notification = self.create_in_app_notification(
                user_id=details.get("user_id"),
                message=details.get("message", "No message provided."),
                notification_type=details.get("notification_type", "info"),
                metadata=details.get("metadata")
            )
            return {"status": "success", "channel": "in_app", "notification": notification}
        else:
            logger.error("Unsupported alert type: %s", alert_type)
            return {"status": "error", "message": "Unsupported alert type."}

# -------------------------------
# Example Usage (for testing purposes)
# -------------------------------
if __name__ == "__main__":
    # Example configuration for email, SMS, and push notifications.
    email_config = {
        "from_email": "admin@example.com",
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_user": "admin@example.com",
        "smtp_password": "securepassword"
    }
    sms_config = {
        "api_url": "https://api.smsprovider.com/send",
        "api_key": "sms-api-key"
    }
    push_config = {
        "api_url": "https://api.pushprovider.com/send",
        "api_key": "push-api-key"
    }

    notification_service = NotificationService(email_config, sms_config, push_config)

    # Send an email notification.
    email_result = notification_service.send_email(
        recipient="user@example.com",
        subject="Welcome!",
        body="Thank you for joining RLG Data and RLG Fans.",
        is_html=False
    )
    print("Email Alert Result:", email_result)

    # Send an SMS notification.
    sms_result = notification_service.send_sms(
        phone_number="+1234567890",
        message="Your OTP is 123456."
    )
    print("SMS Alert Result:", sms_result)

    # Send a push notification.
    push_result = notification_service.send_push_notification(
        user_id="user123",
        title="New Feature!",
        message="Check out the latest updates in RLG Fans.",
        extra_data={"app_version": "1.2.3"}
    )
    print("Push Notification Result:", push_result)

    # Create an in-app notification.
    in_app_notification = notification_service.create_in_app_notification(
        user_id="user123",
        message="Your profile is 90% complete.",
        notification_type="info",
        metadata={"action": "complete_profile"}
    )
    print("In-App Notification:", in_app_notification)

    # Trigger a generic alert (email).
    triggered_alert = notification_service.trigger_alert(
        alert_type="email",
        details={
            "recipient": "user3@example.com",
            "subject": "Triggered Alert",
            "message": "This alert was triggered automatically."
        }
    )
    print("Triggered Alert Result:", triggered_alert)

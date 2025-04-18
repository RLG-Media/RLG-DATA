import logging
from datetime import datetime
from models import User, NotificationLog
from utils import validate_request_data, send_email, send_sms
from mobile_push_notifications import MobilePushNotifications

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class NotificationsManager:
    """
    Centralized system to handle all types of notifications.
    Supports email, SMS, in-app, and push notifications.
    """

    @staticmethod
    def send_email_notification(user_id, subject, body):
        """
        Sends an email notification to a user.
        Args:
            user_id (int): ID of the recipient user.
            subject (str): Email subject.
            body (str): Email body content.
        Returns:
            dict: Email delivery confirmation.
        """
        user = User.query.get(user_id)
        if not user or not user.email:
            raise ValueError("User not found or email not registered.")

        # Send email
        success = send_email(to=user.email, subject=subject, body=body)
        if success:
            NotificationsManager.log_notification(user_id, "email", subject, body)
            logging.info(f"Email sent to user {user_id} at {user.email}.")
            return {"message": "Email sent successfully", "email": user.email}
        else:
            raise RuntimeError(f"Failed to send email to user {user_id}.")

    @staticmethod
    def send_sms_notification(user_id, message):
        """
        Sends an SMS notification to a user.
        Args:
            user_id (int): ID of the recipient user.
            message (str): SMS message content.
        Returns:
            dict: SMS delivery confirmation.
        """
        user = User.query.get(user_id)
        if not user or not user.phone_number:
            raise ValueError("User not found or phone number not registered.")

        # Send SMS
        success = send_sms(to=user.phone_number, message=message)
        if success:
            NotificationsManager.log_notification(user_id, "sms", None, message)
            logging.info(f"SMS sent to user {user_id} at {user.phone_number}.")
            return {"message": "SMS sent successfully", "phone_number": user.phone_number}
        else:
            raise RuntimeError(f"Failed to send SMS to user {user_id}.")

    @staticmethod
    def send_push_notification(user_id, title, body, data=None):
        """
        Sends a push notification to a user.
        Args:
            user_id (int): ID of the recipient user.
            title (str): Notification title.
            body (str): Notification body content.
            data (dict, optional): Additional data payload.
        Returns:
            dict: Push notification delivery confirmation.
        """
        return MobilePushNotifications.send_notification(user_id, title, body, data)

    @staticmethod
    def send_in_app_notification(user_id, message):
        """
        Logs an in-app notification for a user.
        Args:
            user_id (int): ID of the recipient user.
            message (str): Notification message content.
        Returns:
            dict: In-app notification confirmation.
        """
        NotificationsManager.log_notification(user_id, "in-app", None, message)
        logging.info(f"In-app notification logged for user {user_id}.")
        return {"message": "In-app notification logged successfully"}

    @staticmethod
    def send_bulk_notifications(user_ids, notification_type, content, data=None):
        """
        Sends bulk notifications of a specific type.
        Args:
            user_ids (list): List of recipient user IDs.
            notification_type (str): Type of notification ('email', 'sms', 'push', 'in-app').
            content (dict): Notification content. For emails, requires 'subject' and 'body'.
            data (dict, optional): Additional data payload for push notifications.
        Returns:
            dict: Summary of bulk notification delivery.
        """
        responses = []
        for user_id in user_ids:
            try:
                if notification_type == "email":
                    response = NotificationsManager.send_email_notification(user_id, content["subject"], content["body"])
                elif notification_type == "sms":
                    response = NotificationsManager.send_sms_notification(user_id, content["message"])
                elif notification_type == "push":
                    response = NotificationsManager.send_push_notification(user_id, content["title"], content["body"], data)
                elif notification_type == "in-app":
                    response = NotificationsManager.send_in_app_notification(user_id, content["message"])
                else:
                    raise ValueError(f"Unsupported notification type: {notification_type}")

                responses.append({"user_id": user_id, "status": "success", "response": response})
            except Exception as e:
                logging.error(f"Failed to send {notification_type} notification to user {user_id}: {e}")
                responses.append({"user_id": user_id, "status": "failed", "error": str(e)})

        return {"summary": responses}

    @staticmethod
    def schedule_notification(user_id, notification_type, content, send_at, data=None):
        """
        Schedules a notification to be sent at a future date and time.
        Args:
            user_id (int): ID of the recipient user.
            notification_type (str): Type of notification ('email', 'sms', 'push', 'in-app').
            content (dict): Notification content. For emails, requires 'subject' and 'body'.
            send_at (datetime): Scheduled date and time for the notification.
            data (dict, optional): Additional data payload for push notifications.
        """
        from celery_app import app

        @app.task
        def send_scheduled_notification():
            NotificationsManager.send_bulk_notifications([user_id], notification_type, content, data)

        delay_seconds = (send_at - datetime.utcnow()).total_seconds()
        app.send_task(send_scheduled_notification.name, countdown=delay_seconds)
        logging.info(f"Scheduled {notification_type} notification for user {user_id} at {send_at}.")
        return {"message": "Notification scheduled successfully", "send_at": send_at.isoformat()}

    @staticmethod
    def log_notification(user_id, notification_type, subject, body):
        """
        Logs a notification in the database.
        Args:
            user_id (int): ID of the recipient user.
            notification_type (str): Type of notification ('email', 'sms', 'push', 'in-app').
            subject (str, optional): Notification subject (for emails).
            body (str): Notification body content.
        """
        NotificationLog.create(
            user_id=user_id,
            notification_type=notification_type,
            subject=subject,
            body=body,
            timestamp=datetime.utcnow(),
        )

# Example Usage
if __name__ == "__main__":
    # Test email notification
    try:
        response = NotificationsManager.send_email_notification(1, "Welcome to RLG!", "Thank you for joining us.")
        print(response)
    except Exception as e:
        logging.error(f"Error sending email notification: {e}")

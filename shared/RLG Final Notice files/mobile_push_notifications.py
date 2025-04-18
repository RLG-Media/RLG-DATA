import json
import logging
from datetime import datetime
from firebase_admin import messaging, initialize_app, credentials
from models import User, NotificationLog
from utils import validate_request_data

# Initialize Firebase Admin SDK
cred = credentials.Certificate("path/to/firebase_credentials.json")
initialize_app(cred)

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class MobilePushNotifications:
    """
    Handles mobile push notification delivery and management.
    """

    @staticmethod
    def subscribe_user(user_id, device_token):
        """
        Subscribe a user to receive push notifications.
        Args:
            user_id (int): ID of the user.
            device_token (str): Device token to register for notifications.
        Returns:
            dict: Subscription confirmation.
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found.")

        if not device_token:
            raise ValueError("Device token is required.")

        user.device_token = device_token
        user.save()
        logging.info(f"User {user_id} subscribed for push notifications with token {device_token}.")
        return {"message": "Subscription successful", "user_id": user_id}

    @staticmethod
    def unsubscribe_user(user_id):
        """
        Unsubscribe a user from receiving push notifications.
        Args:
            user_id (int): ID of the user.
        Returns:
            dict: Unsubscription confirmation.
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found.")

        user.device_token = None
        user.save()
        logging.info(f"User {user_id} unsubscribed from push notifications.")
        return {"message": "Unsubscription successful", "user_id": user_id}

    @staticmethod
    def send_notification(user_id, title, body, data=None):
        """
        Sends a push notification to a specific user.
        Args:
            user_id (int): ID of the recipient user.
            title (str): Notification title.
            body (str): Notification body.
            data (dict, optional): Additional data to send with the notification.
        Returns:
            dict: Notification delivery confirmation.
        """
        user = User.query.get(user_id)
        if not user or not user.device_token:
            raise ValueError("User not found or device token not registered.")

        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            token=user.device_token,
            data=data or {},
        )

        response = messaging.send(message)
        logging.info(f"Notification sent to user {user_id}: {response}")

        # Log the notification
        NotificationLog.create(
            user_id=user_id,
            title=title,
            body=body,
            data=json.dumps(data or {}),
            timestamp=datetime.utcnow(),
        )

        return {"message": "Notification sent successfully", "response": response}

    @staticmethod
    def send_bulk_notifications(user_ids, title, body, data=None):
        """
        Sends push notifications to multiple users.
        Args:
            user_ids (list): List of recipient user IDs.
            title (str): Notification title.
            body (str): Notification body.
            data (dict, optional): Additional data to send with the notifications.
        Returns:
            dict: Bulk notification delivery summary.
        """
        responses = []
        for user_id in user_ids:
            try:
                response = MobilePushNotifications.send_notification(user_id, title, body, data)
                responses.append({"user_id": user_id, "status": "success", "response": response})
            except Exception as e:
                logging.error(f"Failed to send notification to user {user_id}: {e}")
                responses.append({"user_id": user_id, "status": "failed", "error": str(e)})

        return {"summary": responses}

    @staticmethod
    def test_notification(device_token, title, body, data=None):
        """
        Sends a test push notification to a specific device token.
        Args:
            device_token (str): Target device token.
            title (str): Notification title.
            body (str): Notification body.
            data (dict, optional): Additional data to send with the notification.
        Returns:
            dict: Test notification delivery confirmation.
        """
        if not device_token:
            raise ValueError("Device token is required.")

        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            token=device_token,
            data=data or {},
        )

        response = messaging.send(message)
        logging.info(f"Test notification sent to token {device_token}: {response}")
        return {"message": "Test notification sent successfully", "response": response}

    @staticmethod
    def fetch_notification_logs(user_id, limit=50):
        """
        Fetches the notification logs for a specific user.
        Args:
            user_id (int): ID of the user.
            limit (int, optional): Number of logs to fetch. Defaults to 50.
        Returns:
            list: Notification logs.
        """
        logs = NotificationLog.query.filter_by(user_id=user_id).order_by(NotificationLog.timestamp.desc()).limit(limit)
        return [log.to_dict() for log in logs]


# Example Usage
if __name__ == "__main__":
    # Example test notification
    device_token = "sample_device_token_here"
    try:
        response = MobilePushNotifications.test_notification(
            device_token,
            title="Test Notification",
            body="This is a test notification from RLG.",
            data={"key": "value"},
        )
        print(response)
    except Exception as e:
        logging.error(f"Error sending test notification: {e}")

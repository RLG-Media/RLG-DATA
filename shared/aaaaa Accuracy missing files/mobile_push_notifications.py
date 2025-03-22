import logging
from typing import List, Dict, Optional
from firebase_admin import messaging, credentials, initialize_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("mobile_push_notifications.log"),
        logging.StreamHandler()
    ]
)

class MobilePushNotificationService:
    """
    Service class for managing mobile push notifications for RLG Data and RLG Fans.
    Includes single, bulk, and topic-based notifications.
    """

    def __init__(self, firebase_credentials_path: str):
        """
        Initialize the MobilePushNotificationService.

        Args:
            firebase_credentials_path (str): Path to the Firebase Admin SDK JSON credentials file.
        """
        try:
            cred = credentials.Certificate(firebase_credentials_path)
            initialize_app(cred)
            logging.info("Firebase Admin SDK initialized.")
        except Exception as e:
            logging.error("Failed to initialize Firebase Admin SDK: %s", e)
            raise

    def send_single_notification(self, token: str, title: str, body: str, data: Optional[Dict[str, str]] = None) -> str:
        """
        Send a push notification to a single device.

        Args:
            token (str): The device registration token.
            title (str): The title of the notification.
            body (str): The body of the notification.
            data (Optional[Dict[str, str]]): Additional data payload (optional).

        Returns:
            str: Message ID of the sent notification.
        """
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data=data,
            token=token
        )
        try:
            response = messaging.send(message)
            logging.info("Notification sent to token %s: %s", token, response)
            return response
        except Exception as e:
            logging.error("Failed to send notification to token %s: %s", token, e)
            raise

    def send_bulk_notifications(self, tokens: List[str], title: str, body: str, data: Optional[Dict[str, str]] = None) -> List[str]:
        """
        Send push notifications to multiple devices.

        Args:
            tokens (List[str]): List of device registration tokens.
            title (str): The title of the notification.
            body (str): The body of the notification.
            data (Optional[Dict[str, str]]): Additional data payload (optional).

        Returns:
            List[str]: List of message IDs of the sent notifications.
        """
        messages = [
            messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data,
                token=token
            ) for token in tokens
        ]

        try:
            response = messaging.send_all(messages)
            message_ids = [resp.message_id for resp in response.responses if resp.success]
            logging.info("Bulk notifications sent: %d/%d successful", len(message_ids), len(tokens))
            return message_ids
        except Exception as e:
            logging.error("Failed to send bulk notifications: %s", e)
            raise

    def send_topic_notification(self, topic: str, title: str, body: str, data: Optional[Dict[str, str]] = None) -> str:
        """
        Send a push notification to all devices subscribed to a topic.

        Args:
            topic (str): The topic to send the notification to.
            title (str): The title of the notification.
            body (str): The body of the notification.
            data (Optional[Dict[str, str]]): Additional data payload (optional).

        Returns:
            str: Message ID of the sent notification.
        """
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data=data,
            topic=topic
        )
        try:
            response = messaging.send(message)
            logging.info("Notification sent to topic '%s': %s", topic, response)
            return response
        except Exception as e:
            logging.error("Failed to send notification to topic '%s': %s", topic, e)
            raise

    def subscribe_to_topic(self, tokens: List[str], topic: str) -> Dict[str, int]:
        """
        Subscribe devices to a topic.

        Args:
            tokens (List[str]): List of device registration tokens.
            topic (str): The topic to subscribe to.

        Returns:
            Dict[str, int]: Subscription success and failure counts.
        """
        try:
            response = messaging.subscribe_to_topic(tokens, topic)
            logging.info("Subscribed %d devices to topic '%s'.", response.success_count, topic)
            return {"success": response.success_count, "failure": response.failure_count}
        except Exception as e:
            logging.error("Failed to subscribe devices to topic '%s': %s", topic, e)
            raise

    def unsubscribe_from_topic(self, tokens: List[str], topic: str) -> Dict[str, int]:
        """
        Unsubscribe devices from a topic.

        Args:
            tokens (List[str]): List of device registration tokens.
            topic (str): The topic to unsubscribe from.

        Returns:
            Dict[str, int]: Unsubscription success and failure counts.
        """
        try:
            response = messaging.unsubscribe_from_topic(tokens, topic)
            logging.info("Unsubscribed %d devices from topic '%s'.", response.success_count, topic)
            return {"success": response.success_count, "failure": response.failure_count}
        except Exception as e:
            logging.error("Failed to unsubscribe devices from topic '%s': %s", topic, e)
            raise

# Example usage
if __name__ == "__main__":
    firebase_credentials_path = "path/to/your/firebase_credentials.json"
    notification_service = MobilePushNotificationService(firebase_credentials_path)

    # Send a single notification
    token = "example_device_token"
    notification_service.send_single_notification(
        token,
        title="Test Notification",
        body="This is a test notification."
    )

    # Send bulk notifications
    tokens = ["device_token_1", "device_token_2"]
    notification_service.send_bulk_notifications(
        tokens,
        title="Bulk Notification",
        body="This is a bulk notification."
    )

    # Send topic notification
    topic = "news_updates"
    notification_service.send_topic_notification(
        topic,
        title="Topic Notification",
        body="This is a topic notification."
    )

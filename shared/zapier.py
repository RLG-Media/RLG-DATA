# zapier.py

import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ZapierService:
    """
    A service class for managing Zapier integrations.
    This handles the creation, management, and deletion of Zapier webhooks for automation.
    """

    def __init__(self, zapier_webhook_url):
        """
        Initialize the ZapierService with the provided webhook URL.
        :param zapier_webhook_url: URL of the Zapier webhook.
        """
        self.webhook_url = zapier_webhook_url
        logger.info("ZapierService initialized.")

    def trigger_event(self, event_name, payload):
        """
        Trigger an event in Zapier with a specified payload.
        :param event_name: Name of the event being triggered.
        :param payload: Data payload to send to Zapier.
        :return: Response from Zapier.
        """
        try:
            logger.info(f"Triggering event '{event_name}' in Zapier.")
            response = requests.post(
                self.webhook_url,
                json={
                    "event_name": event_name,
                    "payload": payload,
                },
                timeout=10,
            )
            response.raise_for_status()
            logger.info(f"Event '{event_name}' triggered successfully. Response: {response.status_code}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error triggering event '{event_name}': {str(e)}")
            raise

    def create_webhook(self, webhook_url, trigger_type):
        """
        Register a new webhook in Zapier.
        :param webhook_url: The URL to be called when the trigger occurs.
        :param trigger_type: The type of event to trigger the webhook (e.g., 'new_lead', 'data_update').
        :return: Success message or response details.
        """
        try:
            logger.info(f"Creating webhook with trigger type '{trigger_type}'.")
            response = requests.post(
                self.webhook_url,
                json={
                    "action": "create_webhook",
                    "webhook_url": webhook_url,
                    "trigger_type": trigger_type,
                },
                timeout=10,
            )
            response.raise_for_status()
            logger.info(f"Webhook created successfully: {response.json()}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating webhook: {str(e)}")
            raise

    def delete_webhook(self, webhook_id):
        """
        Delete an existing webhook in Zapier.
        :param webhook_id: The ID of the webhook to delete.
        :return: Success message or response details.
        """
        try:
            logger.info(f"Deleting webhook with ID '{webhook_id}'.")
            response = requests.post(
                self.webhook_url,
                json={
                    "action": "delete_webhook",
                    "webhook_id": webhook_id,
                },
                timeout=10,
            )
            response.raise_for_status()
            logger.info(f"Webhook deleted successfully: {response.json()}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error deleting webhook: {str(e)}")
            raise

    def test_connection(self):
        """
        Test the connection to the Zapier webhook.
        :return: Success or error message.
        """
        try:
            logger.info("Testing connection to Zapier webhook.")
            response = requests.get(self.webhook_url, timeout=10)
            response.raise_for_status()
            logger.info("Zapier webhook connection test successful.")
            return {"status": "success", "message": "Connection to Zapier successful"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Error testing Zapier webhook connection: {str(e)}")
            return {"status": "error", "message": str(e)}


# Example Usage
if __name__ == "__main__":
    zapier_service = ZapierService(zapier_webhook_url="https://hooks.zapier.com/hooks/catch/123456/abcdef/")

    # Test connection
    try:
        test_result = zapier_service.test_connection()
        print(test_result)
    except Exception as e:
        print(f"Error: {str(e)}")

    # Trigger an event
    try:
        result = zapier_service.trigger_event(
            event_name="new_data_uploaded",
            payload={"user_id": 123, "platform": "OnlyFans", "data": {"views": 150, "likes": 20}},
        )
        print(result)
    except Exception as e:
        print(f"Error: {str(e)}")

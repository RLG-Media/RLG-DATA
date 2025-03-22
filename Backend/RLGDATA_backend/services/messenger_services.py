import requests
from flask import current_app

class MessengerService:
    """
    Service class for interacting with the Facebook Messenger API.
    """
    BASE_URL = 'https://graph.facebook.com/v12.0/me/messages'

    def __init__(self, page_access_token):
        """
        Initialize the MessengerService with a page access token.

        :param page_access_token: The access token for the Facebook page.
        """
        self.page_access_token = page_access_token

    def send_message(self, recipient_id, message_text, quick_replies=None, attachment=None):
        """
        Send a message to a user on Messenger.
        
        :param recipient_id: The ID of the recipient.
        :param message_text: The text of the message to send.
        :param quick_replies: Optional quick reply buttons for the message.
        :param attachment: Optional attachment (e.g., image, video, file).
        :return: Response JSON or None in case of failure.
        """
        url = f"{self.BASE_URL}"
        headers = {
            'Authorization': f'Bearer {self.page_access_token}',
            'Content-Type': 'application/json'
        }
        message_data = {
            'recipient': {'id': recipient_id},
            'message': {}
        }

        if message_text:
            message_data['message']['text'] = message_text
        
        if quick_replies:
            message_data['message']['quick_replies'] = quick_replies
        
        if attachment:
            message_data['message']['attachment'] = attachment

        try:
            response = requests.post(url, headers=headers, json=message_data)
            response.raise_for_status()  # Raise exception for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Failed to send message via Messenger: {e}")
            return None

    def handle_webhook_event(self, webhook_event):
        """
        Handle incoming messages and events via webhook.
        
        :param webhook_event: The webhook event data from Messenger.
        :return: Parsed event response or None.
        """
        try:
            current_app.logger.info(f"Processing Messenger webhook event: {webhook_event}")

            # Example: Extract sender and message text from the event
            for entry in webhook_event.get('entry', []):
                for message_event in entry.get('messaging', []):
                    sender_id = message_event.get('sender', {}).get('id')
                    message_text = message_event.get('message', {}).get('text')

                    # Log the extracted data
                    current_app.logger.info(f"Message received from {sender_id}: {message_text}")

                    # Custom logic for processing the message can be added here
                    return {
                        'sender_id': sender_id,
                        'message_text': message_text
                    }
        except Exception as e:
            current_app.logger.error(f"Error processing Messenger webhook event: {e}")
            return None

    def set_webhook(self, callback_url, verify_token):
        """
        Set up a webhook for Messenger.
        
        :param callback_url: The URL to be called when events occur.
        :param verify_token: Token to verify webhook.
        :return: Response JSON or None in case of failure.
        """
        url = f"https://graph.facebook.com/v12.0/me/subscribed_apps"
        headers = {
            'Authorization': f'Bearer {self.page_access_token}',
            'Content-Type': 'application/json'
        }
        data = {
            'callback_url': callback_url,
            'verify_token': verify_token,
            'fields': 'messages'
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Failed to set Messenger webhook: {e}")
            return None

messenger_service = MessengerService(page_access_token='your_page_access_token')

response = messenger_service.send_message(
    recipient_id='123456789',
    message_text='Hello from RLG!',
    quick_replies=[
        {"content_type": "text", "title": "Option 1", "payload": "OPTION_1"},
        {"content_type": "text", "title": "Option 2", "payload": "OPTION_2"}
    ]
)

if response:
    print("Message sent successfully:", response)
else:
    print("Failed to send message.")
webhook_event = {
    "object": "page",
    "entry": [
        {
            "messaging": [
                {
                    "sender": {"id": "123456789"},
                    "message": {"text": "Hello, RLG!"}
                }
            ]
        }
    ]
}

response = messenger_service.handle_webhook_event(webhook_event)
if response:
    print("Processed webhook event:", response)

response = messenger_service.set_webhook(
    callback_url='https://yourdomain.com/messenger/webhook',
    verify_token='your_verify_token'
)

if response:
    print("Webhook setup successful:", response)
else:
    print("Failed to set webhook.")

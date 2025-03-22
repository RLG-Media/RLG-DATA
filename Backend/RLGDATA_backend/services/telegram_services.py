import requests
import logging


class TelegramService:
    """
    Service class for interacting with the Telegram Bot API.
    """
    BASE_URL = 'https://api.telegram.org/bot'  # Base URL for Telegram Bot API

    def __init__(self, bot_token):
        """
        Initialize the TelegramService with the provided bot token.
        
        :param bot_token: Telegram bot token for API authentication.
        """
        self.bot_token = bot_token
        self.base_url = f"{self.BASE_URL}{self.bot_token}/"
        self.session = requests.Session()

    def send_message(self, chat_id, text, parse_mode="Markdown", disable_notification=False):
        """
        Send a message to a Telegram chat.

        :param chat_id: The ID of the chat to send the message to.
        :param text: The message content.
        :param parse_mode: Formatting mode for the message (e.g., "Markdown", "HTML").
        :param disable_notification: Whether to send the message silently (default: False).
        :return: JSON response from the API or None if an error occurs.
        """
        try:
            url = f"{self.base_url}sendMessage"
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': parse_mode,
                'disable_notification': disable_notification
            }

            response = self.session.post(url, json=data)
            response.raise_for_status()
            
            logging.info(f"Message sent to chat ID {chat_id}: {text}")
            return response.json()

        except requests.RequestException as e:
            logging.error(f"Failed to send message to Telegram chat ID {chat_id}: {e}")
            return None

    def get_updates(self, offset=None, limit=100, timeout=0):
        """
        Get updates for the bot, such as messages received.

        :param offset: Identifier of the first update to be returned.
        :param limit: Limits the number of updates to be retrieved (default: 100).
        :param timeout: Timeout in seconds for long polling (default: 0).
        :return: JSON response containing updates or None if an error occurs.
        """
        try:
            url = f"{self.base_url}getUpdates"
            params = {
                'offset': offset,
                'limit': limit,
                'timeout': timeout
            }

            response = self.session.get(url, params=params)
            response.raise_for_status()

            logging.info("Successfully fetched updates from Telegram.")
            return response.json()

        except requests.RequestException as e:
            logging.error(f"Failed to fetch updates from Telegram: {e}")
            return None

    def set_webhook(self, webhook_url):
        """
        Set a webhook URL for the Telegram bot.

        :param webhook_url: The URL to set as the webhook for the bot.
        :return: JSON response from the API or None if an error occurs.
        """
        try:
            url = f"{self.base_url}setWebhook"
            data = {
                'url': webhook_url
            }

            response = self.session.post(url, json=data)
            response.raise_for_status()

            logging.info(f"Webhook set successfully: {webhook_url}")
            return response.json()

        except requests.RequestException as e:
            logging.error(f"Failed to set webhook: {e}")
            return None

    def delete_webhook(self):
        """
        Remove the webhook integration for the bot.

        :return: JSON response from the API or None if an error occurs.
        """
        try:
            url = f"{self.base_url}deleteWebhook"
            response = self.session.post(url)
            response.raise_for_status()

            logging.info("Webhook deleted successfully.")
            return response.json()

        except requests.RequestException as e:
            logging.error(f"Failed to delete webhook: {e}")
            return None

    def send_photo(self, chat_id, photo_url, caption=None, parse_mode="Markdown"):
        """
        Send a photo to a Telegram chat.

        :param chat_id: The ID of the chat to send the photo to.
        :param photo_url: The URL or file ID of the photo to send.
        :param caption: Optional caption for the photo.
        :param parse_mode: Formatting mode for the caption (e.g., "Markdown", "HTML").
        :return: JSON response from the API or None if an error occurs.
        """
        try:
            url = f"{self.base_url}sendPhoto"
            data = {
                'chat_id': chat_id,
                'photo': photo_url,
                'caption': caption,
                'parse_mode': parse_mode
            }

            response = self.session.post(url, json=data)
            response.raise_for_status()

            logging.info(f"Photo sent to chat ID {chat_id} with caption: {caption}")
            return response.json()

        except requests.RequestException as e:
            logging.error(f"Failed to send photo to Telegram chat ID {chat_id}: {e}")
            return None

telegram_service = TelegramService(bot_token="your-bot-token")

telegram_service.send_message(chat_id=123456789, text="Hello, Telegram!")

updates = telegram_service.get_updates(offset=0, limit=10, timeout=10)
print(updates)

telegram_service.set_webhook(webhook_url="https://your-webhook-url.com")

telegram_service.send_photo(chat_id=123456789, photo_url="https://example.com/photo.jpg", caption="Check this out!")

telegram_service.delete_webhook()

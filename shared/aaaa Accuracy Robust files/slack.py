import logging
import os
import requests
from typing import Dict, Optional, Union, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("slack_integration.log")],
)

class SlackClient:
    """
    A class for interacting with Slack's API.
    """

    def __init__(self, token: Optional[str] = None):
        """
        Initialize the SlackClient.

        Args:
            token: Slack Bot Token. If not provided, fetched from environment variables.
        """
        self.token = token or os.getenv("SLACK_BOT_TOKEN")
        if not self.token:
            raise ValueError("Slack Bot Token is required.")
        self.base_url = "https://slack.com/api"
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def send_message(self, channel: str, text: str, blocks: Optional[List[Dict]] = None) -> Dict:
        """
        Send a message to a Slack channel.

        Args:
            channel: Slack channel ID or name.
            text: Fallback text for the message.
            blocks: A list of blocks for rich formatting.

        Returns:
            Response from Slack API.
        """
        url = f"{self.base_url}/chat.postMessage"
        payload = {"channel": channel, "text": text}
        if blocks:
            payload["blocks"] = blocks
        response = self._post(url, payload)
        return response

    def upload_file(self, channels: Union[str, List[str]], file_path: str, title: Optional[str] = None) -> Dict:
        """
        Upload a file to Slack.

        Args:
            channels: Slack channel(s) to send the file to.
            file_path: Path to the file to be uploaded.
            title: Title for the uploaded file.

        Returns:
            Response from Slack API.
        """
        url = f"{self.base_url}/files.upload"
        channels = ",".join(channels) if isinstance(channels, list) else channels
        with open(file_path, "rb") as file:
            files = {"file": file}
            data = {"channels": channels, "title": title}
            response = requests.post(url, headers=self.headers, data=data, files=files)
        return self._handle_response(response)

    def get_channel_list(self) -> Dict:
        """
        Retrieve a list of channels in the Slack workspace.

        Returns:
            Response from Slack API.
        """
        url = f"{self.base_url}/conversations.list"
        response = self._get(url)
        return response

    def invite_user_to_channel(self, channel: str, user: str) -> Dict:
        """
        Invite a user to a Slack channel.

        Args:
            channel: Channel ID to invite the user to.
            user: User ID to be invited.

        Returns:
            Response from Slack API.
        """
        url = f"{self.base_url}/conversations.invite"
        payload = {"channel": channel, "users": user}
        response = self._post(url, payload)
        return response

    def _get(self, url: str, params: Optional[Dict] = None) -> Dict:
        """
        Internal helper for making GET requests.

        Args:
            url: URL to make the GET request to.
            params: Query parameters.

        Returns:
            Parsed JSON response.
        """
        response = requests.get(url, headers=self.headers, params=params)
        return self._handle_response(response)

    def _post(self, url: str, data: Dict) -> Dict:
        """
        Internal helper for making POST requests.

        Args:
            url: URL to make the POST request to.
            data: Payload for the POST request.

        Returns:
            Parsed JSON response.
        """
        response = requests.post(url, headers=self.headers, json=data)
        return self._handle_response(response)

    def _handle_response(self, response: requests.Response) -> Dict:
        """
        Internal helper to handle API responses.

        Args:
            response: The HTTP response object.

        Returns:
            Parsed JSON response.

        Raises:
            ValueError: If the API response indicates an error.
        """
        if not response.ok:
            logging.error(f"Slack API error: {response.status_code} - {response.text}")
            response.raise_for_status()
        result = response.json()
        if not result.get("ok", False):
            error_message = result.get("error", "Unknown error")
            logging.error(f"Slack API returned an error: {error_message}")
            raise ValueError(error_message)
        return result


# Example usage
if __name__ == "__main__":
    try:
        slack_client = SlackClient()
        
        # Send a simple message
        slack_client.send_message(channel="#general", text="Hello from SlackClient!")

        # Upload a file
        slack_client.upload_file(channels="#general", file_path="example.txt", title="Example File")

        # Retrieve and log channel list
        channels = slack_client.get_channel_list()
        logging.info(f"Channel List: {channels}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")

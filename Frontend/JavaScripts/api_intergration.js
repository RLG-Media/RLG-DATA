import requests
from requests.exceptions import RequestException, Timeout
import logging
from typing import Any, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("api_integration.log"),
        logging.StreamHandler()
    ]
)

class APIClient:
    """
    A reusable API client for interacting with external services.
    """

    def __init__(self, base_url: str, timeout: int = 10):
        """
        Initialize the API client.
        :param base_url: Base URL of the external API.
        :param timeout: Request timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers = {"Content-Type": "application/json"}

    def set_headers(self, custom_headers: Dict[str, str]) -> None:
        """
        Update default headers with custom headers.
        :param custom_headers: Dictionary of custom headers.
        """
        self.headers.update(custom_headers)

    def send_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Send an HTTP request to the external API.
        :param method: HTTP method ('GET', 'POST', etc.).
        :param endpoint: API endpoint (relative to the base URL).
        :param params: Query parameters for the request.
        :param data: Payload for POST/PUT requests.
        :return: Parsed JSON response or None if the request fails.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        logging.info(f"Sending {method} request to {url} with params={params} and data={data}")

        try:
            response = requests.request(
                method,
                url,
                headers=self.headers,
                params=params,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            logging.info(f"Response received: {response.status_code}")
            return response.json()
        except Timeout:
            logging.error(f"Request to {url} timed out.")
        except RequestException as e:
            logging.error(f"Request to {url} failed: {e}")
        return None

# Example Integration Functions

def fetch_social_media_data(api_client: APIClient, platform: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Fetch data from a social media API.
    :param api_client: Instance of APIClient.
    :param platform: Name of the platform (e.g., 'facebook', 'twitter').
    :param params: Query parameters for the API request.
    :return: Parsed JSON response or None if the request fails.
    """
    endpoint_map = {
        "facebook": "/facebook/data",
        "twitter": "/twitter/data",
        "instagram": "/instagram/data"
    }

    endpoint = endpoint_map.get(platform)
    if not endpoint:
        logging.error(f"Platform {platform} is not supported.")
        return None

    return api_client.send_request("GET", endpoint, params=params)

def post_user_activity(api_client: APIClient, activity_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Send user activity data to an analytics API.
    :param api_client: Instance of APIClient.
    :param activity_data: Activity data to be posted.
    :return: Parsed JSON response or None if the request fails.
    """
    endpoint = "/analytics/activity"
    return api_client.send_request("POST", endpoint, data=activity_data)

# Example Usage
if __name__ == "__main__":
    base_url = "https://api.example.com"
    api_client = APIClient(base_url)

    # Fetch data from Facebook
    facebook_params = {"user_id": "12345", "fields": "name,posts"}
    facebook_data = fetch_social_media_data(api_client, "facebook", facebook_params)
    if facebook_data:
        logging.info(f"Facebook data: {facebook_data}")

    # Post user activity
    activity_data = {"user_id": "12345", "action": "login", "timestamp": "2024-11-27T12:00:00Z"}
    activity_response = post_user_activity(api_client, activity_data)
    if activity_response:
        logging.info(f"Activity post response: {activity_response}")

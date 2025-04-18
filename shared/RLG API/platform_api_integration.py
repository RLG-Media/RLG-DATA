import logging
import requests
from requests.exceptions import HTTPError, Timeout
from utils import validate_request_data, retry_on_failure
from exceptions import IntegrationError, PlatformAuthenticationError

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class PlatformAPIIntegration:
    """
    A central manager for integrating with external platform APIs.
    Handles authentication, API requests, and response processing for multiple platforms.
    """

    def __init__(self, platform_name, base_url, api_key=None, client_id=None, client_secret=None, auth_token=None):
        self.platform_name = platform_name
        self.base_url = base_url
        self.api_key = api_key
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_token = auth_token
        self.session = requests.Session()
        self.session.headers.update(self._generate_headers())

    def _generate_headers(self):
        """
        Generates headers required for API requests.
        Returns:
            dict: A dictionary of headers.
        """
        headers = {
            "User-Agent": "RLGData/1.0",
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers

    def authenticate(self, auth_endpoint, auth_payload):
        """
        Authenticates with the platform's API and stores the authentication token.
        Args:
            auth_endpoint (str): The API endpoint for authentication.
            auth_payload (dict): The payload for the authentication request.
        """
        try:
            logging.info(f"Authenticating with {self.platform_name}...")
            response = self.session.post(f"{self.base_url}/{auth_endpoint}", json=auth_payload)
            response.raise_for_status()
            self.auth_token = response.json().get("access_token")
            if not self.auth_token:
                raise PlatformAuthenticationError(f"Failed to authenticate with {self.platform_name}. No token received.")
            self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
            logging.info(f"Successfully authenticated with {self.platform_name}.")
        except HTTPError as e:
            raise PlatformAuthenticationError(f"HTTP error during authentication: {e}")
        except Exception as e:
            raise IntegrationError(f"Unexpected error during authentication: {e}")

    @retry_on_failure(max_retries=3, delay=2)
    def make_request(self, endpoint, method="GET", params=None, payload=None):
        """
        Makes a request to the platform API.
        Args:
            endpoint (str): The API endpoint.
            method (str): HTTP method ('GET', 'POST', 'PUT', 'DELETE').
            params (dict, optional): Query parameters.
            payload (dict, optional): Request body for POST/PUT requests.
        Returns:
            dict: The parsed JSON response.
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            logging.info(f"Making {method} request to {self.platform_name}: {url}")
            response = self.session.request(method, url, params=params, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except Timeout:
            raise IntegrationError(f"Request to {self.platform_name} timed out.")
        except HTTPError as e:
            raise IntegrationError(f"HTTP error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise IntegrationError(f"Unexpected error: {e}")

    def fetch_data(self, endpoint, params=None):
        """
        Fetches data from the platform API.
        Args:
            endpoint (str): The API endpoint.
            params (dict, optional): Query parameters.
        Returns:
            dict: The fetched data.
        """
        try:
            logging.info(f"Fetching data from {self.platform_name}...")
            data = self.make_request(endpoint, "GET", params)
            logging.info(f"Data fetched successfully from {self.platform_name}.")
            return data
        except Exception as e:
            logging.error(f"Failed to fetch data from {self.platform_name}: {e}")
            raise

    def post_data(self, endpoint, payload):
        """
        Sends data to the platform API.
        Args:
            endpoint (str): The API endpoint.
            payload (dict): Data to send.
        Returns:
            dict: The API response.
        """
        try:
            logging.info(f"Posting data to {self.platform_name}...")
            response = self.make_request(endpoint, "POST", payload=payload)
            logging.info(f"Data posted successfully to {self.platform_name}.")
            return response
        except Exception as e:
            logging.error(f"Failed to post data to {self.platform_name}: {e}")
            raise

    def update_data(self, endpoint, payload):
        """
        Updates data on the platform API.
        Args:
            endpoint (str): The API endpoint.
            payload (dict): Data to update.
        Returns:
            dict: The API response.
        """
        try:
            logging.info(f"Updating data on {self.platform_name}...")
            response = self.make_request(endpoint, "PUT", payload=payload)
            logging.info(f"Data updated successfully on {self.platform_name}.")
            return response
        except Exception as e:
            logging.error(f"Failed to update data on {self.platform_name}: {e}")
            raise

    def delete_data(self, endpoint):
        """
        Deletes data from the platform API.
        Args:
            endpoint (str): The API endpoint.
        Returns:
            dict: The API response.
        """
        try:
            logging.info(f"Deleting data on {self.platform_name}...")
            response = self.make_request(endpoint, "DELETE")
            logging.info(f"Data deleted successfully on {self.platform_name}.")
            return response
        except Exception as e:
            logging.error(f"Failed to delete data on {self.platform_name}: {e}")
            raise

# Example usage for different platforms
if __name__ == "__main__":
    # Example: Integration with a social media platform
    try:
        facebook_integration = PlatformAPIIntegration(
            platform_name="Facebook",
            base_url="https://graph.facebook.com",
            api_key="YOUR_FACEBOOK_API_KEY"
        )
        user_profile = facebook_integration.fetch_data("me", params={"fields": "id,name,email"})
        print("User Profile:", user_profile)
    except Exception as e:
        logging.error(f"Error integrating with Facebook: {e}")

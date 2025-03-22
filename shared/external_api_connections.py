import requests
from requests.exceptions import RequestException, HTTPError, Timeout
import logging

logger = logging.getLogger(__name__)

class ExternalAPIConnector:
    """
    Utility class to handle external API connections and requests for both RLG Data and RLG Fans.
    Provides a unified interface for making API calls, handling errors, and managing responses.
    """

    def __init__(self, base_url, headers=None, timeout=10):
        """
        Initializes the ExternalAPIConnector.

        :param base_url: Base URL of the external API.
        :param headers: Default headers to include in requests.
        :param timeout: Request timeout in seconds (default is 10).
        """
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}
        self.timeout = timeout

    def _handle_response(self, response):
        """
        Handles the HTTP response from an API call.

        :param response: The HTTP response object.
        :return: Parsed JSON data if available, or raw text response.
        :raises HTTPError: If the HTTP response code indicates an error.
        """
        try:
            response.raise_for_status()
            content_type = response.headers.get('Content-Type', '')
            if content_type.startswith('application/json'):
                return response.json()
            return response.text
        except HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err} - Response: {response.text}")
            raise
        except ValueError as parse_err:
            logger.error(f"Error parsing JSON response: {parse_err} - Response: {response.text}")
            return response.text

    def get(self, endpoint, params=None):
        """
        Sends a GET request to the external API.

        :param endpoint: API endpoint to target.
        :param params: Query parameters for the request.
        :return: Response data.
        """
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            logger.debug(f"Sending GET request to {url} with params {params}")
            response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            return self._handle_response(response)
        except Timeout:
            logger.error("GET request timed out.")
            raise
        except RequestException as e:
            logger.error(f"Error during GET request: {e}")
            raise

    def post(self, endpoint, data=None, json=None):
        """
        Sends a POST request to the external API.

        :param endpoint: API endpoint to target.
        :param data: Form data to include in the request body.
        :param json: JSON data to include in the request body.
        :return: Response data.
        """
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            logger.debug(f"Sending POST request to {url} with data {data} and json {json}")
            response = requests.post(url, headers=self.headers, data=data, json=json, timeout=self.timeout)
            return self._handle_response(response)
        except Timeout:
            logger.error("POST request timed out.")
            raise
        except RequestException as e:
            logger.error(f"Error during POST request: {e}")
            raise

    def put(self, endpoint, data=None, json=None):
        """
        Sends a PUT request to the external API.

        :param endpoint: API endpoint to target.
        :param data: Form data to include in the request body.
        :param json: JSON data to include in the request body.
        :return: Response data.
        """
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            logger.debug(f"Sending PUT request to {url} with data {data} and json {json}")
            response = requests.put(url, headers=self.headers, data=data, json=json, timeout=self.timeout)
            return self._handle_response(response)
        except Timeout:
            logger.error("PUT request timed out.")
            raise
        except RequestException as e:
            logger.error(f"Error during PUT request: {e}")
            raise

    def delete(self, endpoint, params=None):
        """
        Sends a DELETE request to the external API.

        :param endpoint: API endpoint to target.
        :param params: Query parameters for the request.
        :return: Response data.
        """
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            logger.debug(f"Sending DELETE request to {url} with params {params}")
            response = requests.delete(url, headers=self.headers, params=params, timeout=self.timeout)
            return self._handle_response(response)
        except Timeout:
            logger.error("DELETE request timed out.")
            raise
        except RequestException as e:
            logger.error(f"Error during DELETE request: {e}")
            raise

# Example Usage:
# connector = ExternalAPIConnector(base_url="https://api.example.com", headers={"Authorization": "Bearer token"})
# response = connector.get("/data")

"""
api_connector.py

This module provides a robust APIConnector class for interacting with external APIs.
It is designed to serve both RLG Data and RLG Fans by supporting GET, POST, PUT, and DELETE
requests with built-in error handling, retries, logging, and flexible configuration.
"""

import requests
from requests.adapters import HTTPAdapter, Retry
import logging

class APIConnector:
    def __init__(self, config):
        """
        Initializes the APIConnector.

        Parameters:
            config (dict): A configuration dictionary that should contain an 'endpoints' key.
                           The 'endpoints' value is another dictionary where each key is a
                           unique endpoint name and its value is a dictionary with:
                             - 'url': The API endpoint URL.
                             - 'headers': (Optional) A dict of headers to include.
                             - 'api_key': (Optional) An API key to be used for authorization.
        """
        self.config = config

        # Setup a requests Session with retry strategy to handle transient errors.
        self.session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Configure logging
        self.logger = logging.getLogger("APIConnector")
        self.logger.setLevel(logging.DEBUG)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _prepare_headers(self, endpoint_config):
        """
        Prepares headers for the API call. If an API key is provided in the endpoint configuration,
        it adds it as a Bearer token.

        Parameters:
            endpoint_config (dict): Configuration for the particular endpoint.

        Returns:
            dict: Headers dictionary for the API request.
        """
        headers = endpoint_config.get("headers", {}).copy()
        api_key = endpoint_config.get("api_key")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers

    def get(self, endpoint_name, params=None):
        """
        Performs a GET request to the specified endpoint.

        Parameters:
            endpoint_name (str): The key for the desired endpoint in the config.
            params (dict, optional): Query parameters for the request.

        Returns:
            dict: JSON response from the API.

        Raises:
            ValueError: If the endpoint is not found in the configuration.
            requests.exceptions.RequestException: For request-related errors.
        """
        if endpoint_name not in self.config.get("endpoints", {}):
            self.logger.error(f"Endpoint '{endpoint_name}' not found in configuration.")
            raise ValueError(f"Invalid endpoint: {endpoint_name}")

        endpoint_config = self.config["endpoints"][endpoint_name]
        url = endpoint_config["url"]
        headers = self._prepare_headers(endpoint_config)

        try:
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            self.logger.debug(f"GET {url} with params {params} succeeded.")
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"GET request to {url} failed: {e}")
            raise

    def post(self, endpoint_name, data=None, json_data=None):
        """
        Performs a POST request to the specified endpoint.

        Parameters:
            endpoint_name (str): The key for the desired endpoint in the config.
            data (dict, optional): Form data to be sent in the body of the request.
            json_data (dict, optional): JSON data to be sent in the body of the request.

        Returns:
            dict: JSON response from the API.

        Raises:
            ValueError: If the endpoint is not found.
            requests.exceptions.RequestException: For request-related errors.
        """
        if endpoint_name not in self.config.get("endpoints", {}):
            self.logger.error(f"Endpoint '{endpoint_name}' not found in configuration.")
            raise ValueError(f"Invalid endpoint: {endpoint_name}")

        endpoint_config = self.config["endpoints"][endpoint_name]
        url = endpoint_config["url"]
        headers = self._prepare_headers(endpoint_config)

        try:
            response = self.session.post(url, data=data, json=json_data, headers=headers, timeout=10)
            response.raise_for_status()
            self.logger.debug(f"POST {url} succeeded with payload: {json_data or data}.")
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"POST request to {url} failed: {e}")
            raise

    def put(self, endpoint_name, data=None, json_data=None):
        """
        Performs a PUT request to the specified endpoint.

        Parameters:
            endpoint_name (str): The key for the desired endpoint in the config.
            data (dict, optional): Form data for the request.
            json_data (dict, optional): JSON data for the request.

        Returns:
            dict: JSON response from the API.

        Raises:
            ValueError: If the endpoint is not found.
            requests.exceptions.RequestException: For request-related errors.
        """
        if endpoint_name not in self.config.get("endpoints", {}):
            self.logger.error(f"Endpoint '{endpoint_name}' not found in configuration.")
            raise ValueError(f"Invalid endpoint: {endpoint_name}")

        endpoint_config = self.config["endpoints"][endpoint_name]
        url = endpoint_config["url"]
        headers = self._prepare_headers(endpoint_config)

        try:
            response = self.session.put(url, data=data, json=json_data, headers=headers, timeout=10)
            response.raise_for_status()
            self.logger.debug(f"PUT {url} succeeded with payload: {json_data or data}.")
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"PUT request to {url} failed: {e}")
            raise

    def delete(self, endpoint_name, params=None):
        """
        Performs a DELETE request to the specified endpoint.

        Parameters:
            endpoint_name (str): The key for the desired endpoint in the config.
            params (dict, optional): Query parameters for the DELETE request.

        Returns:
            dict: JSON response from the API.

        Raises:
            ValueError: If the endpoint is not found.
            requests.exceptions.RequestException: For request-related errors.
        """
        if endpoint_name not in self.config.get("endpoints", {}):
            self.logger.error(f"Endpoint '{endpoint_name}' not found in configuration.")
            raise ValueError(f"Invalid endpoint: {endpoint_name}")

        endpoint_config = self.config["endpoints"][endpoint_name]
        url = endpoint_config["url"]
        headers = self._prepare_headers(endpoint_config)

        try:
            response = self.session.delete(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            self.logger.debug(f"DELETE {url} with params {params} succeeded.")
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"DELETE request to {url} failed: {e}")
            raise

    def health_check(self, endpoint_name):
        """
        Performs a basic GET request to check the connectivity of an endpoint.

        Parameters:
            endpoint_name (str): The key for the desired endpoint in the config.

        Returns:
            bool: True if the health check passes; False otherwise.
        """
        try:
            self.get(endpoint_name)
            self.logger.info(f"Health check passed for endpoint: {endpoint_name}")
            return True
        except Exception as e:
            self.logger.error(f"Health check failed for endpoint: {endpoint_name} with error: {e}")
            return False

# --------------------------
# Recommendations:
# --------------------------
# 1. Consider integrating a caching mechanism (e.g., requests_cache) if you expect a high volume of
#    repeated API calls and need to reduce latency.
# 2. For scaling and asynchronous processing, you might later refactor these methods using an async HTTP
#    client (e.g., aiohttp) if your application demands concurrent processing.
# 3. Include unit tests for each API method to ensure reliability under various scenarios.
# 4. Monitor and adjust timeout and retry parameters based on real-world API response times.
# 5. Ensure that sensitive data like API keys are stored securely (for instance, using environment variables
#    or a secure vault) rather than hardcoding them in configuration files.

# Example usage (this part is for demonstration and should be moved to a separate test or main file):
if __name__ == "__main__":
    # Sample configuration for demonstration
    sample_config = {
        "endpoints": {
            "rlg_data": {
                "url": "https://api.rlgdata.example.com/v1/data",
                "api_key": "YOUR_RLG_DATA_API_KEY",
                "headers": {"Content-Type": "application/json"}
            },
            "rlg_fans": {
                "url": "https://api.rlgfans.example.com/v1/fans",
                "api_key": "YOUR_RLG_FANS_API_KEY",
                "headers": {"Content-Type": "application/json"}
            }
        }
    }

    connector = APIConnector(sample_config)

    # Perform a health check on the RLG Data endpoint.
    if connector.health_check("rlg_data"):
        print("RLG Data endpoint is healthy.")
    else:
        print("RLG Data endpoint health check failed.")

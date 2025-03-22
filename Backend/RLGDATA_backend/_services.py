import requests
import logging
from typing import Any, Dict, Optional

# Initialize logging
logging.basicConfig(level=logging.INFO)

class BaseService:
    """
    Base template for a scraping or data-fetching service. This class includes 
    generic methods for API requests, error handling, and authentication.
    """

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize the service with a base URL and an optional API key.
        
        :param base_url: The root URL of the service's API.
        :param api_key: The API key for the service, if required.
        """
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
            "Content-Type": "application/json",
        }

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform a GET request to the specified endpoint.
        
        :param endpoint: API endpoint (relative to `base_url`) to request data from.
        :param params: Optional dictionary of query parameters.
        :return: Response data as a dictionary.
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            logging.info(f"GET request to {url} successful.")
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Error with GET request to {url}: {e}")
            return {"error": str(e)}

    def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform a POST request to the specified endpoint.
        
        :param endpoint: API endpoint to post data to.
        :param data: Payload to send in the POST request.
        :return: Response data as a dictionary.
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            logging.info(f"POST request to {url} successful.")
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Error with POST request to {url}: {e}")
            return {"error": str(e)}

    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """
        Handle service-specific authentication if required.
        
        :param credentials: Dictionary containing necessary login information.
        :return: Boolean indicating success or failure.
        """
        if not self.api_key:
            logging.error("API key not found for authentication.")
            return False
        auth_endpoint = "auth/login"  # Replace with actual authentication endpoint if needed
        response = self._post(auth_endpoint, data=credentials)
        if "access_token" in response:
            self.headers["Authorization"] = f"Bearer {response['access_token']}"
            logging.info("Authentication successful.")
            return True
        else:
            logging.error("Authentication failed.")
            return False

    def fetch_data(self, query: str) -> Dict[str, Any]:
        """
        Fetch data based on a specific query. Intended to be overridden or used as-is.
        
        :param query: Query string to search for.
        :return: Dictionary containing query results.
        """
        endpoint = f"search?q={query}"  # Replace with appropriate endpoint
        return self._get(endpoint)

    def log_and_handle_error(self, error_message: str) -> None:
        """
        Log errors and handle them for consistent error reporting.
        
        :param error_message: Custom error message to log.
        """
        logging.error(error_message)


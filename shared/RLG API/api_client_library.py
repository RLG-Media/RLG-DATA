import requests
import logging
from typing import Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("api_client_library.log"),
        logging.StreamHandler()
    ]
)

class APIClient:
    """
    A generic API client for managing HTTP requests to external services.
    This client is designed to support RLG Data and RLG Fans integrations.
    """

    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
        """
        Initialize the API client.

        Args:
            base_url: The base URL of the API.
            headers: Default headers to include in all requests.
        """
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        logging.info("APIClient initialized with base URL: %s", self.base_url)

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Send a GET request to the API.

        Args:
            endpoint: The API endpoint (relative to the base URL).
            params: Query parameters to include in the request.

        Returns:
            A dictionary containing the API response.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            logging.info("GET request to %s successful.", url)
            return response.json()
        except requests.RequestException as e:
            logging.error("GET request to %s failed: %s", url, e)
            return {"error": str(e)}

    def post(self, endpoint: str, data: Optional[Dict] = None, json: Optional[Dict] = None) -> Dict:
        """
        Send a POST request to the API.

        Args:
            endpoint: The API endpoint (relative to the base URL).
            data: Form-encoded data to include in the request.
            json: JSON data to include in the request.

        Returns:
            A dictionary containing the API response.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.post(url, headers=self.headers, data=data, json=json)
            response.raise_for_status()
            logging.info("POST request to %s successful.", url)
            return response.json()
        except requests.RequestException as e:
            logging.error("POST request to %s failed: %s", url, e)
            return {"error": str(e)}

    def put(self, endpoint: str, data: Optional[Dict] = None, json: Optional[Dict] = None) -> Dict:
        """
        Send a PUT request to the API.

        Args:
            endpoint: The API endpoint (relative to the base URL).
            data: Form-encoded data to include in the request.
            json: JSON data to include in the request.

        Returns:
            A dictionary containing the API response.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.put(url, headers=self.headers, data=data, json=json)
            response.raise_for_status()
            logging.info("PUT request to %s successful.", url)
            return response.json()
        except requests.RequestException as e:
            logging.error("PUT request to %s failed: %s", url, e)
            return {"error": str(e)}

    def delete(self, endpoint: str) -> Dict:
        """
        Send a DELETE request to the API.

        Args:
            endpoint: The API endpoint (relative to the base URL).

        Returns:
            A dictionary containing the API response.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            logging.info("DELETE request to %s successful.", url)
            return response.json()
        except requests.RequestException as e:
            logging.error("DELETE request to %s failed: %s", url, e)
            return {"error": str(e)}

    def set_auth_token(self, token: str):
        """
        Set the Authorization header with a bearer token.

        Args:
            token: The bearer token to include in requests.
        """
        self.headers["Authorization"] = f"Bearer {token}"
        logging.info("Authorization token set.")

# Example usage
if __name__ == "__main__":
    client = APIClient("https://api.example.com", headers={"User-Agent": "RLG-Client/1.0"})

    # Set authentication token
    client.set_auth_token("example_token")

    # Perform a GET request
    response = client.get("/example-endpoint", params={"key": "value"})
    print("GET Response:", response)

    # Perform a POST request
    response = client.post("/example-endpoint", json={"key": "value"})
    print("POST Response:", response)

    # Perform a PUT request
    response = client.put("/example-endpoint", json={"key": "updated_value"})
    print("PUT Response:", response)

    # Perform a DELETE request
    response = client.delete("/example-endpoint")
    print("DELETE Response:", response)

# platform_integration.py

import requests
import pandas as pd

class PlatformIntegration:
    """
    PlatformIntegration class to handle seamless integration with various social media and content platforms.
    """
    def __init__(self, api_credentials, platform_url_map):
        """
        Initializes the PlatformIntegration with API credentials and a URL map for various platforms.

        :param api_credentials: A dictionary containing API keys and secrets for different platforms.
        :param platform_url_map: A dictionary mapping platform names to their respective API base URLs.
        """
        self.api_credentials = api_credentials
        self.platform_url_map = platform_url_map

    def _get_headers(self, platform):
        """
        Generates the headers required for API requests for a specific platform.

        :param platform: Name of the platform.
        :return: A dictionary containing the headers including the API key.
        """
        headers = {
            'Authorization': f'Bearer {self.api_credentials[platform]["api_key"]}',
            'Content-Type': 'application/json'
        }
        return headers

    def _send_request(self, platform, endpoint, method='GET', params=None, data=None):
        """
        Sends an API request to the specified platform.

        :param platform: Name of the platform.
        :param endpoint: API endpoint relative to the platform's base URL.
        :param method: HTTP method (GET, POST, PUT, DELETE).
        :param params: Query parameters for the request.
        :param data: Payload for POST and PUT requests.
        :return: JSON response from the API.
        """
        url = f"{self.platform_url_map[platform]}{endpoint}"
        headers = self._get_headers(platform)
        
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, json=data)

        if response.status_code not in [200, 201]:
            raise Exception(f"Error {response.status_code}: {response.text}")
        return response.json()

    def fetch_content(self, platform, content_type, params=None):
        """
        Fetches content from the specified platform.

        :param platform: Name of the platform.
        :param content_type: Type of content to fetch (e.g., 'posts', 'videos', 'articles').
        :param params: Query parameters for the content fetch.
        :return: Content fetched from the platform.
        """
        endpoint = f'/v1/{content_type}'
        response = self._send_request(platform, endpoint, method='GET', params=params)
        return response.get('data', [])

    def post_content(self, platform, content_data):
        """
        Posts content to a specified platform.

        :param platform: Name of the platform.
        :param content_data: Dictionary containing content data (title, description, media, etc.).
        :return: Response from the platform indicating success or failure.
        """
        endpoint = '/v1/content'
        response = self._send_request(platform, endpoint, method='POST', data=content_data)
        return response

    def update_content(self, platform, content_id, content_data):
        """
        Updates content on a specified platform.

        :param platform: Name of the platform.
        :param content_id: ID of the content to be updated.
        :param content_data: Updated content data.
        :return: Response from the platform indicating success or failure.
        """
        endpoint = f'/v1/content/{content_id}'
        response = self._send_request(platform, endpoint, method='PUT', data=content_data)
        return response

    def delete_content(self, platform, content_id):
        """
        Deletes content from a specified platform.

        :param platform: Name of the platform.
        :param content_id: ID of the content to be deleted.
        :return: Response from the platform indicating success or failure.
        """
        endpoint = f'/v1/content/{content_id}'
        response = self._send_request(platform, endpoint, method='DELETE')
        return response

    def get_analytics(self, platform, analytics_type, params=None):
        """
        Fetches analytics data from the specified platform.

        :param platform: Name of the platform.
        :param analytics_type: Type of analytics data to fetch (e.g., 'engagement', 'reach', 'follower_growth').
        :param params: Query parameters for the analytics fetch.
        :return: Analytics data from the platform.
        """
        endpoint = f'/v1/analytics/{analytics_type}'
        response = self._send_request(platform, endpoint, method='GET', params=params)
        return response.get('data', [])

    def save_integration_state(self, filepath):
        """
        Saves the current state of the integration (API credentials and URLs) to a file.

        :param filepath: Path where the integration state should be saved.
        """
        pd.to_pickle((self.api_credentials, self.platform_url_map), filepath)

    def load_integration_state(self, filepath):
        """
        Loads a saved integration state from a file.

        :param filepath: Path to the saved integration state.
        """
        self.api_credentials, self.platform_url_map = pd.read_pickle(filepath)

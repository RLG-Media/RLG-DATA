# third_party_integration.py

import requests
from requests.exceptions import HTTPError, RequestException
import json
from some_module import handle_third_party_error  # Assuming you have a module for error handling

class ThirdPartyIntegration:
    """
    ThirdPartyIntegration class to handle communication with external APIs.
    """
    def __init__(self, api_base_url, api_key):
        """
        Initializes the ThirdPartyIntegration class with the base URL and API key.

        :param api_base_url: Base URL for the third-party API.
        :param api_key: API key to authenticate requests.
        """
        self.api_base_url = api_base_url
        self.api_key = api_key

    def _send_request(self, endpoint, method='GET', params=None, data=None, headers=None):
        """
        Sends a request to the third-party API.

        :param endpoint: API endpoint to hit.
        :param method: HTTP method (GET/POST/PUT/DELETE).
        :param params: Parameters for the request.
        :param data: Payload for the request.
        :param headers: Custom headers for the request.
        :return: JSON response from the API.
        """
        url = f"{self.api_base_url}/{endpoint}"
        headers = headers if headers else {}
        headers.update({'Authorization': f'Bearer {self.api_key}'})

        try:
            response = requests.request(method, url, params=params, json=data, headers=headers)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
            return response.json()
        except HTTPError as http_err:
            handle_third_party_error(http_err)  # Handle specific HTTP error
        except RequestException as req_err:
            handle_third_party_error(req_err)  # Handle general request error

    def get_data(self, endpoint, params=None):
        """
        Fetches data from the third-party API.

        :param endpoint: API endpoint to retrieve data from.
        :param params: Optional parameters for filtering the data.
        :return: Data retrieved from the API.
        """
        return self._send_request(endpoint, method='GET', params=params)

    def post_data(self, endpoint, data=None):
        """
        Sends data to the third-party API.

        :param endpoint: API endpoint to post data to.
        :param data: Payload to send to the API.
        :return: Response from the API.
        """
        return self._send_request(endpoint, method='POST', data=data)

    def put_data(self, endpoint, data=None):
        """
        Updates data via the third-party API.

        :param endpoint: API endpoint to update data at.
        :param data: Payload to update.
        :return: Response from the API.
        """
        return self._send_request(endpoint, method='PUT', data=data)

    def delete_data(self, endpoint, params=None):
        """
        Deletes data via the third-party API.

        :param endpoint: API endpoint to delete data from.
        :param params: Optional parameters to specify which data to delete.
        :return: Response from the API.
        """
        return self._send_request(endpoint, method='DELETE', params=params)

# Example usage:
# api_integration = ThirdPartyIntegration('https://api.example.com', 'your_api_key')
# response = api_integration.get_data('endpoint_path', {'param1': 'value1'})
# print(response)

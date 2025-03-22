import requests
import logging

class FanfixService:
    def __init__(self, access_token):
        """
        Initialize the Fanfix service with an access token for API authentication.
        """
        self.access_token = access_token
        self.api_url = "https://api.fanfix.io"  # Update with actual Fanfix API URL if available.
        self.headers = {"Authorization": f"Bearer {self.access_token}"}
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_profile_data(self, user_id):
        """
        Fetch profile data for a specific Fanfix user.
        """
        try:
            url = f"{self.api_url}/users/{user_id}"
            response = self.session.get(url)
            response.raise_for_status()
            logging.info(f"Fetched profile data for user {user_id}.")
            return response.json()  # Return JSON data of the user profile
        except requests.RequestException as e:
            logging.error(f"Failed to fetch profile data for user {user_id}: {e}")
            return None

    def get_fan_data(self, user_id):
        """
        Fetch fan data (e.g., number of fans, engagement, etc.) for a Fanfix user.
        """
        try:
            url = f"{self.api_url}/users/{user_id}/fans"
            response = self.session.get(url)
            response.raise_for_status()
            logging.info(f"Fetched fan data for user {user_id}.")
            return response.json()  # Return fan-related statistics
        except requests.RequestException as e:
            logging.error(f"Failed to fetch fan data for user {user_id}: {e}")
            return None

    def get_post_data(self, user_id):
        """
        Fetch post data (e.g., engagement on posts, views, likes) for a Fanfix user.
        """
        try:
            url = f"{self.api_url}/users/{user_id}/posts"
            response = self.session.get(url)
            response.raise_for_status()
            logging.info(f"Fetched post data for user {user_id}.")
            return response.json()  # Return post-related statistics
        except requests.RequestException as e:
            logging.error(f"Failed to fetch post data for user {user_id}: {e}")
            return None

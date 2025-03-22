import requests
import logging

class FanslyService:
    def __init__(self, access_token):
        """
        Initialize the Fansly service with an access token for API authentication.
        """
        self.access_token = access_token
        self.api_url = "https://api.fansly.com"  # Update with the actual Fansly API URL if available.
        self.headers = {"Authorization": f"Bearer {self.access_token}"}
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_profile_data(self, user_id):
        """
        Fetch profile data for a specific Fansly user.
        """
        try:
            url = f"{self.api_url}/users/{user_id}"
            response = self.session.get(url)
            response.raise_for_status()
            logging.info(f"Fetched profile data for user {user_id} on Fansly.")
            return response.json()  # Return JSON data of the user profile
        except requests.RequestException as e:
            logging.error(f"Failed to fetch profile data for user {user_id} on Fansly: {e}")
            return None

    def get_follower_data(self, user_id):
        """
        Fetch follower data for a Fansly user.
        """
        try:
            url = f"{self.api_url}/users/{user_id}/followers"
            response = self.session.get(url)
            response.raise_for_status()
            logging.info(f"Fetched follower data for user {user_id} on Fansly.")
            return response.json()  # Return fan/follower data
        except requests.RequestException as e:
            logging.error(f"Failed to fetch follower data for user {user_id} on Fansly: {e}")
            return None

    def get_content_data(self, user_id):
        """
        Fetch content data (posts, videos, etc.) for a Fansly user.
        """
        try:
            url = f"{self.api_url}/users/{user_id}/content"
            response = self.session.get(url)
            response.raise_for_status()
            logging.info(f"Fetched content data for user {user_id} on Fansly.")
            return response.json()  # Return post/content data
        except requests.RequestException as e:
            logging.error(f"Failed to fetch content data for user {user_id} on Fansly: {e}")
            return None

import requests
import logging

class IFansService:
    def __init__(self, access_token):
        """
        Initialize the iFans service with an access token for API authentication.
        """
        self.access_token = access_token
        self.api_url = "https://api.ifans.com"  # Update with actual iFans API URL if available.
        self.headers = {"Authorization": f"Bearer {self.access_token}"}
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_profile_data(self, user_id):
        """
        Fetch profile data for a specific iFans user.
        """
        try:
            url = f"{self.api_url}/users/{user_id}"
            response = self.session.get(url)
            response.raise_for_status()
            logging.info(f"Fetched profile data for user {user_id} on iFans.")
            return response.json()  # Return JSON data of the user profile
        except requests.RequestException as e:
            logging.error(f"Failed to fetch profile data for user {user_id} on iFans: {e}")
            return None

    def get_subscribers_data(self, user_id):
        """
        Fetch subscriber data for an iFans user.
        """
        try:
            url = f"{self.api_url}/users/{user_id}/subscribers"
            response = self.session.get(url)
            response.raise_for_status()
            logging.info(f"Fetched subscriber data for user {user_id} on iFans.")
            return response.json()  # Return subscriber data
        except requests.RequestException as e:
            logging.error(f"Failed to fetch subscriber data for user {user_id} on iFans: {e}")
            return None

    def get_posts_data(self, user_id):
        """
        Fetch content data (posts, videos, etc.) for an iFans user.
        """
        try:
            url = f"{self.api_url}/users/{user_id}/posts"
            response = self.session.get(url)
            response.raise_for_status()
            logging.info(f"Fetched content data for user {user_id} on iFans.")
            return response.json()  # Return post/content data
        except requests.RequestException as e:
            logging.error(f"Failed to fetch content data for user {user_id} on iFans: {e}")
            return None

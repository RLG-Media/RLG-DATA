import requests
import logging

class UnlockedService:
    def __init__(self, access_token):
        """
        Initialize the Unlocked service with an access token for API authentication.
        """
        self.access_token = access_token
        self.api_url = "https://api.unlocked.com/v1"  # Unlocked API base URL
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_profile_data(self, creator_id):
        """
        Fetch profile data for a specific creator on Unlocked.
        """
        try:
            url = f"{self.api_url}/creators/{creator_id}/profile"
            response = self.session.get(url)
            response.raise_for_status()
            logging.info(f"Fetched profile data for creator {creator_id} on Unlocked.")
            return response.json()  # Return the creator's profile data
        except requests.RequestException as e:
            logging.error(f"Failed to fetch profile data for creator {creator_id} on Unlocked: {e}")
            return None

    def get_creator_posts(self, creator_id):
        """
        Fetch posts by a specific creator on Unlocked.
        """
        try:
            url = f"{self.api_url}/creators/{creator_id}/posts"
            response = self.session.get(url)
            response.raise_for_status()
            logging.info(f"Fetched posts for creator {creator_id} on Unlocked.")
            return response.json()  # Return the creator's posts
        except requests.RequestException as e:
            logging.error(f"Failed to fetch posts for creator {creator_id} on Unlocked: {e}")
            return None

    def get_creator_subscribers(self, creator_id):
        """
        Fetch subscriber data for a specific creator on Unlocked.
        """
        try:
            url = f"{self.api_url}/creators/{creator_id}/subscribers"
            response = self.session.get(url)
            response.raise_for_status()
            logging.info(f"Fetched subscriber data for creator {creator_id} on Unlocked.")
            return response.json()  # Return the creator's subscriber data
        except requests.RequestException as e:
            logging.error(f"Failed to fetch subscriber data for creator {creator_id} on Unlocked: {e}")
            return None

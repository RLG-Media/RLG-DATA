import requests
import logging

class AdultNodeService:
    def __init__(self, access_token):
        """
        Initialize the AdultNode service with an access token for API authentication.
        """
        self.access_token = access_token
        self.api_url = "https://api.adultnode.com/v1"  # AdultNode API base URL
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_creator_profile(self, creator_id):
        """
        Fetch profile data for a specific creator on AdultNode.
        """
        try:
            url = f"{self.api_url}/creators/{creator_id}/profile"
            response = self.session.get(url)
            response.raise_for_status()
            logging.info(f"Fetched profile data for creator {creator_id} on AdultNode.")
            return response.json()  # Return the creator's profile data
        except requests.RequestException as e:
            logging.error(f"Failed to fetch profile data for creator {creator_id} on AdultNode: {e}")
            return None

    def get_creator_posts(self, creator_id):
        """
        Fetch posts by a specific creator on AdultNode.
        """
        try:
            url = f"{self.api_url}/creators/{creator_id}/posts"
            response = self.session.get(url)
            response.raise_for_status()
            logging.info(f"Fetched posts for creator {creator_id} on AdultNode.")
            return response.json()  # Return the creator's posts
        except requests.RequestException as e:
            logging.error(f"Failed to fetch posts for creator {creator_id} on AdultNode: {e}")
            return None

    def get_creator_fans(self, creator_id):
        """
        Fetch fan data for a specific creator on AdultNode.
        """
        try:
            url = f"{self.api_url}/creators/{creator_id}/fans"
            response = self.session.get(url)
            response.raise_for_status()
            logging.info(f"Fetched fan data for creator {creator_id} on AdultNode.")
            return response.json()  # Return the creator's fan data
        except requests.RequestException as e:
            logging.error(f"Failed to fetch fan data for creator {creator_id} on AdultNode: {e}")
            return None

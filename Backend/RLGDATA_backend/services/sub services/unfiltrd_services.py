import requests
import logging

class UnfiltrdService:
    def __init__(self, access_token):
        """
        Initialize the Unfiltrd service with an access token for API authentication.
        """
        self.access_token = access_token
        self.api_url = "https://api.unfiltrd.com/v1"  # Unfiltrd API base URL
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_creator_profile(self, creator_id):
        """
        Fetch profile data for a specific creator on Unfiltrd.
        """
        try:
            url = f"{self.api_url}/creators/{creator_id}/profile"
            response = self.session.get(url)
            response.raise_for_status()
            logging.info(f"Fetched profile data for creator {creator_id} on Unfiltrd.")
            return response.json()  # Return the creator's profile data
        except requests.RequestException as e:
            logging.error(f"Failed to fetch profile data for creator {creator_id} on Unfiltrd: {e}")
            return None

    def get_creator_content(self, creator_id):
        """
        Fetch content by a specific creator on Unfiltrd.
        """
        try:
            url = f"{self.api_url}/creators/{creator_id}/content"
            response = self.session.get(url)
            response.raise_for_status()
            logging.info(f"Fetched content for creator {creator_id} on Unfiltrd.")
            return response.json()  # Return the creator's content
        except requests.RequestException as e:
            logging.error(f"Failed to fetch content for creator {creator_id} on Unfiltrd: {e}")
            return None

    def get_creator_subscribers(self, creator_id):
        """
        Fetch subscriber data for a specific creator on Unfiltrd.
        """
        try:
            url = f"{self.api_url}/creators/{creator_id}/subscribers"
            response = self.session.get(url)
            response.raise_for_status()
            logging.info(f"Fetched subscriber data for creator {creator_id} on Unfiltrd.")
            return response.json()  # Return the creator's subscriber data
        except requests.RequestException as e:
            logging.error(f"Failed to fetch subscriber data for creator {creator_id} on Unfiltrd: {e}")
            return None

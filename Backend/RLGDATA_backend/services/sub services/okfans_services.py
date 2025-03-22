import requests
import logging

class OkFansService:
    def __init__(self, access_token):
        """
        Initialize the OkFans service with an access token for API authentication.
        """
        self.access_token = access_token
        self.api_url = "https://api.okfans.com/v1"  # OkFans API base URL
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_creator_profile(self, creator_id):
        """
        Fetch profile data for a specific creator on OkFans.
        """
        try:
            url = f"{self.api_url}/creators/{creator_id}/profile"
            response = self.session.get(url)
            response.raise_for_status()
            logging.info(f"Fetched profile data for creator {creator_id} on OkFans.")
            return response.json()  # Return the creator's profile data
        except requests.RequestException as e:
            logging.error(f"Failed to fetch profile data for creator {creator_id} on OkFans: {e}")
            return None

    def get_creator_posts(self, creator_id):
        """
        Fetch posts by a specific creator on OkFans.
        """
        try:
            url = f"{self.api_url}/creators/{creator_id}/posts"
            response = self.session.get(url)
            response.raise_for_status()
            logging.info(f"Fetched posts for creator {creator_id} on OkFans.")
            return response.json()  # Return the creator's post data
        except requests.RequestException as e:
            logging.error(f"Failed to fetch posts for creator {creator_id} on OkFans: {e}")
            return None

    def get_trending_creators(self):
        """
        Fetch trending creators on OkFans.
        """
        try:
            url = f"{self.api_url}/creators/trending"
            response = self.session.get(url)
            response.raise_for_status()
            logging.info("Fetched trending creators on OkFans.")
            return response.json()  # Return trending creators' data
        except requests.RequestException as e:
            logging.error(f"Failed to fetch trending creators on OkFans: {e}")
            return None

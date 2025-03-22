import requests
import logging

class FapelloService:
    def __init__(self, access_token):
        """
        Initialize the Fapello service with an access token for API authentication.
        """
        self.access_token = access_token
        self.api_url = "https://api.fapello.com/v1"  # Fapello API base URL
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_profile(self, profile_id):
        """
        Fetch profile data for a specific creator on Fapello.
        """
        try:
            url = f"{self.api_url}/creators/{profile_id}/profile"
            response = self.session.get(url)
            response.raise_for_status()
            logging.info(f"Fetched profile data for creator {profile_id} on Fapello.")
            return response.json()  # Return the profile data
        except requests.RequestException as e:
            logging.error(f"Failed to fetch profile data for creator {profile_id} on Fapello: {e}")
            return None

    def get_profile_content(self, profile_id):
        """
        Fetch content (photos and videos) from a specific creator on Fapello.
        """
        try:
            url = f"{self.api_url}/creators/{profile_id}/content"
            response = self.session.get(url)
            response.raise_for_status()
            logging.info(f"Fetched content for creator {profile_id} on Fapello.")
            return response.json()  # Return the content data
        except requests.RequestException as e:
            logging.error(f"Failed to fetch content for creator {profile_id} on Fapello: {e}")
            return None

    def get_trending_creators(self):
        """
        Fetch trending creators on Fapello.
        """
        try:
            url = f"{self.api_url}/creators/trending"
            response = self.session.get(url)
            response.raise_for_status()
            logging.info("Fetched trending creators on Fapello.")
            return response.json()  # Return trending creators' data
        except requests.RequestException as e:
            logging.error(f"Failed to fetch trending creators on Fapello: {e}")
            return None

import requests
import logging

class ManyVidsService:
    def __init__(self, access_token):
        """
        Initialize the ManyVids service with an access token for API authentication.
        """
        self.access_token = access_token
        self.api_url = "https://api.manyvids.com/v1"  # ManyVids API base URL
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_creator_profile(self, creator_id):
        """
        Fetch profile data for a specific creator on ManyVids.
        """
        try:
            url = f"{self.api_url}/creators/{creator_id}/profile"
            response = self.session.get(url)
            response.raise_for_status()
            logging.info(f"Fetched profile data for creator {creator_id} on ManyVids.")
            return response.json()  # Return the creator's profile data
        except requests.RequestException as e:
            logging.error(f"Failed to fetch profile data for creator {creator_id} on ManyVids: {e}")
            return None

    def get_creator_videos(self, creator_id):
        """
        Fetch videos by a specific creator on ManyVids.
        """
        try:
            url = f"{self.api_url}/creators/{creator_id}/videos"
            response = self.session.get(url)
            response.raise_for_status()
            logging.info(f"Fetched videos for creator {creator_id} on ManyVids.")
            return response.json()  # Return the creator's video data
        except requests.RequestException as e:
            logging.error(f"Failed to fetch videos for creator {creator_id} on ManyVids: {e}")
            return None

    def get_trending_videos(self):
        """
        Fetch trending videos on ManyVids.
        """
        try:
            url = f"{self.api_url}/videos/trending"
            response = self.session.get(url)
            response.raise_for_status()
            logging.info("Fetched trending videos on ManyVids.")
            return response.json()  # Return trending video data
        except requests.RequestException as e:
            logging.error(f"Failed to fetch trending videos on ManyVids: {e}")
            return None

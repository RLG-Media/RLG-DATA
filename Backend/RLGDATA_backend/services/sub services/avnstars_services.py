import requests
import logging

class AVNStarsService:
    def __init__(self, base_url, api_key):
        """
        Initialize the AVNStars service with the base URL and API key for the AVNStars platform.
        """
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self.session = requests.Session()

    def search_profile(self, profile_name):
        """
        Search for a profile on AVNStars by profile name.
        """
        try:
            url = f"{self.base_url}/profiles/search"
            params = {"query": profile_name}
            response = self.session.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            logging.info(f"Searched profile {profile_name} on AVNStars.")
            return response.json()  # Return search results
        except requests.RequestException as e:
            logging.error(f"Failed to search profile {profile_name} on AVNStars: {e}")
            return None

    def get_profile_details(self, profile_id):
        """
        Get details of a specific profile on AVNStars by profile ID.
        """
        try:
            url = f"{self.base_url}/profiles/{profile_id}"
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            logging.info(f"Fetched details for profile {profile_id} on AVNStars.")
            return response.json()  # Return profile details
        except requests.RequestException as e:
            logging.error(f"Failed to fetch profile details for {profile_id} on AVNStars: {e}")
            return None

    def get_trending_profiles(self):
        """
        Fetch trending profiles on AVNStars.
        """
        try:
            url = f"{self.base_url}/profiles/trending"
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            logging.info("Fetched trending profiles on AVNStars.")
            return response.json()  # Return trending profiles' data
        except requests.RequestException as e:
            logging.error(f"Failed to fetch trending profiles on AVNStars: {e}")
            return None

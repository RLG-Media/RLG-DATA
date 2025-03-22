import requests
import logging

class SimpCityService:
    def __init__(self, base_url):
        """
        Initialize the SimpCity service with the base URL for the SimpCity platform.
        """
        self.base_url = base_url
        self.session = requests.Session()

    def search_profile(self, profile_name):
        """
        Search for a profile on SimpCity by profile name.
        """
        try:
            url = f"{self.base_url}/profiles/search"
            params = {"query": profile_name}
            response = self.session.get(url, params=params)
            response.raise_for_status()
            logging.info(f"Searched profile {profile_name} on SimpCity.")
            return response.json()  # Return search results
        except requests.RequestException as e:
            logging.error(f"Failed to search profile {profile_name} on SimpCity: {e}")
            return None

    def get_profile_details(self, profile_id):
        """
        Get details of a specific profile on SimpCity by profile ID.
        """
        try:
            url = f"{self.base_url}/profiles/{profile_id}"
            response = self.session.get(url)
            response.raise_for_status()
            logging.info(f"Fetched details for profile {profile_id} on SimpCity.")
            return response.json()  # Return profile details
        except requests.RequestException as e:
            logging.error(f"Failed to fetch profile details for {profile_id} on SimpCity: {e}")
            return None

    def get_trending_profiles(self):
        """
        Fetch trending profiles on SimpCity.
        """
        try:
            url = f"{self.base_url}/profiles/trending"
            response = self.session.get(url)
            response.raise_for_status()
            logging.info("Fetched trending profiles on SimpCity.")
            return response.json()  # Return trending profiles' data
        except requests.RequestException as e:
            logging.error(f"Failed to fetch trending profiles on SimpCity: {e}")
            return None

import requests
import logging

class FansMetricsService:
    def __init__(self, api_key):
        """
        Initialize the FansMetrics service with the API key for authentication.
        """
        self.api_key = api_key
        self.api_url = "https://api.fansmetrics.com/v1"  # FansMetrics API base URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def search_creator(self, creator_name):
        """
        Search for a creator's profile data on FansMetrics.
        """
        try:
            url = f"{self.api_url}/creators/search"
            params = {"name": creator_name}
            response = self.session.get(url, params=params)
            response.raise_for_status()
            logging.info(f"Searched creator {creator_name} on FansMetrics.")
            return response.json()  # Return search results
        except requests.RequestException as e:
            logging.error(f"Failed to search creator {creator_name} on FansMetrics: {e}")
            return None

    def get_creator_stats(self, creator_id):
        """
        Fetch stats for a specific creator on FansMetrics.
        """
        try:
            url = f"{self.api_url}/creators/{creator_id}/stats"
            response = self.session.get(url)
            response.raise_for_status()
            logging.info(f"Fetched stats for creator {creator_id} on FansMetrics.")
            return response.json()  # Return creator's stats
        except requests.RequestException as e:
            logging.error(f"Failed to fetch stats for creator {creator_id} on FansMetrics: {e}")
            return None

    def get_trending_creators(self):
        """
        Fetch trending creators on FansMetrics.
        """
        try:
            url = f"{self.api_url}/creators/trending"
            response = self.session.get(url)
            response.raise_for_status()
            logging.info("Fetched trending creators on FansMetrics.")
            return response.json()  # Return trending creators' data
        except requests.RequestException as e:
            logging.error(f"Failed to fetch trending creators on FansMetrics: {e}")
            return None

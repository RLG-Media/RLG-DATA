import requests
import logging

class StripchatService:
    def __init__(self, base_url, api_key):
        """
        Initialize the Stripchat service with the base URL and API key for scraping or fetching data.
        """
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        self.headers = {
            'Authorization': f'Bearer {self.api_key}'
        }

    def search_model(self, model_name):
        """
        Search for a model on Stripchat by model name.
        """
        try:
            url = f"{self.base_url}/search/models"
            params = {"query": model_name}
            response = self.session.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            logging.info(f"Searched for model {model_name} on Stripchat.")
            return response.json()  # Return search results
        except requests.RequestException as e:
            logging.error(f"Failed to search for model {model_name} on Stripchat: {e}")
            return None

    def get_model_profile(self, model_id):
        """
        Get detailed profile information of a specific model by model ID.
        """
        try:
            url = f"{self.base_url}/models/{model_id}/profile"
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            logging.info(f"Fetched profile for model {model_id} on Stripchat.")
            return response.json()  # Return model profile data
        except requests.RequestException as e:
            logging.error(f"Failed to fetch profile for model {model_id} on Stripchat: {e}")
            return None

    def get_trending_models(self):
        """
        Fetch trending models on Stripchat.
        """
        try:
            url = f"{self.base_url}/models/trending"
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            logging.info("Fetched trending models on Stripchat.")
            return response.json()  # Return trending models' data
        except requests.RequestException as e:
            logging.error(f"Failed to fetch trending models on Stripchat: {e}")
            return None

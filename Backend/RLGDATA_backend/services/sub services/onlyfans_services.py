import requests
from flask import current_app

class OnlyFansService:
    """
    Service class for interacting with the OnlyFans API.
    """
    BASE_URL = 'https://onlyfans.com/api/'  # Placeholder for OnlyFans API base URL

    def __init__(self, user_token):
        self.user_token = user_token

    def get_user_data(self):
        """
        Fetch user data from OnlyFans.
        """
        url = f"{self.BASE_URL}user"
        headers = {
            'Authorization': f'Bearer {self.user_token}'
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            current_app.logger.error(f"Failed to fetch user data: {response.text}")
            return None

    def get_content(self):
        """
        Fetch content from OnlyFans.
        """
        url = f"{self.BASE_URL}content"
        headers = {
            'Authorization': f'Bearer {self.user_token}'
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            current_app.logger.error(f"Failed to fetch content: {response.text}")
            return None

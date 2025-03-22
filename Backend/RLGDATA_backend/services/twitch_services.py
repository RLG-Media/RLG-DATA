import requests
import logging


class TwitchService:
    """
    Service class for interacting with the Twitch API.
    """
    BASE_URL = 'https://api.twitch.tv/helix/'  # Twitch API base URL

    def __init__(self, client_id, access_token):
        """
        Initialize the TwitchService with client ID and access token.

        :param client_id: The Client ID provided by Twitch.
        :param access_token: The access token for authenticating API requests.
        """
        self.client_id = client_id
        self.access_token = access_token
        self.session = requests.Session()

    def _get_headers(self):
        """
        Generate the authorization headers for the API requests.

        :return: Dictionary containing headers.
        """
        return {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

    def get_user_data(self, username):
        """
        Fetch user data from Twitch by username.

        :param username: The username of the Twitch user.
        :return: JSON response containing user information, or None if an error occurs.
        """
        try:
            url = f"{self.BASE_URL}users"
            params = {'login': username}
            response = self.session.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()

            logging.info(f"Successfully fetched user data for Twitch username: {username}.")
            return response.json()

        except requests.RequestException as e:
            logging.error(f"Failed to fetch user data from Twitch for username {username}: {e}")
            return None

    def get_streams(self, user_id):
        """
        Fetch live streams for a Twitch user by user ID.

        :param user_id: The ID of the Twitch user.
        :return: JSON response containing live streams, or None if an error occurs.
        """
        try:
            url = f"{self.BASE_URL}streams"
            params = {'user_id': user_id}
            response = self.session.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()

            logging.info(f"Successfully fetched live streams for Twitch user ID: {user_id}.")
            return response.json()

        except requests.RequestException as e:
            logging.error(f"Failed to fetch streams from Twitch for user ID {user_id}: {e}")
            return None

    def get_channel_videos(self, broadcaster_id, max_results=10):
        """
        Fetch videos from a Twitch channel by broadcaster ID.

        :param broadcaster_id: The ID of the Twitch broadcaster.
        :param max_results: Maximum number of videos to retrieve (default: 10).
        :return: JSON response containing channel videos, or None if an error occurs.
        """
        try:
            url = f"{self.BASE_URL}videos"
            params = {'broadcaster_id': broadcaster_id, 'first': max_results}
            response = self.session.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()

            logging.info(f"Successfully fetched {max_results} videos for Twitch channel ID: {broadcaster_id}.")
            return response.json()

        except requests.RequestException as e:
            logging.error(f"Failed to fetch videos from Twitch channel ID {broadcaster_id}: {e}")
            return None

    def get_followers(self, user_id):
        """
        Fetch followers of a Twitch user by user ID.

        :param user_id: The ID of the Twitch user.
        :return: JSON response containing followers, or None if an error occurs.
        """
        try:
            url = f"{self.BASE_URL}users/follows"
            params = {'to_id': user_id}
            response = self.session.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()

            logging.info(f"Successfully fetched followers for Twitch user ID: {user_id}.")
            return response.json()

        except requests.RequestException as e:
            logging.error(f"Failed to fetch followers from Twitch for user ID {user_id}: {e}")
            return None

    def get_categories(self, game_id):
        """
        Fetch categories related to a specific game on Twitch by game ID.

        :param game_id: The ID of the Twitch game.
        :return: JSON response containing categories, or None if an error occurs.
        """
        try:
            url = f"{self.BASE_URL}games"
            params = {'id': game_id}
            response = self.session.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()

            logging.info(f"Successfully fetched categories for game ID: {game_id}.")
            return response.json()

        except requests.RequestException as e:
            logging.error(f"Failed to fetch categories from Twitch for game ID {game_id}: {e}")
            return None

twitch_service = TwitchService(client_id="your-client-id", access_token="your-access-token")

user_data = twitch_service.get_user_data(username="example_username")
print(user_data)

live_streams = twitch_service.get_streams(user_id="123456")
print(live_streams)

channel_videos = twitch_service.get_channel_videos(broadcaster_id="123456", max_results=5)
print(channel_videos)

followers = twitch_service.get_followers(user_id="123456")
print(followers)

game_categories = twitch_service.get_categories(game_id="123456")
print(game_categories)

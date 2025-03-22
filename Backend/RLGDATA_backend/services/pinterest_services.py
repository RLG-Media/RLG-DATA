import requests
import logging

class PinterestService:
    """
    Service class for interacting with the Pinterest API.
    """

    BASE_URL = "https://api.pinterest.com/v5/"  # Updated to v5 for the latest Pinterest API version.

    def __init__(self, access_token):
        """
        Initialize the PinterestService with an access token for API authentication.

        :param access_token: The OAuth2 access token for authenticating with the Pinterest API.
        """
        self.access_token = access_token
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        })

    def fetch_data(self, endpoint, params=None):
        """
        General method for making GET requests to the Pinterest API.

        :param endpoint: The API endpoint to query.
        :param params: Optional query parameters.
        :return: JSON response data or None if an error occurs.
        """
        url = f"{self.BASE_URL}{endpoint}"
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            logging.info(f"Fetched data from Pinterest API: {endpoint}")
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Error fetching data from Pinterest API ({endpoint}): {e}")
            return None

    def post_data(self, endpoint, data):
        """
        General method for making POST requests to the Pinterest API.

        :param endpoint: The API endpoint to query.
        :param data: The payload to send in the POST request.
        :return: JSON response data or None if an error occurs.
        """
        url = f"{self.BASE_URL}{endpoint}"
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            logging.info(f"Successfully posted data to Pinterest API: {endpoint}")
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Error posting data to Pinterest API ({endpoint}): {e}")
            return None

    def get_user_profile(self):
        """
        Fetch user profile information from Pinterest.

        :return: User profile data or None if an error occurs.
        """
        return self.fetch_data("user_account")

    def get_boards(self):
        """
        Fetch all boards for the authenticated user.

        :return: List of boards or None if an error occurs.
        """
        return self.fetch_data("boards")

    def create_board(self, name, description=None):
        """
        Create a new board on Pinterest.

        :param name: The name of the board.
        :param description: Optional description of the board.
        :return: The created board data or None if an error occurs.
        """
        data = {
            "name": name,
            "description": description or ""
        }
        return self.post_data("boards", data)

    def create_pin(self, board_id, title, description, link, image_url):
        """
        Create a new pin on a specific board.

        :param board_id: The ID of the board where the pin will be created.
        :param title: The title of the pin.
        :param description: The description of the pin.
        :param link: The URL that the pin links to.
        :param image_url: The URL of the image to pin.
        :return: The created pin data or None if an error occurs.
        """
        data = {
            "board_id": board_id,
            "title": title,
            "description": description,
            "link": link,
            "media_source": {"source_type": "image_url", "url": image_url}
        }
        return self.post_data("pins", data)

    def get_pins_from_board(self, board_id, page_size=20, cursor=None):
        """
        Fetch all pins from a specific board.

        :param board_id: The ID of the board to retrieve pins from.
        :param page_size: The number of results per page (default is 20).
        :param cursor: The pagination cursor for fetching the next set of results.
        :return: List of pins or None if an error occurs.
        """
        params = {
            "page_size": page_size,
            "bookmark": cursor,
        }
        return self.fetch_data(f"boards/{board_id}/pins", params)

    def delete_pin(self, pin_id):
        """
        Delete a specific pin by its ID.

        :param pin_id: The ID of the pin to delete.
        :return: True if successful, False otherwise.
        """
        url = f"{self.BASE_URL}pins/{pin_id}"
        try:
            response = self.session.delete(url)
            if response.status_code == 204:
                logging.info(f"Successfully deleted pin with ID: {pin_id}")
                return True
            else:
                logging.error(f"Failed to delete pin with ID {pin_id}: {response.text}")
                return False
        except requests.RequestException as e:
            logging.error(f"Error deleting pin with ID {pin_id}: {e}")
            return False

    def refresh_access_token(self, client_id, client_secret, refresh_token):
        """
        Refresh the OAuth2 access token using a refresh token.

        :param client_id: The client ID of the Pinterest app.
        :param client_secret: The client secret of the Pinterest app.
        :param refresh_token: The refresh token for obtaining a new access token.
        :return: New access token data or None if the request fails.
        """
        url = "https://api.pinterest.com/v5/oauth/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
        }

        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            logging.info("Successfully refreshed Pinterest access token.")
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Failed to refresh Pinterest access token: {e}")
            return None

pinterest_service = PinterestService(access_token="your_access_token")
user_profile = pinterest_service.get_user_profile()

if user_profile:
    print("User Profile:", user_profile)
else:
    print("Failed to fetch user profile.")

new_pin = pinterest_service.create_pin(
    board_id="123456",
    title="My New Pin",
    description="Check out this awesome link!",
    link="https://example.com",
    image_url="https://example.com/image.jpg"
)

if new_pin:
    print("Created Pin:", new_pin)
else:
    print("Failed to create pin.")

new_token_data = pinterest_service.refresh_access_token(
    client_id="your_client_id",
    client_secret="your_client_secret",
    refresh_token="your_refresh_token"
)

if new_token_data:
    print("New Access Token:", new_token_data)
else:
    print("Failed to refresh access token.")

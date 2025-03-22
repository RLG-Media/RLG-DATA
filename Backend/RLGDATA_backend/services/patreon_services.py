import requests
import logging

class PatreonService:
    """
    Service class for interacting with the Patreon API.
    """

    API_BASE_URL = "https://www.patreon.com/api/oauth2/v2"

    def __init__(self, access_token):
        """
        Initialize the Patreon service with an access token for API authentication.

        :param access_token: The OAuth2 access token for authenticating with the Patreon API.
        """
        self.access_token = access_token
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        })

    def fetch_data(self, endpoint, params=None):
        """
        General method for making GET requests to the Patreon API.

        :param endpoint: The API endpoint to query.
        :param params: Optional query parameters.
        :return: JSON response data or None if an error occurs.
        """
        url = f"{self.API_BASE_URL}/{endpoint}"
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            logging.info(f"Fetched data from Patreon API: {endpoint}")
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Error fetching data from Patreon API ({endpoint}): {e}")
            return None

    def get_campaign_data(self, campaign_id, include=None):
        """
        Fetch data for a specific campaign on Patreon.

        :param campaign_id: The ID of the campaign.
        :param include: Optional related resources to include in the response (e.g., 'creator,tiers').
        :return: Campaign data or None.
        """
        params = {"include": include} if include else {}
        endpoint = f"campaigns/{campaign_id}"
        return self.fetch_data(endpoint, params)

    def get_pledges_data(self, campaign_id, page_size=20, cursor=None):
        """
        Fetch pledges data for a specific campaign on Patreon.

        :param campaign_id: The ID of the campaign.
        :param page_size: The number of results per page (default is 20).
        :param cursor: The pagination cursor for fetching the next set of results.
        :return: Pledge data or None.
        """
        params = {
            "page[size]": page_size,
            "page[cursor]": cursor,
        }
        endpoint = f"campaigns/{campaign_id}/members"
        return self.fetch_data(endpoint, params)

    def get_creator_posts(self, campaign_id, page_size=10, cursor=None):
        """
        Fetch creator posts for a specific campaign on Patreon.

        :param campaign_id: The ID of the campaign.
        :param page_size: The number of results per page (default is 10).
        :param cursor: The pagination cursor for fetching the next set of results.
        :return: Creator posts or None.
        """
        params = {
            "page[size]": page_size,
            "page[cursor]": cursor,
        }
        endpoint = f"campaigns/{campaign_id}/posts"
        return self.fetch_data(endpoint, params)

    def get_user_details(self):
        """
        Fetch authenticated user's details from Patreon.

        :return: User details or None.
        """
        endpoint = "identity"
        return self.fetch_data(endpoint)

    def refresh_access_token(self, client_id, client_secret, refresh_token):
        """
        Refresh the OAuth2 access token using a refresh token.

        :param client_id: The client ID of the Patreon app.
        :param client_secret: The client secret of the Patreon app.
        :param refresh_token: The refresh token for obtaining a new access token.
        :return: New access token data or None if the request fails.
        """
        url = "https://www.patreon.com/api/oauth2/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
        }

        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            logging.info("Successfully refreshed Patreon access token.")
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Failed to refresh Patreon access token: {e}")
            return None

patreon_service = PatreonService(access_token="your_access_token")
campaign_data = patreon_service.get_campaign_data(campaign_id="12345", include="creator,tiers")

if campaign_data:
    print("Campaign Data:", campaign_data)
else:
    print("Failed to fetch campaign data.")

pledge_data = patreon_service.get_pledges_data(campaign_id="12345", page_size=50)

if pledge_data:
    print("Pledge Data:", pledge_data)
else:
    print("Failed to fetch pledge data.")

new_token_data = patreon_service.refresh_access_token(
    client_id="your_client_id",
    client_secret="your_client_secret",
    refresh_token="your_refresh_token"
)

if new_token_data:
    print("New Access Token:", new_token_data)
else:
    print("Failed to refresh access token.")

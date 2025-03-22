import requests
import logging


class SnapchatService:
    """
    Service class for interacting with the Snapchat API.
    """
    BASE_URL = 'https://adsapi.snapchat.com/v1/'  # Updated Snapchat API base URL

    def __init__(self, access_token):
        """
        Initialize the SnapchatService with the provided access token.
        
        :param access_token: OAuth token for authenticating API requests.
        """
        self.access_token = access_token
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        })

    def get_user_profile(self):
        """
        Fetch the authenticated user's profile data from Snapchat.
        
        :return: User profile data or None if an error occurs.
        """
        try:
            url = f"{self.BASE_URL}me"
            response = self.session.get(url)
            response.raise_for_status()

            user_profile = response.json()
            logging.info("Successfully fetched user profile from Snapchat.")
            return user_profile

        except requests.RequestException as e:
            logging.error(f"Failed to fetch user profile from Snapchat: {e}")
            return None

    def send_snap(self, recipient_id, media_url, media_type="IMAGE"):
        """
        Send a snap to a user.
        
        :param recipient_id: The Snapchat ID of the recipient.
        :param media_url: URL of the media to be sent.
        :param media_type: Type of media being sent (default: "IMAGE").
        :return: Response data or None if an error occurs.
        """
        try:
            url = f"{self.BASE_URL}snaps/send"
            payload = {
                'recipient_id': recipient_id,
                'media_url': media_url,
                'media_type': media_type
            }

            response = self.session.post(url, json=payload)
            response.raise_for_status()

            logging.info(f"Successfully sent snap to recipient ID: {recipient_id}")
            return response.json()

        except requests.RequestException as e:
            logging.error(f"Failed to send snap to {recipient_id}: {e}")
            return None

    def get_ads_analytics(self, ad_account_id, start_date, end_date, metrics):
        """
        Fetch analytics data for ads within a specific date range.
        
        :param ad_account_id: Snapchat Ad Account ID.
        :param start_date: Start date for the analytics (YYYY-MM-DD).
        :param end_date: End date for the analytics (YYYY-MM-DD).
        :param metrics: List of metrics to fetch.
        :return: Analytics data or None if an error occurs.
        """
        try:
            url = f"{self.BASE_URL}adaccounts/{ad_account_id}/stats"
            payload = {
                'start_time': start_date,
                'end_time': end_date,
                'metrics': metrics
            }

            response = self.session.get(url, params=payload)
            response.raise_for_status()

            analytics_data = response.json()
            logging.info(f"Successfully fetched ad analytics for account ID: {ad_account_id}")
            return analytics_data

        except requests.RequestException as e:
            logging.error(f"Failed to fetch ad analytics for account ID {ad_account_id}: {e}")
            return None

    def upload_media(self, file_path, media_type="IMAGE"):
        """
        Upload media to Snapchat for use in ads or snaps.
        
        :param file_path: Local file path of the media to upload.
        :param media_type: Type of media being uploaded (default: "IMAGE").
        :return: Media ID or None if an error occurs.
        """
        try:
            url = f"{self.BASE_URL}media/upload"
            files = {'media': (file_path, open(file_path, 'rb'), 'application/octet-stream')}
            data = {'media_type': media_type}

            response = self.session.post(url, data=data, files=files)
            response.raise_for_status()

            media_id = response.json().get('media_id')
            logging.info(f"Successfully uploaded media. Media ID: {media_id}")
            return media_id

        except requests.RequestException as e:
            logging.error(f"Failed to upload media: {e}")
            return None

    def get_snap_analytics(self, snap_id, metrics):
        """
        Fetch analytics for a specific snap.
        
        :param snap_id: ID of the snap.
        :param metrics: List of metrics to fetch.
        :return: Snap analytics data or None if an error occurs.
        """
        try:
            url = f"{self.BASE_URL}snaps/{snap_id}/analytics"
            params = {'metrics': metrics}

            response = self.session.get(url, params=params)
            response.raise_for_status()

            analytics_data = response.json()
            logging.info(f"Successfully fetched analytics for snap ID: {snap_id}")
            return analytics_data

        except requests.RequestException as e:
            logging.error(f"Failed to fetch analytics for snap ID {snap_id}: {e}")
            return None

snapchat_service = SnapchatService(access_token="your-access-token")

profile = snapchat_service.get_user_profile()
print(profile)

response = snapchat_service.send_snap(
    recipient_id="recipient-id",
    media_url="https://example.com/snap.jpg",
    media_type="IMAGE"
)
print(response)

analytics = snapchat_service.get_ads_analytics(
    ad_account_id="account-id",
    start_date="2023-01-01",
    end_date="2023-12-31",
    metrics=["impressions", "clicks", "spend"]
)
print(analytics)

media_id = snapchat_service.upload_media(file_path="path/to/image.jpg")
print(media_id)

snap_analytics = snapchat_service.get_snap_analytics(
    snap_id="snap-id",
    metrics=["views", "screenshots", "replays"]
)
print(snap_analytics)

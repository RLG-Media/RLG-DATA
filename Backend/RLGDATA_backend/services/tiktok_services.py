import requests
import logging


class TikTokService:
    """
    Service class for interacting with the TikTok API.
    """
    BASE_URL = 'https://open.tiktokapis.com/v1/'  # Updated TikTok API base URL

    def __init__(self, access_token):
        """
        Initialize the TikTokService with an access token.
        
        :param access_token: The access token for authenticating TikTok API requests.
        """
        self.access_token = access_token
        self.session = requests.Session()

    def _get_headers(self):
        """
        Generate the authorization headers for the API requests.
        
        :return: Dictionary containing headers.
        """
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

    def get_user_info(self, user_id):
        """
        Fetch user information from TikTok.
        
        :param user_id: The unique ID of the TikTok user.
        :return: JSON response containing user information, or None if an error occurs.
        """
        try:
            url = f"{self.BASE_URL}users/{user_id}/info/"
            response = self.session.get(url, headers=self._get_headers())
            response.raise_for_status()

            logging.info(f"Successfully fetched user info for TikTok user ID {user_id}.")
            return response.json()

        except requests.RequestException as e:
            logging.error(f"Failed to fetch user info for TikTok user ID {user_id}: {e}")
            return None

    def get_video_details(self, video_id):
        """
        Fetch details about a specific TikTok video.
        
        :param video_id: The unique ID of the TikTok video.
        :return: JSON response containing video details, or None if an error occurs.
        """
        try:
            url = f"{self.BASE_URL}videos/{video_id}/info/"
            response = self.session.get(url, headers=self._get_headers())
            response.raise_for_status()

            logging.info(f"Successfully fetched details for TikTok video ID {video_id}.")
            return response.json()

        except requests.RequestException as e:
            logging.error(f"Failed to fetch details for TikTok video ID {video_id}: {e}")
            return None

    def search_hashtags(self, hashtag):
        """
        Search for TikTok videos by hashtag.
        
        :param hashtag: The hashtag to search for.
        :return: JSON response containing search results, or None if an error occurs.
        """
        try:
            url = f"{self.BASE_URL}discover/hashtags/"
            params = {'query': hashtag}
            response = self.session.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()

            logging.info(f"Successfully fetched videos for hashtag: {hashtag}.")
            return response.json()

        except requests.RequestException as e:
            logging.error(f"Failed to fetch videos for hashtag {hashtag}: {e}")
            return None

    def upload_video(self, video_path, caption):
        """
        Upload a video to TikTok.
        
        :param video_path: Path to the video file to be uploaded.
        :param caption: Caption for the video.
        :return: JSON response containing upload details, or None if an error occurs.
        """
        try:
            url = f"{self.BASE_URL}videos/upload/"
            with open(video_path, 'rb') as video_file:
                files = {'video': video_file}
                data = {'caption': caption}
                response = self.session.post(url, headers=self._get_headers(), data=data, files=files)
                response.raise_for_status()

            logging.info(f"Video uploaded successfully with caption: {caption}.")
            return response.json()

        except FileNotFoundError:
            logging.error(f"Video file not found: {video_path}")
            return None
        except requests.RequestException as e:
            logging.error(f"Failed to upload video to TikTok: {e}")
            return None

    def get_user_videos(self, user_id, max_results=10):
        """
        Fetch a user's TikTok videos.
        
        :param user_id: The unique ID of the TikTok user.
        :param max_results: Maximum number of videos to retrieve (default: 10).
        :return: JSON response containing user's videos, or None if an error occurs.
        """
        try:
            url = f"{self.BASE_URL}users/{user_id}/videos/"
            params = {'limit': max_results}
            response = self.session.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()

            logging.info(f"Successfully fetched {max_results} videos for TikTok user ID {user_id}.")
            return response.json()

        except requests.RequestException as e:
            logging.error(f"Failed to fetch videos for TikTok user ID {user_id}: {e}")
            return None

tiktok_service = TikTokService(access_token="your-access-token")

user_info = tiktok_service.get_user_info(user_id="123456")
print(user_info)

video_details = tiktok_service.get_video_details(video_id="abcdef")
print(video_details)

videos_by_hashtag = tiktok_service.search_hashtags(hashtag="trending")
print(videos_by_hashtag)

response = tiktok_service.upload_video(video_path="path/to/video.mp4", caption="My new TikTok video!")
print(response)

user_videos = tiktok_service.get_user_videos(user_id="123456", max_results=5)
print(user_videos)

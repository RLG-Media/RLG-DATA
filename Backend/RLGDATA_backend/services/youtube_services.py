import requests
import logging


class YouTubeService:
    """
    Service class for interacting with the YouTube Data API.
    """
    BASE_URL = 'https://www.googleapis.com/youtube/v3/'  # YouTube Data API base URL

    def __init__(self, api_key):
        """
        Initialize the YouTubeService with an API key.

        :param api_key: The API key for YouTube Data API.
        """
        self.api_key = api_key
        self.session = requests.Session()

    def _get_common_params(self):
        """
        Generate common parameters for all YouTube API requests.

        :return: Dictionary of common parameters.
        """
        return {'key': self.api_key}

    def search_videos(self, query, max_results=10):
        """
        Search for videos on YouTube using a query.

        :param query: The search query string.
        :param max_results: Maximum number of results to retrieve (default: 10).
        :return: JSON response containing search results, or None if an error occurs.
        """
        try:
            url = f"{self.BASE_URL}search"
            params = {
                'part': 'snippet',
                'q': query,
                'maxResults': max_results,
                'type': 'video'
            }
            params.update(self._get_common_params())
            response = self.session.get(url, params=params)
            response.raise_for_status()

            logging.info(f"Successfully searched YouTube videos for query: '{query}'.")
            return response.json()

        except requests.RequestException as e:
            logging.error(f"Failed to search videos on YouTube for query '{query}': {e}")
            return None

    def get_video_details(self, video_id):
        """
        Get details about a specific YouTube video.

        :param video_id: The ID of the video.
        :return: JSON response containing video details, or None if an error occurs.
        """
        try:
            url = f"{self.BASE_URL}videos"
            params = {
                'part': 'snippet,contentDetails,statistics',
                'id': video_id
            }
            params.update(self._get_common_params())
            response = self.session.get(url, params=params)
            response.raise_for_status()

            logging.info(f"Successfully fetched video details for video ID: {video_id}.")
            return response.json()

        except requests.RequestException as e:
            logging.error(f"Failed to fetch video details from YouTube for video ID '{video_id}': {e}")
            return None

    def get_channel_details(self, channel_id):
        """
        Get details about a specific YouTube channel.

        :param channel_id: The ID of the channel.
        :return: JSON response containing channel details, or None if an error occurs.
        """
        try:
            url = f"{self.BASE_URL}channels"
            params = {
                'part': 'snippet,statistics,brandingSettings',
                'id': channel_id
            }
            params.update(self._get_common_params())
            response = self.session.get(url, params=params)
            response.raise_for_status()

            logging.info(f"Successfully fetched channel details for channel ID: {channel_id}.")
            return response.json()

        except requests.RequestException as e:
            logging.error(f"Failed to fetch channel details from YouTube for channel ID '{channel_id}': {e}")
            return None

    def get_playlist_videos(self, playlist_id, max_results=10):
        """
        Retrieve videos from a specific YouTube playlist.

        :param playlist_id: The ID of the playlist.
        :param max_results: Maximum number of videos to retrieve (default: 10).
        :return: JSON response containing playlist videos, or None if an error occurs.
        """
        try:
            url = f"{self.BASE_URL}playlistItems"
            params = {
                'part': 'snippet',
                'playlistId': playlist_id,
                'maxResults': max_results
            }
            params.update(self._get_common_params())
            response = self.session.get(url, params=params)
            response.raise_for_status()

            logging.info(f"Successfully fetched videos from playlist ID: {playlist_id}.")
            return response.json()

        except requests.RequestException as e:
            logging.error(f"Failed to fetch videos from playlist ID '{playlist_id}': {e}")
            return None

    def get_trending_videos(self, region_code='US', max_results=10):
        """
        Retrieve trending videos on YouTube for a specific region.

        :param region_code: The region code (default: 'US').
        :param max_results: Maximum number of videos to retrieve (default: 10).
        :return: JSON response containing trending videos, or None if an error occurs.
        """
        try:
            url = f"{self.BASE_URL}videos"
            params = {
                'part': 'snippet,statistics',
                'chart': 'mostPopular',
                'regionCode': region_code,
                'maxResults': max_results
            }
            params.update(self._get_common_params())
            response = self.session.get(url, params=params)
            response.raise_for_status()

            logging.info(f"Successfully fetched trending videos for region: {region_code}.")
            return response.json()

        except requests.RequestException as e:
            logging.error(f"Failed to fetch trending videos for region '{region_code}': {e}")
            return None

youtube_service = YouTubeService(api_key="your-youtube-api-key")

results = youtube_service.search_videos(query="Python tutorials")
print(results)

video_details = youtube_service.get_video_details(video_id="abcd1234")
print(video_details)

channel_details = youtube_service.get_channel_details(channel_id="UC123456789")
print(channel_details)

playlist_videos = youtube_service.get_playlist_videos(playlist_id="PL123456789", max_results=5)
print(playlist_videos)

trending_videos = youtube_service.get_trending_videos(region_code="US", max_results=10)
print(trending_videos)

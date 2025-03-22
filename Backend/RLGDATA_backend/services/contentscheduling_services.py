import requests
from flask import current_app
from shared.utils import log_error, log_info, validate_api_response  # Shared utilities
from shared.config import CONTENT_SCHEDULING_API_URL, CONTENT_SCHEDULING_API_KEY  # Shared configurations

class ContentSchedulingService:
    """
    Service class for managing content scheduling.
    Handles scheduling, retrieving, and updating scheduled posts efficiently.
    """

    def __init__(self):
        if not CONTENT_SCHEDULING_API_KEY or not CONTENT_SCHEDULING_API_URL:
            raise ValueError("API key and base URL must be provided in the configuration.")
        self.api_key = CONTENT_SCHEDULING_API_KEY
        self.base_url = CONTENT_SCHEDULING_API_URL

    def schedule_post(self, post_data):
        url = f"{self.base_url}/schedule"
        headers = self._get_headers()

        try:
            response = requests.post(url, headers=headers, json=post_data, timeout=10)
            if response.status_code == 201:
                result = response.json()
                log_info(f"Post scheduled successfully: {post_data.get('title', 'No Title')}")
                return result
            else:
                log_error(f"Failed to schedule post: {response.text}")
                return {'error': 'Unable to schedule post'}
        except requests.RequestException as e:
            log_error(f"Error scheduling post: {e}")
            return {'error': 'Service temporarily unavailable'}

    def get_scheduled_posts(self, start_date=None, end_date=None, platforms=None):
        url = f"{self.base_url}/scheduled"
        headers = self._get_headers()
        params = {
            'start_date': start_date,
            'end_date': end_date,
            'platforms': ','.join(platforms) if platforms else None
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if validate_api_response(response):
                posts = response.json()
                log_info(f"Retrieved scheduled posts with filters: {params}")
                return posts
            else:
                log_error(f"Failed to fetch scheduled posts: {response.text}")
                return {'error': 'Unable to fetch scheduled posts'}
        except requests.RequestException as e:
            log_error(f"Error fetching scheduled posts: {e}")
            return {'error': 'Service temporarily unavailable'}

    def update_scheduled_post(self, post_id, update_data):
        url = f"{self.base_url}/schedule/{post_id}"
        headers = self._get_headers()

        try:
            response = requests.put(url, headers=headers, json=update_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                log_info(f"Post updated successfully: ID {post_id}")
                return result
            else:
                log_error(f"Failed to update scheduled post: {response.text}")
                return {'error': 'Unable to update post'}
        except requests.RequestException as e:
            log_error(f"Error updating scheduled post: {e}")
            return {'error': 'Service temporarily unavailable'}

    def delete_scheduled_post(self, post_id):
        url = f"{self.base_url}/schedule/{post_id}"
        headers = self._get_headers()

        try:
            response = requests.delete(url, headers=headers, timeout=10)
            if response.status_code == 204:
                log_info(f"Post deleted successfully: ID {post_id}")
                return {'message': 'Post deleted successfully'}
            else:
                log_error(f"Failed to delete scheduled post: {response.text}")
                return {'error': 'Unable to delete post'}
        except requests.RequestException as e:
            log_error(f"Error deleting scheduled post: {e}")
            return {'error': 'Service temporarily unavailable'}

    def _get_headers(self):
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

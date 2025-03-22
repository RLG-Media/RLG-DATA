import requests
from flask import current_app
from shared.utils import log_error, log_info, validate_api_response  # Shared utilities
from shared.config import FACEBOOK_GRAPH_API_BASE_URL  # Shared configuration

class FacebookService:
    """
    Service class for interacting with the Facebook Graph API.
    Provides methods for fetching page insights, posts, and other related data.
    """

    def __init__(self, access_token):
        """
        Initialize the FacebookService instance with the required access token.
        
        :param access_token: Access token for authenticating API requests.
        """
        self.access_token = access_token
        self.base_url = FACEBOOK_GRAPH_API_BASE_URL
        self.headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

    def get_page_insights(self, page_id, metrics=None):
        """
        Fetch insights for a specific Facebook page.
        
        :param page_id: The Facebook Page ID.
        :param metrics: (Optional) List of metrics to retrieve insights for. If None, fetches default metrics.
        :return: Insights data as JSON or an error message.
        """
        try:
            url = f"{self.base_url}/{page_id}/insights"
            params = {'metric': ','.join(metrics)} if metrics else {}
            params['access_token'] = self.access_token

            response = requests.get(url, headers=self.headers, params=params)
            if validate_api_response(response):
                log_info(f"Successfully fetched insights for page {page_id}")
                return response.json()
            else:
                log_error(f"Failed to fetch insights for page {page_id}: {response.text}")
                return {'error': 'Failed to fetch page insights'}
        except requests.RequestException as e:
            log_error(f"Error fetching Facebook page insights: {e}")
            return {'error': 'Service temporarily unavailable'}

    def get_page_posts(self, page_id, limit=10):
        """
        Fetch recent posts from a specific Facebook page.
        
        :param page_id: The Facebook Page ID.
        :param limit: Number of posts to fetch (default is 10).
        :return: Posts data as JSON or an error message.
        """
        try:
            url = f"{self.base_url}/{page_id}/posts"
            params = {
                'limit': limit,
                'access_token': self.access_token
            }

            response = requests.get(url, headers=self.headers, params=params)
            if validate_api_response(response):
                log_info(f"Successfully fetched posts for page {page_id}")
                return response.json()
            else:
                log_error(f"Failed to fetch posts for page {page_id}: {response.text}")
                return {'error': 'Failed to fetch page posts'}
        except requests.RequestException as e:
            log_error(f"Error fetching Facebook posts: {e}")
            return {'error': 'Service temporarily unavailable'}

    def post_to_page(self, page_id, message, link=None):
        """
        Create a new post on a specific Facebook page.
        
        :param page_id: The Facebook Page ID.
        :param message: The message content of the post.
        :param link: (Optional) A link to include in the post.
        :return: Response data as JSON or an error message.
        """
        try:
            url = f"{self.base_url}/{page_id}/feed"
            data = {
                'message': message,
                'access_token': self.access_token
            }
            if link:
                data['link'] = link

            response = requests.post(url, headers=self.headers, data=data)
            if validate_api_response(response):
                log_info(f"Successfully created a post on page {page_id}")
                return response.json()
            else:
                log_error(f"Failed to create a post on page {page_id}: {response.text}")
                return {'error': 'Failed to create page post'}
        except requests.RequestException as e:
            log_error(f"Error posting to Facebook page: {e}")
            return {'error': 'Service temporarily unavailable'}

    def get_page_followers(self, page_id):
        """
        Fetch the total number of followers for a specific Facebook page.
        
        :param page_id: The Facebook Page ID.
        :return: Follower count as JSON or an error message.
        """
        try:
            url = f"{self.base_url}/{page_id}/followers_count"
            params = {'access_token': self.access_token}

            response = requests.get(url, headers=self.headers, params=params)
            if validate_api_response(response):
                log_info(f"Successfully fetched followers count for page {page_id}")
                return response.json()
            else:
                log_error(f"Failed to fetch followers count for page {page_id}: {response.text}")
                return {'error': 'Failed to fetch followers count'}
        except requests.RequestException as e:
            log_error(f"Error fetching Facebook page followers: {e}")
            return {'error': 'Service temporarily unavailable'}

facebook_service = FacebookService(access_token="YOUR_ACCESS_TOKEN")
insights = facebook_service.get_page_insights(page_id="123456789", metrics=["page_views", "page_likes"])
print(insights)

posts = facebook_service.get_page_posts(page_id="123456789", limit=5)
print(posts)

response = facebook_service.post_to_page(page_id="123456789", message="Check out our latest updates!", link="https://example.com")
print(response)

followers = facebook_service.get_page_followers(page_id="123456789")
print(followers)

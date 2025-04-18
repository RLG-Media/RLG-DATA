# api_integration.py

import logging
import requests
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class APIIntegration:
    def __init__(self, platform, auth_data):
        self.platform = platform
        self.auth_data = auth_data
        self.api_base_url = f"https://api.{self.platform}.com/v1"

    def send_request(self, endpoint, method='GET', params=None, data=None, headers=None):
        """Send an API request to the platform."""
        url = f"{self.api_base_url}/{endpoint}"
        headers = headers if headers else {"Authorization": f"Bearer {self.auth_data['access_token']}"}

        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, data=json.dumps(data))
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, data=json.dumps(data))
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers)

            response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)
            response_data = response.json()
            logger.info(f"API request to {self.platform} successful. Endpoint: {endpoint}, Method: {method}")
            return response_data

        except requests.exceptions.RequestException as e:
            logger.error(f"API request to {self.platform} failed. Endpoint: {endpoint}, Method: {method}, Error: {e}")
            raise

    def get_user_data(self, user_id):
        """Retrieve user data from the API."""
        endpoint = f"users/{user_id}"
        return self.send_request(endpoint)

    def post_content(self, content_data):
        """Post new content to the API."""
        endpoint = "content"
        return self.send_request(endpoint, method='POST', data=content_data)

    def get_recent_posts(self, user_id):
        """Retrieve recent posts from the API."""
        endpoint = f"users/{user_id}/posts"
        return self.send_request(endpoint)

    def schedule_post(self, schedule_data):
        """Schedule a post through the API."""
        endpoint = "posts/schedule"
        return self.send_request(endpoint, method='POST', data=schedule_data)

    def get_comments(self, post_id):
        """Retrieve comments from a specific post."""
        endpoint = f"posts/{post_id}/comments"
        return self.send_request(endpoint)

    def like_post(self, post_id):
        """Like a specific post."""
        endpoint = f"posts/{post_id}/like"
        return self.send_request(endpoint, method='POST')

    def get_engagement_metrics(self, user_id):
        """Retrieve engagement metrics for a user."""
        endpoint = f"users/{user_id}/engagement"
        return self.send_request(endpoint)

    def get_platform_insights(self):
        """Retrieve platform-wide insights or analytics."""
        endpoint = "insights"
        return self.send_request(endpoint)
    
    # Additional helper methods for more structured data handling or formatting
    def _format_request_data(self, data):
        """Format request data to be JSON-compliant."""
        return json.dumps(data) if isinstance(data, dict) else data

# Additional Recommendations for APIIntegration:
# 1. Handle rate limiting by implementing exponential backoff or retry mechanisms.
# 2. Secure all API calls using HTTPS and enforce strict SSL checks.
# 3. Include pagination handling for large datasets retrieved from APIs.
# 4. Implement caching for frequently accessed data to reduce redundant API calls.
# 5. Provide detailed error logging with response codes and error messages for better troubleshooting.
# 6. Add authentication token validation before each API call to ensure its validity.
# 7. Incorporate proper handling of API response errors (400, 401, 403, etc.).
# 8. Provide detailed data parsing and validation to ensure accurate data integration.
# 9. Include robust handling for different API response formats (JSON, XML, etc.).
# 10. Include a timeout parameter to control the duration of API calls, ensuring resilience in network delays.

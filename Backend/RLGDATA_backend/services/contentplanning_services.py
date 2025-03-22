import requests
from flask import current_app
from shared.utils import log_error, log_info, validate_api_response  # Shared utilities
from shared.config import CONTENT_PLANNING_API_URL, CONTENT_PLANNING_API_KEY  # Shared configurations

class ContentPlanningService:
    """
    Service class for content planning and scheduling.
    Provides functionality to generate content ideas and schedule posts effectively.
    """

    def __init__(self):
        if not CONTENT_PLANNING_API_KEY or not CONTENT_PLANNING_API_URL:
            raise ValueError("API key and base URL must be provided in the configuration.")
        self.api_key = CONTENT_PLANNING_API_KEY
        self.base_url = CONTENT_PLANNING_API_URL

    def generate_content_ideas(self, topic, audience=None, keywords=None):
        url = f"{self.base_url}/content/ideas"
        headers = self._get_headers()
        payload = {
            'topic': topic,
            'audience': audience,
            'keywords': keywords
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if validate_api_response(response):
                ideas = response.json()
                log_info(f"Generated content ideas for topic: {topic}")
                return ideas
            else:
                log_error(f"Failed to generate content ideas for topic: {topic}: {response.text}")
                return {'error': 'Unable to generate content ideas'}
        except requests.RequestException as e:
            log_error(f"Error generating content ideas: {e}")
            return {'error': 'Service temporarily unavailable'}

    def schedule_content(self, content_data):
        url = f"{self.base_url}/content/schedule"
        headers = self._get_headers()

        try:
            response = requests.post(url, headers=headers, json=content_data, timeout=10)
            if response.status_code == 201:
                result = response.json()
                log_info(f"Content scheduled successfully: {content_data.get('title', 'No Title')}")
                return result
            else:
                log_error(f"Failed to schedule content: {response.text}")
                return {'error': 'Unable to schedule content'}
        except requests.RequestException as e:
            log_error(f"Error scheduling content: {e}")
            return {'error': 'Service temporarily unavailable'}

    def fetch_scheduled_content(self, start_date=None, end_date=None, status=None):
        url = f"{self.base_url}/content/scheduled"
        headers = self._get_headers()
        params = {
            'start_date': start_date,
            'end_date': end_date,
            'status': status
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if validate_api_response(response):
                content_list = response.json()
                log_info(f"Fetched scheduled content with filters: {params}")
                return content_list
            else:
                log_error(f"Failed to fetch scheduled content: {response.text}")
                return {'error': 'Unable to fetch scheduled content'}
        except requests.RequestException as e:
            log_error(f"Error fetching scheduled content: {e}")
            return {'error': 'Service temporarily unavailable'}

    def _get_headers(self):
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

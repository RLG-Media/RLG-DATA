import requests
from typing import Dict, Any, Optional, List
from flask import current_app
from shared.utils import log_error, log_info, validate_api_response  # Shared utilities
from shared.config import CRISIS_MANAGEMENT_API_URL, CRISIS_MANAGEMENT_API_KEY  # Shared configurations

class CrisisManagementService:
    """
    Service class for managing crisis-related content and responses.
    Provides tools for scheduling critical posts, escalating issues,
    and monitoring crisis management tasks.
    """

    def __init__(self) -> None:
        """
        Initializes the CrisisManagementService with API configuration.
        Raises:
            ValueError: If the API key or base URL is missing.
        """
        if not CRISIS_MANAGEMENT_API_KEY or not CRISIS_MANAGEMENT_API_URL:
            raise ValueError("API key and base URL must be provided in the configuration.")
        self.api_key: str = CRISIS_MANAGEMENT_API_KEY
        self.base_url: str = CRISIS_MANAGEMENT_API_URL
        log_info("CrisisManagementService initialized.")

    def schedule_crisis_post(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Schedule a crisis post using the external crisis management API.
        
        Args:
            post_data (Dict[str, Any]): A dictionary containing the post details.
                Example: {"title": "Urgent Update", "content": "..."}

        Returns:
            Dict[str, Any]: The JSON response from the API if successful, or an error dictionary.
        """
        url = f"{self.base_url}/schedule"
        headers = self._get_headers()

        try:
            response = requests.post(url, headers=headers, json=post_data, timeout=10)
            if validate_api_response(response):
                log_info(f"Crisis post scheduled successfully: {post_data.get('title', 'No Title')}")
                return response.json()
            else:
                log_error(f"Failed to schedule crisis post: {response.text}")
                return {'error': 'Unable to schedule crisis post'}
        except requests.RequestException as e:
            log_error(f"Error scheduling crisis post: {e}")
            return {'error': 'Service temporarily unavailable'}

    def get_scheduled_crisis_posts(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieve scheduled crisis posts, optionally filtered by provided parameters.
        
        Args:
            filters (Optional[Dict[str, Any]]): A dictionary of filters to apply (e.g., status, date range).

        Returns:
            Dict[str, Any]: The JSON response containing scheduled crisis posts or an error message.
        """
        url = f"{self.base_url}/scheduled"
        headers = self._get_headers()
        params = filters if filters else {}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if validate_api_response(response):
                log_info(f"Fetched scheduled crisis posts with filters: {params}")
                return response.json()
            else:
                log_error(f"Failed to fetch scheduled crisis posts: {response.text}")
                return {'error': 'Unable to fetch scheduled crisis posts'}
        except requests.RequestException as e:
            log_error(f"Error fetching scheduled crisis posts: {e}")
            return {'error': 'Service temporarily unavailable'}

    def escalate_issue(self, issue_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Escalate a crisis issue using the external API.
        
        Args:
            issue_details (Dict[str, Any]): A dictionary containing issue details.
                Example: {"description": "System outage", "severity": "high"}

        Returns:
            Dict[str, Any]: The JSON response from the API if successful, or an error dictionary.
        """
        url = f"{self.base_url}/escalate"
        headers = self._get_headers()

        try:
            response = requests.post(url, headers=headers, json=issue_details, timeout=10)
            if validate_api_response(response):
                log_info(f"Issue escalated successfully: {issue_details.get('description', 'No Description')}")
                return response.json()
            else:
                log_error(f"Failed to escalate issue: {response.text}")
                return {'error': 'Unable to escalate issue'}
        except requests.RequestException as e:
            log_error(f"Error escalating issue: {e}")
            return {'error': 'Service temporarily unavailable'}

    def monitor_crisis_status(self, crisis_id: str) -> Dict[str, Any]:
        """
        Monitor the status of a crisis using its unique ID.
        
        Args:
            crisis_id (str): The unique identifier for the crisis.

        Returns:
            Dict[str, Any]: The JSON response containing the crisis status or an error message.
        """
        url = f"{self.base_url}/status/{crisis_id}"
        headers = self._get_headers()

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if validate_api_response(response):
                log_info(f"Retrieved status for crisis ID: {crisis_id}")
                return response.json()
            else:
                log_error(f"Failed to retrieve crisis status for ID {crisis_id}: {response.text}")
                return {'error': 'Unable to retrieve crisis status'}
        except requests.RequestException as e:
            log_error(f"Error retrieving crisis status: {e}")
            return {'error': 'Service temporarily unavailable'}

    def _get_headers(self) -> Dict[str, str]:
        """
        Constructs the HTTP headers required for API calls.
        
        Returns:
            Dict[str, str]: A dictionary with Authorization and Content-Type headers.
        """
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

# -------------------------------
# Additional Recommendations:
# -------------------------------
# 1. Consider adding retry logic for transient network errors (e.g., using requests.adapters.Retry).
# 2. Extend methods to support region, country, city, or town-specific parameters if needed.
# 3. Integrate caching for frequently requested data to improve performance.
# 4. Ensure that sensitive configuration values are loaded securely from environment variables or a secrets manager.
# 5. Write unit tests for each method to validate API responses and error handling.

# -------------------------------
# Example Usage (for testing purposes)
# -------------------------------
if __name__ == "__main__":
    service = CrisisManagementService()

    # Example: Schedule a crisis post
    post_data = {
        "title": "Emergency Update",
        "content": "A critical incident has occurred. Please stand by for further updates."
    }
    scheduled_post = service.schedule_crisis_post(post_data)
    print("Scheduled Crisis Post:", scheduled_post)

    # Example: Retrieve scheduled crisis posts with optional filters
    scheduled_posts = service.get_scheduled_crisis_posts(filters={"status": "pending"})
    print("Scheduled Crisis Posts:", scheduled_posts)

    # Example: Escalate an issue
    issue_details = {"description": "Major outage affecting multiple regions", "severity": "high"}
    escalation_result = service.escalate_issue(issue_details)
    print("Escalation Result:", escalation_result)

    # Example: Monitor crisis status by crisis ID
    crisis_status = service.monitor_crisis_status("crisis123")
    print("Crisis Status:", crisis_status)

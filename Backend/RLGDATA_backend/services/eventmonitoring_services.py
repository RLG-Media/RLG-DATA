import requests
from typing import Dict, Any, Optional, List
from flask import current_app
from shared.utils import log_error, log_info, validate_api_response  # Shared utilities
from shared.config import EVENT_MONITORING_API_URL, EVENT_MONITORING_API_KEY  # Shared configurations

class EventMonitoringService:
    """
    Service class for monitoring events related to brands, topics, and industries.
    Provides functionalities for fetching events, retrieving event details, and monitoring event trends.
    This service is designed for both RLG Data and RLG Fans, and can be extended to incorporate
    region, country, city, or town-specific parameters if needed.
    """

    def __init__(self) -> None:
        """
        Initializes the EventMonitoringService with the necessary API configuration.
        Raises:
            ValueError: If the API key or base URL is missing.
        """
        if not EVENT_MONITORING_API_KEY or not EVENT_MONITORING_API_URL:
            raise ValueError("API key and base URL must be provided in the configuration.")
        self.api_key: str = EVENT_MONITORING_API_KEY
        self.base_url: str = EVENT_MONITORING_API_URL
        log_info("EventMonitoringService initialized with base URL: %s", self.base_url)

    def fetch_events(self, keyword: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Fetch events based on a given keyword and optional filters.
        
        Args:
            keyword (str): Keyword to search for events.
            filters (Optional[Dict[str, Any]]): Additional filtering parameters (e.g., location, date_range).
        
        Returns:
            Dict[str, Any]: JSON response from the API containing events data, or an error message.
        """
        url = f"{self.base_url}/events"
        headers = self._get_headers()
        params: Dict[str, Any] = {'keyword': keyword}
        if filters:
            params.update(filters)

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if validate_api_response(response):
                log_info("Successfully fetched events for keyword: %s", keyword)
                return response.json()
            else:
                log_error("Failed to fetch events: %s", response.text)
                return {'error': 'Unable to fetch events'}
        except requests.RequestException as e:
            log_error("Error fetching events: %s", e)
            return {'error': 'Service temporarily unavailable'}

    def get_event_details(self, event_id: str) -> Dict[str, Any]:
        """
        Retrieve detailed information about a specific event.
        
        Args:
            event_id (str): The unique identifier of the event.
        
        Returns:
            Dict[str, Any]: JSON response containing event details, or an error message.
        """
        url = f"{self.base_url}/events/{event_id}"
        headers = self._get_headers()

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if validate_api_response(response):
                log_info("Successfully fetched details for event ID: %s", event_id)
                return response.json()
            else:
                log_error("Failed to fetch event details: %s", response.text)
                return {'error': 'Unable to fetch event details'}
        except requests.RequestException as e:
            log_error("Error fetching event details: %s", e)
            return {'error': 'Service temporarily unavailable'}

    def monitor_event_trends(self, keywords: List[str]) -> Dict[str, Any]:
        """
        Monitor trends for a list of keywords by posting them to the external API.
        
        Args:
            keywords (List[str]): List of keywords to monitor.
        
        Returns:
            Dict[str, Any]: JSON response from the API containing trend data, or an error message.
        """
        url = f"{self.base_url}/trends"
        headers = self._get_headers()
        data = {'keywords': keywords}

        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            if validate_api_response(response):
                log_info("Successfully monitored trends for keywords: %s", keywords)
                return response.json()
            else:
                log_error("Failed to monitor trends: %s", response.text)
                return {'error': 'Unable to monitor trends'}
        except requests.RequestException as e:
            log_error("Error monitoring trends: %s", e)
            return {'error': 'Service temporarily unavailable'}

    def _get_headers(self) -> Dict[str, str]:
        """
        Constructs the HTTP headers for API calls.
        
        Returns:
            Dict[str, str]: A dictionary with the Authorization and Content-Type headers.
        """
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

# -------------------------------
# Additional Recommendations:
# -------------------------------
# 1. Consider adding retry logic (e.g., using requests.adapters.Retry) for transient network errors.
# 2. Extend filtering options to include region, country, city, or town if such metadata is available.
# 3. Implement caching for frequently requested events to reduce API calls.
# 4. Ensure sensitive configuration values (e.g., API keys) are securely stored via environment variables.
# 5. Write comprehensive unit tests to validate each method under various scenarios.

# -------------------------------
# Example Usage (for testing purposes)
# -------------------------------
if __name__ == "__main__":
    event_service = EventMonitoringService()

    # Example: Fetch events with filters
    events = event_service.fetch_events(
        "AI Technology", 
        filters={"location": "USA", "date_range": "2025-01-01 to 2025-01-31"}
    )
    print("Events:", events)

    # Example: Get event details by event ID
    details = event_service.get_event_details("EVENT12345")
    print("Event Details:", details)

    # Example: Monitor trends for a set of keywords
    trends = event_service.monitor_event_trends(["AI", "Data Science", "Cloud Computing"])
    print("Event Trends:", trends)

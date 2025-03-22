import requests
from flask import current_app
from shared.utils import log_error, log_info, validate_api_response  # Shared utilities
from shared.config import BRAND_HEALTH_API_URL, BRAND_HEALTH_API_KEY  # Shared configurations
from typing import Dict, Any, Optional, List

class BrandHealthService:
    """
    Service class for monitoring brand health metrics.
    
    This service interacts with external APIs to analyze sentiment, fetch brand mentions,
    and monitor brand trends, thereby generating actionable insights.
    """

    def __init__(self) -> None:
        if not BRAND_HEALTH_API_KEY or not BRAND_HEALTH_API_URL:
            raise ValueError("API key and base URL must be provided in the configuration.")
        self.api_key: str = BRAND_HEALTH_API_KEY
        self.base_url: str = BRAND_HEALTH_API_URL
        log_info("BrandHealthService initialized with base URL and API key.")

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze the sentiment of the provided text using an external API.
        
        Args:
            text (str): The text to analyze.
        
        Returns:
            Dict[str, Any]: The sentiment analysis result or an error message.
        """
        url = f"{self.base_url}/sentiment"
        headers = self._get_headers()
        payload = {'text': text}

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if validate_api_response(response):
                result = response.json()
                log_info(f"Sentiment analysis successful for text: {text[:50]}...")
                return result
            else:
                log_error(f"Sentiment analysis failed: {response.text}")
                return {'error': 'Sentiment analysis failed'}
        except requests.RequestException as e:
            log_error(f"Error analyzing sentiment: {e}")
            return {'error': 'Service temporarily unavailable'}

    def fetch_brand_mentions(self, brand_name: str, sources: Optional[List[str]] = None, limit: int = 100) -> Dict[str, Any]:
        """
        Fetch brand mentions for the specified brand.
        
        Args:
            brand_name (str): The name of the brand.
            sources (Optional[List[str]]): List of sources to filter by (if any).
            limit (int): Maximum number of mentions to retrieve.
        
        Returns:
            Dict[str, Any]: The brand mentions data or an error message.
        """
        url = f"{self.base_url}/mentions"
        headers = self._get_headers()
        params = {
            'brand_name': brand_name,
            'sources': ','.join(sources) if sources else None,
            'limit': limit
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if validate_api_response(response):
                result = response.json()
                log_info(f"Successfully fetched mentions for brand: {brand_name}")
                return result
            else:
                log_error(f"Failed to fetch mentions for {brand_name}: {response.text}")
                return {'error': 'Unable to fetch brand mentions'}
        except requests.RequestException as e:
            log_error(f"Error fetching brand mentions: {e}")
            return {'error': 'Service temporarily unavailable'}

    def monitor_brand_trends(self, brand_name: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Monitor brand trends over a specified date range.
        
        Args:
            brand_name (str): The brand name to monitor.
            start_date (str): Start date (ISO format recommended).
            end_date (str): End date (ISO format recommended).
        
        Returns:
            Dict[str, Any]: The trend analysis data or an error message.
        """
        url = f"{self.base_url}/trends"
        headers = self._get_headers()
        payload = {
            'brand_name': brand_name,
            'start_date': start_date,
            'end_date': end_date
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if validate_api_response(response):
                result = response.json()
                log_info(f"Successfully monitored trends for brand: {brand_name}")
                return result
            else:
                log_error(f"Failed to monitor trends for {brand_name}: {response.text}")
                return {'error': 'Unable to monitor brand trends'}
        except requests.RequestException as e:
            log_error(f"Error monitoring brand trends: {e}")
            return {'error': 'Service temporarily unavailable'}

    def _get_headers(self) -> Dict[str, str]:
        """
        Generate request headers for the API calls, including the Authorization header.
        
        Returns:
            Dict[str, str]: A dictionary of HTTP headers.
        """
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

# -------------------------------
# Additional Recommendations:
# -------------------------------
# 1. Enhance error handling by integrating retry logic for transient network issues.
# 2. If regional adjustments are needed, extend methods to accept region, country, city, or town parameters.
# 3. Secure API keys and endpoints by loading them from environment variables or a secrets manager.
# 4. Integrate caching for frequently requested data to reduce API load.
# 5. Consider adding unit tests in the tests/ folder to validate API responses and error handling.

# -------------------------------
# Example Usage (for testing purposes)
# -------------------------------
if __name__ == "__main__":
    service = BrandHealthService()
    
    # Example sentiment analysis
    sample_text = "Our brand is performing exceptionally well in the current market!"
    sentiment_result = service.analyze_sentiment(sample_text)
    print("Sentiment Analysis Result:", sentiment_result)
    
    # Example fetching brand mentions
    mentions = service.fetch_brand_mentions("RLG", sources=["twitter", "facebook"], limit=50)
    print("Brand Mentions:", mentions)
    
    # Example monitoring brand trends
    trends = service.monitor_brand_trends("RLG", "2025-01-01", "2025-01-31")
    print("Brand Trends:", trends)

import logging
from typing import Dict, Any, List, Optional
import requests
from datetime import datetime
from shared.config import SEO_MONITORING_API_URL, SEO_MONITORING_API_KEY  # Ensure these are defined in your shared configuration
from shared.utils import log_info, log_error, validate_api_response  # Shared logging and response validation utilities

# Configure logging if not already configured by your application.
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class SEOMonitoringService:
    """
    Service class for continuously monitoring SEO performance metrics.

    This service fetches data such as keyword rankings, visibility, and trend analysis from an external SEO monitoring API.
    It supports optional filtering by region, country, city, and town to ensure localized accuracy.
    Designed for both RLG Data and RLG Fans, it can be extended or integrated with other SEO data sources.
    """

    def __init__(self) -> None:
        """
        Initialize the SEOMonitoringService using configuration values from shared settings.

        Raises:
            ValueError: If the SEO monitoring API URL or API key is missing.
        """
        if not SEO_MONITORING_API_URL or not SEO_MONITORING_API_KEY:
            raise ValueError("SEO monitoring API URL and API key must be provided in the configuration.")
        self.api_url: str = SEO_MONITORING_API_URL
        self.api_key: str = SEO_MONITORING_API_KEY
        log_info("SEOMonitoringService initialized successfully with API URL: %s", self.api_url)

    def _get_headers(self) -> Dict[str, str]:
        """
        Construct HTTP headers for requests to the SEO monitoring API.

        Returns:
            Dict[str, str]: A dictionary containing the Authorization and Content-Type headers.
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def get_keyword_ranking(
        self, 
        keyword: str, 
        region: Optional[str] = None, 
        country: Optional[str] = None,
        city: Optional[str] = None, 
        town: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve the ranking and related SEO metrics for a given keyword.

        Optional geographic filters can be applied to obtain localized results.

        Args:
            keyword (str): The keyword to check.
            region (Optional[str]): The region to filter by.
            country (Optional[str]): The country to filter by.
            city (Optional[str]): The city to filter by.
            town (Optional[str]): The town to filter by.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing ranking information and metrics,
                                      or None if an error occurs.
        """
        endpoint = f"{self.api_url}/keyword-ranking"
        params = {"keyword": keyword}
        if region:
            params["region"] = region
        if country:
            params["country"] = country
        if city:
            params["city"] = city
        if town:
            params["town"] = town

        try:
            response = requests.get(endpoint, headers=self._get_headers(), params=params, timeout=10)
            response.raise_for_status()
            if validate_api_response(response):
                log_info("Successfully fetched ranking for keyword '%s' with filters: %s", keyword, params)
                return response.json()
            else:
                log_error("Invalid response received for keyword ranking.")
                return None
        except requests.RequestException as e:
            log_error("Error fetching keyword ranking for '%s': %s", keyword, e)
            return None

    def monitor_seo_trends(self, keywords: List[str], timeframe: str = "today 12-m") -> Optional[Dict[str, Any]]:
        """
        Monitor SEO trends for a list of keywords over a specified timeframe.

        Args:
            keywords (List[str]): A list of keywords to monitor.
            timeframe (str): The timeframe for the trend analysis (e.g., 'today 12-m').

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing trend analysis data or None if an error occurs.
        """
        endpoint = f"{self.api_url}/seo-trends"
        payload = {
            "keywords": keywords,
            "timeframe": timeframe,
            "timestamp": datetime.utcnow().isoformat()
        }
        try:
            response = requests.post(endpoint, headers=self._get_headers(), json=payload, timeout=10)
            response.raise_for_status()
            if validate_api_response(response):
                log_info("Successfully monitored SEO trends for keywords: %s", keywords)
                return response.json()
            else:
                log_error("Invalid response received for SEO trends monitoring.")
                return None
        except requests.RequestException as e:
            log_error("Error monitoring SEO trends for keywords %s: %s", keywords, e)
            return None

    def get_site_visibility(self, site_url: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve overall SEO visibility metrics for a specific site.

        Args:
            site_url (str): The website URL to check.

        Returns:
            Optional[Dict[str, Any]]: A dictionary with visibility metrics or None if an error occurs.
        """
        endpoint = f"{self.api_url}/site-visibility"
        params = {"site_url": site_url}
        try:
            response = requests.get(endpoint, headers=self._get_headers(), params=params, timeout=10)
            response.raise_for_status()
            if validate_api_response(response):
                log_info("Successfully fetched SEO visibility for site: %s", site_url)
                return response.json()
            else:
                log_error("Invalid response received for site visibility.")
                return None
        except requests.RequestException as e:
            log_error("Error fetching SEO visibility for site %s: %s", site_url, e)
            return None


# -------------------------------
# Example Usage (for testing purposes)
# -------------------------------
if __name__ == "__main__":
    # Initialize the SEOMonitoringService.
    seo_monitor = SEOMonitoringService()

    # Example: Get keyword ranking with optional geographic filters.
    ranking_data = seo_monitor.get_keyword_ranking(
        keyword="machine learning",
        region="Europe",
        country="Germany",
        city="Berlin"
    )
    if ranking_data:
        print("Keyword Ranking Data:")
        print(ranking_data)
    else:
        print("Failed to fetch keyword ranking data.")

    # Example: Monitor SEO trends for multiple keywords.
    trends_data = seo_monitor.monitor_seo_trends(keywords=["AI", "blockchain", "data science"])
    if trends_data:
        print("SEO Trends Data:")
        print(trends_data)
    else:
        print("Failed to monitor SEO trends.")

    # Example: Get site visibility metrics.
    visibility_data = seo_monitor.get_site_visibility(site_url="https://example.com")
    if visibility_data:
        print("Site Visibility Data:")
        print(visibility_data)
    else:
        print("Failed to fetch site visibility data.")

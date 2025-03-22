from google.oauth2 import service_account
from googleapiclient.discovery import build
import logging
from typing import Dict, List, Any, Optional
from flask import current_app
from shared.utils import log_error, log_info, validate_api_response  # Shared utilities for logging and response validation
from shared.config import GOOGLE_SEARCH_CONSOLE_CREDENTIALS, GOOGLE_SEARCH_CONSOLE_SITE_URL
# (Ensure you have defined GOOGLE_SEARCH_CONSOLE_CREDENTIALS and, optionally, default site URL in your config)

# Configure logging (if not already configured globally)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class GoogleSearchConsoleService:
    """
    Service class for interacting with Google Search Console to fetch search analytics data,
    coverage data, and sitemap data. This service is designed for both RLG Data and RLG Fans
    and can be extended with additional filtering (e.g., region, country, city, town) if needed.
    """

    def __init__(self, credentials_json: str = GOOGLE_SEARCH_CONSOLE_CREDENTIALS) -> None:
        """
        Initialize the service with a Google Cloud Service Account JSON file for authentication.
        
        Args:
            credentials_json (str): Path to the service account JSON file.
            
        Raises:
            ValueError: If credentials are missing or invalid.
        """
        try:
            self.credentials = service_account.Credentials.from_service_account_file(credentials_json)
            # Build the Search Console API client. Adjust API version if needed.
            self.search_console = build('searchconsole', 'v1', credentials=self.credentials)
            log_info("Google Search Console Service initialized successfully.")
        except Exception as e:
            log_error(f"Error initializing Google Search Console Service: {e}")
            raise

    def get_search_analytics(self, site_url: str, start_date: str, end_date: str, dimensions: List[str], row_limit: int = 10) -> Optional[Dict[str, Any]]:
        """
        Fetch search analytics data from Google Search Console.
        
        Args:
            site_url (str): The URL of the site (e.g., 'https://yourwebsite.com').
            start_date (str): The start date for the data (ISO format, e.g., '2023-01-01').
            end_date (str): The end date for the data (ISO format, e.g., '2023-12-31').
            dimensions (List[str]): Dimensions to include in the report (e.g., ['query', 'page']).
            row_limit (int): Limit the number of rows returned (default is 10).
            
        Returns:
            Optional[Dict[str, Any]]: The search analytics report as a dictionary or None if an error occurs.
        """
        try:
            request_body = {
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': dimensions,
                'rowLimit': row_limit
            }
            response = self.search_console.searchanalytics().query(siteUrl=site_url, body=request_body).execute()
            log_info(f"Successfully fetched Search Console data for site: {site_url}")
            return response
        except Exception as e:
            log_error(f"Failed to fetch Search Console data for site {site_url}: {e}")
            return None

    def get_coverage_data(self, site_url: str, start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
        """
        Fetch coverage data from Google Search Console.
        
        Args:
            site_url (str): The URL of the site.
            start_date (str): The start date (e.g., '2023-01-01').
            end_date (str): The end date (e.g., '2023-12-31').
            
        Returns:
            Optional[Dict[str, Any]]: The coverage data report or None if an error occurs.
        """
        try:
            request_body = {
                'startDate': start_date,
                'endDate': end_date
            }
            # The URL Testing Tools API might be used for coverage data (adjust API if needed)
            response = self.search_console.urlTestingTools().query(siteUrl=site_url, body=request_body).execute()
            log_info(f"Successfully fetched coverage data for site: {site_url}")
            return response
        except Exception as e:
            log_error(f"Failed to fetch coverage data for site {site_url}: {e}")
            return None

    def get_sitemap_data(self, site_url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch sitemap data from Google Search Console.
        
        Args:
            site_url (str): The URL of the site.
            
        Returns:
            Optional[Dict[str, Any]]: The sitemap data report or None if an error occurs.
        """
        try:
            # The sitemaps().list() method does not require a request body.
            response = self.search_console.sitemaps().list(siteUrl=site_url).execute()
            log_info(f"Successfully fetched sitemap data for site: {site_url}")
            return response
        except Exception as e:
            log_error(f"Failed to fetch sitemap data for site {site_url}: {e}")
            return None

# -------------------------------
# Example Usage (for testing purposes)
# -------------------------------
if __name__ == "__main__":
    # Use default site URL from configuration if available, otherwise provide one.
    site_url = "https://example.com"  # Replace with your actual site URL
    credentials_path = "path/to/service_account.json"  # Replace with your actual service account JSON path

    gsc_service = GoogleSearchConsoleService(credentials_json=credentials_path)
    
    # Fetch search analytics data
    analytics_data = gsc_service.get_search_analytics(
        site_url=site_url,
        start_date="2024-01-01",
        end_date="2024-12-31",
        dimensions=["query", "page"],
        row_limit=20
    )
    print("Search Analytics Data:")
    print(analytics_data)
    
    # Fetch coverage data
    coverage_data = gsc_service.get_coverage_data(
        site_url=site_url,
        start_date="2024-01-01",
        end_date="2024-12-31"
    )
    print("Coverage Data:")
    print(coverage_data)
    
    # Fetch sitemap data
    sitemap_data = gsc_service.get_sitemap_data(site_url=site_url)
    print("Sitemap Data:")
    print(sitemap_data)

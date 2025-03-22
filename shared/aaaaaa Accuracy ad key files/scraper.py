# scraper.py - Shared Scraper Service for RLG Data and RLG Fans

import requests
from bs4 import BeautifulSoup
import logging
import json
from concurrent.futures import ThreadPoolExecutor
from shared.utils.cache_manager import CacheManager
from shared.utils.geo_utils import validate_geolocation
from shared.utils.data_storage import save_scraped_data
from shared.monitoring import log_event, track_performance

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScraperService:
    """
    Scraper service to handle web scraping and data retrieval for RLG Data and RLG Fans.
    """

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.cache = CacheManager()

    @track_performance
    def scrape_url(self, url, params=None, parse_json=False):
        """
        Scrapes a given URL and returns its content.
        :param url: The URL to scrape
        :param params: Optional query parameters for the request
        :param parse_json: Whether to parse JSON content
        :return: Scraped data (HTML or JSON)
        """
        try:
            logger.info(f"Scraping URL: {url} with params: {params}")
            
            # Check cache before scraping
            cached_data = self.cache.get(url)
            if cached_data:
                logger.info(f"Cache hit for URL: {url}")
                return cached_data

            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()

            if parse_json:
                content = response.json()
            else:
                content = response.text

            # Cache the result for future use
            self.cache.set(url, content)

            logger.info(f"Successfully scraped URL: {url}")
            return content
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error while scraping {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error while scraping {url}: {e}")
            raise

    @track_performance
    def scrape_multiple_urls(self, urls, params=None, parse_json=False, max_threads=5):
        """
        Scrapes multiple URLs concurrently.
        :param urls: List of URLs to scrape
        :param params: Optional query parameters for each request
        :param parse_json: Whether to parse JSON content
        :param max_threads: Maximum number of threads to use
        :return: Dictionary of URL -> scraped data
        """
        results = {}
        try:
            with ThreadPoolExecutor(max_threads) as executor:
                futures = {
                    executor.submit(self.scrape_url, url, params, parse_json): url
                    for url in urls
                }
                for future in futures:
                    url = futures[future]
                    try:
                        results[url] = future.result()
                    except Exception as e:
                        logger.error(f"Error scraping {url}: {e}")
            logger.info("Successfully completed concurrent scraping")
        except Exception as e:
            logger.error(f"Error in concurrent scraping: {e}")
        return results

    def parse_html(self, html, selectors):
        """
        Parses HTML content using the provided CSS selectors.
        :param html: HTML content to parse
        :param selectors: Dictionary of {field_name: CSS selector}
        :return: Parsed data as a dictionary
        """
        try:
            soup = BeautifulSoup(html, "html.parser")
            parsed_data = {}
            for field, selector in selectors.items():
                element = soup.select_one(selector)
                parsed_data[field] = element.text.strip() if element else None
            logger.info(f"Parsed data: {json.dumps(parsed_data, indent=2)}")
            return parsed_data
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            raise

    def scrape_and_store(self, url, selectors, store=True, metadata=None):
        """
        Scrapes a URL, parses it using CSS selectors, and optionally stores the data.
        :param url: URL to scrape
        :param selectors: CSS selectors for parsing
        :param store: Whether to store the parsed data
        :param metadata: Optional metadata for storage
        :return: Parsed data
        """
        try:
            logger.info(f"Starting scrape_and_store for URL: {url}")
            html = self.scrape_url(url)
            parsed_data = self.parse_html(html, selectors)

            if store:
                save_scraped_data(parsed_data, metadata)
                logger.info(f"Data saved for URL: {url}")

            return parsed_data
        except Exception as e:
            logger.error(f"Error in scrape_and_store: {e}")
            raise

    def validate_scrape_by_location(self, url, ip_address):
        """
        Validates if a scrape is allowed based on the user's geolocation.
        :param url: URL to scrape
        :param ip_address: User's IP address
        :return: Scraped content or error message
        """
        try:
            location_data = validate_geolocation(ip_address)
            if location_data.get("restricted"):
                logger.warning(f"Scrape blocked for restricted location: {location_data}")
                return {"error": "Scraping is restricted in your location"}

            return self.scrape_url(url)
        except Exception as e:
            logger.error(f"Error validating scrape by location: {e}")
            raise


# Standalone functions
def test_scraper():
    """
    Tests the scraper service functionality.
    """
    scraper = ScraperService()
    test_url = "https://example.com"
    selectors = {"title": "title", "header": "h1"}

    try:
        logger.info("Testing scraper with example URL")
        parsed_data = scraper.scrape_and_store(test_url, selectors, store=False)
        logger.info(f"Test scrape result: {parsed_data}")
    except Exception as e:
        logger.error(f"Scraper test failed: {e}")


# Main entry point for manual testing
if __name__ == "__main__":
    test_scraper()

scraper = ScraperService()

# Single URL scraping
html_data = scraper.scrape_url("https://example.com")

# Concurrent scraping
urls = ["https://example1.com", "https://example2.com"]
results = scraper.scrape_multiple_urls(urls)

# Parse HTML
parsed_data = scraper.parse_html(html_data, {"title": "title", "header": "h1"})

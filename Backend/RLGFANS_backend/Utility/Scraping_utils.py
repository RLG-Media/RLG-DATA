# scraping_utils.py - Utility functions for web scraping and data extraction for RLG Fans

import datetime
import requests
from bs4 import BeautifulSoup
import logging
from time import sleep
from random import uniform
from urllib.parse import urljoin
from fake_useragent import UserAgent

logger = logging.getLogger("RLG_Fans.ScrapingUtils")
ua = UserAgent()

class ScraperUtils:
    """
    Utility class containing helper functions for web scraping.
    This includes HTML parsing, request handling, and data extraction.
    """

    @staticmethod
    def get_html_content(url, retries=3, delay=2):
        """
        Fetch HTML content from the specified URL with retries and delays to avoid detection.

        Args:
            url (str): URL to fetch content from.
            retries (int): Number of retries in case of request failure.
            delay (float): Delay between retries to avoid server blocking.

        Returns:
            BeautifulSoup object if successful, None otherwise.
        """
        headers = {'User-Agent': ua.random}
        for attempt in range(retries):
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    logger.info(f"Successfully fetched HTML content for {url}")
                    return BeautifulSoup(response.text, 'html.parser')
                else:
                    logger.warning(f"Failed to fetch {url} - Status code: {response.status_code}")
            except requests.RequestException as e:
                logger.error(f"Request error on {url} - Attempt {attempt+1}/{retries}: {e}")
                sleep(delay)
        return None

    @staticmethod
    def extract_links(soup, base_url):
        """
        Extract all links from a BeautifulSoup object and convert to absolute URLs.

        Args:
            soup (BeautifulSoup): Parsed HTML content.
            base_url (str): Base URL to resolve relative URLs.

        Returns:
            list of str: Absolute URLs found in the content.
        """
        links = []
        for link in soup.find_all('a', href=True):
            abs_url = urljoin(base_url, link['href'])
            links.append(abs_url)
        logger.info(f"Extracted {len(links)} links from {base_url}")
        return links

    @staticmethod
    def parse_trending_content(soup):
        """
        Parse trending content elements from the HTML based on predefined patterns.

        Args:
            soup (BeautifulSoup): Parsed HTML content.

        Returns:
            list of dict: List of trending content with title, URL, and summary.
        """
        trending_content = []
        for item in soup.select('.trending-item'):
            title = item.get_text(strip=True)
            url = item.get('href')
            summary = item.select_one('.summary').get_text(strip=True) if item.select_one('.summary') else ""
            trending_content.append({'title': title, 'url': url, 'summary': summary})
        logger.info(f"Parsed {len(trending_content)} trending content items")
        return trending_content

    @staticmethod
    def save_content_to_db(content_list, platform, db_session):
        """
        Save extracted content to the database.

        Args:
            content_list (list of dict): Extracted content to save.
            platform (str): Platform name.
            db_session: Database session for committing data.
        """
        from models import PlatformContent  # Local import to avoid circular dependencies
        for content in content_list:
            entry = PlatformContent(
                title=content['title'],
                url=content['url'],
                summary=content['summary'],
                platform=platform,
                created_at=datetime.now()
            )
            db_session.add(entry)
        db_session.commit()
        logger.info(f"Saved {len(content_list)} items to database for platform {platform}")

    @staticmethod
    def random_delay(min_delay=1, max_delay=3):
        """
        Random delay to mimic human behavior.

        Args:
            min_delay (int): Minimum delay in seconds.
            max_delay (int): Maximum delay in seconds.
        """
        delay = uniform(min_delay, max_delay)
        logger.debug(f"Sleeping for {delay:.2f} seconds to mimic human behavior")
        sleep(delay)
    
    @staticmethod
    def analyze_trending_keywords(content_list):
        """
        Analyze trending keywords from content titles.

        Args:
            content_list (list of dict): List of content items with 'title' field.

        Returns:
            dict: Keyword frequency analysis results.
        """
        from collections import Counter
        keywords = []
        for content in content_list:
            keywords.extend(content['title'].split())
        keyword_counts = dict(Counter(keywords))
        logger.info(f"Analyzed trending keywords from {len(content_list)} items")
        return keyword_counts

    @staticmethod
    def fetch_data_with_retry(url, retries=3, delay=1):
        """
        Fetches data from a URL with retry logic and exponential backoff.

        Args:
            url (str): The URL to fetch data from.
            retries (int): Number of retries for fetching data.
            delay (float): Initial delay between retries.

        Returns:
            response or None: The response object if the request is successful, else None.
        """
        headers = {'User-Agent': ua.random}
        for attempt in range(retries):
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    logger.info(f"Data fetched successfully from {url}")
                    return response
            except requests.RequestException as e:
                logger.warning(f"Retry {attempt+1}/{retries} for {url} due to error: {e}")
                sleep(delay * (2 ** attempt))  # Exponential backoff
        logger.error(f"Failed to fetch data from {url} after {retries} retries")
        return None

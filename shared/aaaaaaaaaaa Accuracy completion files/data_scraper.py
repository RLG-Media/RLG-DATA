"""
datascraper.py

This module provides robust scraping functions for both RLG Data and RLG Fans.
- RLG Data: Scrapes media-related content from news or media websites.
- RLG Fans: Scrapes social media or community forum pages for fan engagement metrics.
Additionally, this updated version attempts to extract location information (e.g., country, city, town)
from the scraped text using simple regex-based heuristics. You can extend or replace this stub
with more advanced geocoding or NLP techniques as needed.

Both functions are designed to be robust, region-, country-, city-, town-aware, and scalable.
"""

import re
import requests
from bs4 import BeautifulSoup
import logging
import time

# Configure logging for the scraper
logger = logging.getLogger("DataScraper")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

# Sample configuration for region-specific URLs or selectors.
# In production, these settings could be loaded from an external configuration file.
REGION_CONFIG = {
    "default": {
        "rlg_data_url": "https://example.com/news",       # Replace with a real media/news site URL.
        "rlg_fans_url": "https://example.com/social",       # Replace with a real social/community site URL.
        "data_selector": ".article",                        # CSS selector for articles.
        "fans_selector": ".post",                           # CSS selector for social posts.
    },
    "us": {
        "rlg_data_url": "https://us.example.com/news",
        "rlg_fans_url": "https://us.example.com/social",
        "data_selector": ".news-item",
        "fans_selector": ".social-post",
    },
    # Add additional regions as needed.
}

def fetch_html(url, retries=3, delay=2):
    """
    Fetch HTML content from the given URL with retries.

    Parameters:
        url (str): The URL to fetch.
        retries (int): Number of retries if the request fails.
        delay (int): Delay (in seconds) between retries.

    Returns:
        str: HTML content if successful, None otherwise.
    """
    for attempt in range(1, retries + 1):
        try:
            logger.debug(f"Fetching URL: {url} (Attempt {attempt})")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            logger.debug("Successfully fetched HTML content.")
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}. Attempt {attempt} of {retries}.")
            time.sleep(delay)
    return None

def parse_location(text):
    """
    A simple heuristic function to extract location information (country, city, town)
    from the provided text using regex patterns.
    
    Parameters:
        text (str): The text from which to extract location info.
        
    Returns:
        dict: A dictionary with keys 'country', 'city', and 'town'. Defaults to "Unknown" if not found.
        
    Note:
        This function is a stub for demonstration. For accurate location extraction, consider integrating
        with NLP libraries or geocoding APIs.
    """
    # For demonstration, we try to match patterns like "in City" or "from City"
    # This is a very basic example and should be replaced with more robust processing.
    country = "Unknown"
    city = "Unknown"
    town = "Unknown"
    
    # Example regex to extract a capitalized word following "in" or "from"
    match = re.search(r'\b(?:in|from)\s+([A-Z][a-zA-Z]+)', text)
    if match:
        city = match.group(1)
        # Optionally set country based on city if known (stub example)
        # In real implementation, you might use a lookup table or geocoding API.
        country = "USA"  # Example default for demonstration.
    
    # Further regex patterns can be added to extract town or other granular location data.
    return {"country": country, "city": city, "town": town}

def parse_media_data(html_content, selector):
    """
    Parse HTML content to extract media-related data using the provided CSS selector.

    Parameters:
        html_content (str): HTML content of the page.
        selector (str): CSS selector to find article elements.

    Returns:
        list: A list of dictionaries representing media items.
              Each dictionary includes the title and, if available, location info.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    articles = soup.select(selector)
    results = []
    for article in articles:
        try:
            title = article.get_text(strip=True)
            # Optionally extract location info from the title (or other sub-elements)
            location_info = parse_location(title)
            results.append({"title": title, "location": location_info})
        except Exception as e:
            logger.error(f"Error parsing an article element: {e}")
    logger.info(f"Extracted {len(results)} media items.")
    return results

def parse_fans_data(html_content, selector):
    """
    Parse HTML content to extract fan engagement data using the provided CSS selector.

    Parameters:
        html_content (str): HTML content of the page.
        selector (str): CSS selector to find social post elements.

    Returns:
        list: A list of dictionaries representing fan posts.
              Each dictionary includes the content and, if available, location info.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    posts = soup.select(selector)
    results = []
    for post in posts:
        try:
            content = post.get_text(strip=True)
            # Optionally extract location info from the content
            location_info = parse_location(content)
            results.append({"content": content, "location": location_info})
        except Exception as e:
            logger.error(f"Error parsing a social post element: {e}")
    logger.info(f"Extracted {len(results)} fan posts.")
    return results

def scrape_data_for_rlg_data(region="default"):
    """
    Scrape media data for RLG Data from the configured source.

    Parameters:
        region (str): Region key to select the appropriate configuration.

    Returns:
        dict: A dictionary with scraped media data and metadata.
              Includes source URL, region, total articles, and the list of articles.
    """
    config = REGION_CONFIG.get(region, REGION_CONFIG["default"])
    url = config["rlg_data_url"]
    selector = config["data_selector"]

    logger.info(f"Scraping RLG Data from {url} for region '{region}'")
    html_content = fetch_html(url)
    if html_content is None:
        logger.error("Failed to retrieve HTML content for RLG Data.")
        return {"error": "Failed to retrieve data", "data": []}

    articles = parse_media_data(html_content, selector)
    # Optionally, add further processing like sentiment analysis or keyword extraction here.
    scraped_data = {
        "source": url,
        "region": region,
        "total_articles": len(articles),
        "articles": articles
    }
    logger.info("Successfully scraped RLG Data.")
    return scraped_data

def scrape_data_for_rlg_fans(region="default"):
    """
    Scrape fan engagement data for RLG Fans from the configured source.

    Parameters:
        region (str): Region key to select the appropriate configuration.

    Returns:
        dict: A dictionary with scraped fan data and metadata.
              Includes source URL, region, total posts, and the list of fan posts.
    """
    config = REGION_CONFIG.get(region, REGION_CONFIG["default"])
    url = config["rlg_fans_url"]
    selector = config["fans_selector"]

    logger.info(f"Scraping RLG Fans data from {url} for region '{region}'")
    html_content = fetch_html(url)
    if html_content is None:
        logger.error("Failed to retrieve HTML content for RLG Fans.")
        return {"error": "Failed to retrieve data", "fans": []}

    posts = parse_fans_data(html_content, selector)
    # Optionally, add further processing like engagement scoring or trend analysis here.
    scraped_data = {
        "source": url,
        "region": region,
        "total_posts": len(posts),
        "fans": posts
    }
    logger.info("Successfully scraped RLG Fans data.")
    return scraped_data

# -------------------------------
# Additional Recommendations:
# -------------------------------
# 1. For pages that load content dynamically, consider using Selenium or Playwright to render JavaScript.
# 2. Incorporate proxy and user-agent rotation if scraping sites with anti-scraping measures.
# 3. Implement caching (e.g., using requests_cache) for frequently accessed pages to improve performance.
# 4. Validate and sanitize all extracted data to prevent issues downstream.
# 5. For high-volume scraping, consider asynchronous approaches (e.g., using aiohttp and asyncio) to improve scalability.
# 6. Enhance location extraction by integrating with NLP libraries or geocoding APIs for country, city, and town accuracy.
# 7. Move region-specific settings and CSS selectors to an external configuration file for easier management and tuning.

if __name__ == "__main__":
    # For standalone testing, print sample scraped data for the default region.
    logger.info("Starting standalone test for RLG Data scraping:")
    rlg_data = scrape_data_for_rlg_data()
    logger.info(f"RLG Data Scraped: {rlg_data}")

    logger.info("Starting standalone test for RLG Fans scraping:")
    rlg_fans = scrape_data_for_rlg_fans()
    logger.info(f"RLG Fans Scraped: {rlg_fans}")

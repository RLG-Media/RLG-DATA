import requests
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def check_robots_txt(url):
    """
    Check whether the URL is allowed to be scraped based on the site's robots.txt file.
    
    :param url: URL of the site to be scraped
    :return: True if scraping is allowed, False otherwise
    """
    try:
        robots_url = f"{url}/robots.txt"
        parser = RobotFileParser()
        parser.set_url(robots_url)
        parser.read()

        # Check if scraping is allowed for all user-agents
        return parser.can_fetch('*', url)

    except Exception as e:
        logging.error(f"Failed to read robots.txt for {url}: {e}")
        return False


def fetch_page(url, delay=1):
    """
    Fetch the HTML content of a given page, with optional delay to avoid overwhelming the server.
    
    :param url: The URL to scrape
    :param delay: Delay in seconds between requests (to avoid server overload)
    :return: The HTML content of the page if successful, None otherwise
    """
    try:
        time.sleep(delay)  # Respectful scraping, add delay between requests
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for bad HTTP responses

        logging.info(f"Successfully fetched page: {url}")
        return response.content

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching page {url}: {e}")
        return None


def extract_data(soup, tag, attribute=None, value=None):
    """
    Extracts data from a BeautifulSoup object based on HTML tag, and optionally attribute and value.
    
    :param soup: The BeautifulSoup object to search within
    :param tag: The HTML tag to search for (e.g., 'div', 'a', 'p')
    :param attribute: The attribute to filter by (optional, e.g., 'class', 'id')
    :param value: The value of the attribute to filter by (optional)
    :return: A list of elements that match the criteria
    """
    try:
        if attribute and value:
            elements = soup.find_all(tag, {attribute: value})
        else:
            elements = soup.find_all(tag)

        logging.info(f"Extracted {len(elements)} elements using tag: {tag}, attribute: {attribute}, value: {value}")
        return elements

    except Exception as e:
        logging.error(f"Error extracting data with tag: {tag}, attribute: {attribute}, value: {value} - {e}")
        return []


def scrape_website(url, tag, attribute=None, value=None, delay=1):
    """
    Scrape a website by fetching its HTML content and extracting specific data based on the given tag and attribute.
    
    :param url: The URL to scrape
    :param tag: The HTML tag to search for (e.g., 'div', 'a', 'p')
    :param attribute: The attribute to filter by (optional, e.g., 'class', 'id')
    :param value: The value of the attribute to filter by (optional)
    :param delay: Delay between requests in seconds
    :return: A list of extracted elements from the page
    """
    # Step 1: Check if the website allows scraping via robots.txt
    if not check_robots_txt(url):
        logging.warning(f"Scraping is disallowed by robots.txt for {url}")
        return []

    # Step 2: Fetch the page content
    html_content = fetch_page(url, delay=delay)
    if not html_content:
        logging.error(f"Failed to fetch page: {url}")
        return []

    # Step 3: Parse the content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Step 4: Extract data based on tag, attribute, and value
    extracted_elements = extract_data(soup, tag, attribute, value)

    return extracted_elements


def scrape_multiple_urls(urls, tag, attribute=None, value=None, delay=1):
    """
    Scrape multiple URLs in sequence, fetching data from each based on the given tag and attribute.
    
    :param urls: A list of URLs to scrape
    :param tag: The HTML tag to search for (e.g., 'div', 'a', 'p')
    :param attribute: The attribute to filter by (optional)
    :param value: The value of the attribute to filter by (optional)
    :param delay: Delay between each request
    :return: A dictionary where the keys are URLs and values are lists of extracted elements
    """
    results = {}
    for url in urls:
        logging.info(f"Scraping URL: {url}")
        results[url] = scrape_website(url, tag, attribute, value, delay)

    return results

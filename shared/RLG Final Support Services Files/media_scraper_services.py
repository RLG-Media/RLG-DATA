import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime
import json
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("media_scraper_services.log"),
        logging.StreamHandler()
    ]
)

class MediaScraperService:
    """
    Service for scraping mainstream and community media websites for RLG Data and RLG Fans.
    """

    def __init__(self, user_agent: str = "RLG Media Scraper/1.0", rate_limit: float = 1.0):
        """
        Initialize the MediaScraperService.

        Args:
            user_agent: The User-Agent string to use for HTTP requests.
            rate_limit: Minimum time in seconds between requests to avoid overloading servers.
        """
        self.headers = {"User-Agent": user_agent}
        self.rate_limit = rate_limit
        logging.info("MediaScraperService initialized with rate limit: %.2f seconds", rate_limit)

    def fetch_html(self, url: str) -> Optional[str]:
        """
        Fetch the raw HTML content of a webpage.

        Args:
            url: The URL of the webpage to scrape.

        Returns:
            The HTML content of the page or None if the request fails.
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            logging.info("Successfully fetched content from %s", url)
            return response.text
        except requests.RequestException as e:
            logging.error("Failed to fetch content from %s: %s", url, e)
            return None

    def parse_article_links(self, html: str, base_url: str, link_selector: str) -> List[str]:
        """
        Extract article links from a webpage.

        Args:
            html: The raw HTML content of the page.
            base_url: The base URL to resolve relative links.
            link_selector: CSS selector for identifying article links.

        Returns:
            A list of fully resolved article URLs.
        """
        try:
            soup = BeautifulSoup(html, "html.parser")
            links = []
            for anchor in soup.select(link_selector):
                href = anchor.get("href")
                if href:
                    full_url = href if href.startswith("http") else base_url + href
                    links.append(full_url)
            logging.info("Extracted %d article links", len(links))
            return links
        except Exception as e:
            logging.error("Failed to parse article links: %s", e)
            return []

    def scrape_article(self, url: str, content_selector: str) -> Optional[Dict]:
        """
        Scrape the content of a single article.

        Args:
            url: The URL of the article to scrape.
            content_selector: CSS selector for the article content.

        Returns:
            A dictionary containing the article title, content, and metadata, or None if scraping fails.
        """
        html = self.fetch_html(url)
        if not html:
            return None

        try:
            soup = BeautifulSoup(html, "html.parser")
            title = soup.title.string.strip() if soup.title else "Untitled"
            content = " ".join([p.get_text(strip=True) for p in soup.select(content_selector)])
            scraped_at = datetime.utcnow().isoformat()

            article_data = {
                "url": url,
                "title": title,
                "content": content,
                "scraped_at": scraped_at
            }
            logging.info("Successfully scraped article from %s", url)
            return article_data
        except Exception as e:
            logging.error("Failed to scrape article from %s: %s", url, e)
            return None

    def batch_scrape(self, urls: List[str], content_selector: str) -> List[Dict]:
        """
        Scrape multiple articles.

        Args:
            urls: A list of article URLs to scrape.
            content_selector: CSS selector for the article content.

        Returns:
            A list of dictionaries containing scraped article data.
        """
        articles = []
        for url in urls:
            time.sleep(self.rate_limit)  # Respect rate limiting
            article = self.scrape_article(url, content_selector)
            if article:
                articles.append(article)
        logging.info("Batch scraping complete. Scraped %d articles.", len(articles))
        return articles

    def save_scraped_data(self, data: List[Dict], output_path: str):
        """
        Save scraped data to a JSON file.

        Args:
            data: The list of scraped article data.
            output_path: Path to the output JSON file.
        """
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logging.info("Scraped data saved to %s", output_path)
        except Exception as e:
            logging.error("Failed to save scraped data to %s: %s", output_path, e)

# Example usage
if __name__ == "__main__":
    scraper = MediaScraperService()

    # Example configuration
    test_url = "https://example-news-site.com"
    article_page_selector = ".article-link"
    article_content_selector = "article p"

    # Fetch and parse links
    homepage_html = scraper.fetch_html(test_url)
    if homepage_html:
        article_links = scraper.parse_article_links(homepage_html, test_url, article_page_selector)

        # Scrape articles
        scraped_articles = scraper.batch_scrape(article_links[:5], article_content_selector)

        # Save results
        scraper.save_scraped_data(scraped_articles, "scraped_articles.json")

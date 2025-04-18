import requests
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
import re
import logging
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("monetization_analytics_services.log"),  # Change filename as needed
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SEOInsights:
    """
    SEO Insights Tool for gathering, analyzing, and reporting keyword data,
    competitor insights, and traffic metrics for both RLG Data and RLG Fans.
    """

    def __init__(self):
        # Replace the placeholders below with your actual API keys,
        # preferably loaded from environment variables.
        self.google_search_api = "https://serpapi.com/search.json"
        self.api_key = "YOUR_SERPAPI_KEY"  # Replace with your SerpAPI key
        self.similarweb_api = "https://api.similarweb.com/v1/website/"
        self.similarweb_key = "YOUR_SIMILARWEB_API_KEY"  # Replace with your SimilarWeb API key
        logger.info("SEOInsights tool initialized.")

    def get_search_volume(self, keyword: str) -> Optional[Dict[str, Any]]:
        """
        Fetch search volume and competition data for a keyword using the Google Search API via SerpAPI.

        Args:
            keyword (str): The keyword to search.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing search volume metrics; None on error.
        """
        logger.info(f"Fetching search volume for keyword: {keyword}")
        params = {
            "engine": "google",
            "q": keyword,
            "api_key": self.api_key,
        }
        try:
            response = requests.get(self.google_search_api, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            search_data = {
                "keyword": keyword,
                "total_results": int(data.get("search_information", {}).get("total_results", 0)),
                "search_time": data.get("search_information", {}).get("search_time", 0),
                "featured_snippets": any(result.get("snippet") for result in data.get("organic_results", [])),
            }
            logger.info(f"Search volume for '{keyword}': {search_data}")
            return search_data
        except requests.RequestException as e:
            logger.error(f"Error fetching search volume for '{keyword}': {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing search volume response for '{keyword}': {e}")
            return None

    def get_competitors(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Fetch top competitors for a specific keyword from the Google Search API via SerpAPI.

        Args:
            keyword (str): The keyword to search competitors for.

        Returns:
            List[Dict[str, Any]]: List of competitor data dictionaries.
        """
        logger.info(f"Fetching competitors for keyword: {keyword}")
        params = {
            "engine": "google",
            "q": keyword,
            "api_key": self.api_key,
        }
        try:
            response = requests.get(self.google_search_api, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            competitors = [
                {
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "rank": result.get("position", 0),
                }
                for result in data.get("organic_results", [])
            ]
            logger.info(f"Fetched {len(competitors)} competitors for keyword '{keyword}'.")
            return competitors
        except requests.RequestException as e:
            logger.error(f"Error fetching competitors for '{keyword}': {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching competitors for '{keyword}': {e}")
            return []

    def analyze_keyword_strength(self, keyword: str) -> Dict[str, Any]:
        """
        Analyze keyword strength by combining search volume and competitor data.

        Args:
            keyword (str): The keyword to analyze.

        Returns:
            Dict[str, Any]: Dictionary containing keyword strength metrics.
        """
        logger.info(f"Analyzing keyword strength for: {keyword}")
        search_volume = self.get_search_volume(keyword)
        competitors = self.get_competitors(keyword)

        if not search_volume:
            logger.error(f"Failed to analyze keyword: {keyword} due to missing search volume data.")
            return {"error": f"Failed to analyze keyword: {keyword}"}

        keyword_strength = {
            "keyword": keyword,
            "total_results": search_volume.get("total_results", 0),
            "competition_level": len(competitors),
            "has_featured_snippets": search_volume.get("featured_snippets", False),
        }
        logger.info(f"Keyword strength for '{keyword}': {keyword_strength}")
        return keyword_strength

    def fetch_website_traffic(self, domain: str) -> Optional[Dict[str, Any]]:
        """
        Fetch traffic data for a specific domain using the SimilarWeb API.

        Args:
            domain (str): The domain to fetch traffic data for.

        Returns:
            Optional[Dict[str, Any]]: Dictionary containing traffic metrics; None on error.
        """
        logger.info(f"Fetching website traffic for domain: {domain}")
        url = f"{self.similarweb_api}{domain}/total-traffic-and-engagement/visits"
        params = {"api_key": self.similarweb_key}
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            traffic_data = {
                "domain": domain,
                "monthly_visits": data.get("visits", 0),
                "engagement_score": data.get("engagement_score", 0),
            }
            logger.info(f"Traffic data for {domain}: {traffic_data}")
            return traffic_data
        except requests.RequestException as e:
            logger.error(f"Error fetching traffic data for {domain}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching traffic data for {domain}: {e}")
            return None

    def parse_google_trends(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Scrape Google Trends for related keyword trends.

        Args:
            keyword (str): The keyword to search on Google Trends.

        Returns:
            List[Dict[str, Any]]: List of dictionaries with trend information.
        """
        logger.info(f"Scraping Google Trends for keyword: {keyword}")
        trends = []
        # Note: Google Trends uses dynamic content; this basic scraper may not work reliably.
        url = f"https://trends.google.com/trends/explore?q={keyword}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            # This CSS selector and parsing logic are simplistic; adjust as needed.
            for trend in soup.select(".related-queries .item"):
                text = trend.get_text(strip=True)
                # Extract numeric value from the text, if present.
                match = re.search(r"(\d+)", text)
                search_score = int(match.group(1)) if match else 0
                trends.append({
                    "query": text,
                    "search_score": search_score,
                })
            logger.info(f"Found {len(trends)} related trends for keyword '{keyword}'.")
        except Exception as e:
            logger.error(f"Error parsing Google Trends data for '{keyword}': {e}")
        return trends

    def generate_report(self, keyword: str) -> Dict[str, Any]:
        """
        Generate a comprehensive SEO report for a given keyword.

        The report includes search volume, competitor data, keyword strength,
        and related trends.

        Args:
            keyword (str): The keyword to generate the report for.

        Returns:
            Dict[str, Any]: A dictionary containing the SEO report.
        """
        logger.info(f"Generating SEO report for keyword: {keyword}")
        try:
            report = {
                "keyword": keyword,
                "search_volume": self.get_search_volume(keyword),
                "competitors": self.get_competitors(keyword),
                "keyword_strength": self.analyze_keyword_strength(keyword),
                "related_trends": self.parse_google_trends(keyword),
            }
            logger.info(f"SEO report for '{keyword}' generated successfully.")
            return report
        except Exception as e:
            logger.error(f"Error generating SEO report for '{keyword}': {e}")
            return {"error": "Failed to generate report"}

# -------------------------------
# Example Usage (for testing purposes)
# -------------------------------
if __name__ == "__main__":
    seo_tool = SEOInsights()
    test_keyword = "digital marketing"
    logger.info("Starting SEO Insights Tool...")
    report = seo_tool.generate_report(test_keyword)
    print(json.dumps(report, indent=2))

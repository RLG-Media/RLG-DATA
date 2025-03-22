import logging
import time
import requests
from typing import List, Dict, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("real_time_news_monitoring.log"),
        logging.StreamHandler()
    ]
)

class RealTimeNewsMonitoringService:
    """
    Service for real-time monitoring of news sources and platforms, covering mainstream, community, 
    international, and social media platforms for RLG Data and RLG Fans.
    """

    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        """
        Initialize the service with API keys for various news and social media platforms.

        Args:
            api_keys: A dictionary containing API keys for different platforms.
        """
        self.api_keys = api_keys or {}
        self.sources = {
            "news_api": "https://newsapi.org/v2/everything",
            "google_news": "https://www.googleapis.com/customsearch/v1",
            "reddit": "https://www.reddit.com/search.json",
            "twitter": "https://api.twitter.com/2/tweets/search/recent",
        }
        logging.info("RealTimeNewsMonitoringService initialized.")

    def fetch_news_from_newsapi(self, keyword: str, language: str = "en", page_size: int = 50) -> List[Dict]:
        """
        Fetch news articles from NewsAPI.

        Args:
            keyword: The keyword to search for.
            language: Language of the news articles (default: English).
            page_size: Number of articles to fetch per request (default: 50).

        Returns:
            A list of news articles.
        """
        url = self.sources["news_api"]
        headers = {"Authorization": f"Bearer {self.api_keys.get('news_api')}"}
        params = {"q": keyword, "language": language, "pageSize": page_size}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            articles = response.json().get("articles", [])
            logging.info("Fetched %d articles from NewsAPI for keyword '%s'.", len(articles), keyword)
            return articles
        except Exception as e:
            logging.error("Failed to fetch news from NewsAPI: %s", e)
            return []

    def fetch_news_from_reddit(self, keyword: str, subreddit: Optional[str] = None) -> List[Dict]:
        """
        Fetch news mentions from Reddit.

        Args:
            keyword: The keyword to search for.
            subreddit: Optional subreddit to limit the search to.

        Returns:
            A list of Reddit posts.
        """
        url = self.sources["reddit"]
        params = {"q": keyword, "restrict_sr": 1 if subreddit else 0, "subreddit": subreddit}
        headers = {"User-Agent": "RLGNewsMonitor/1.0"}

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            posts = response.json().get("data", {}).get("children", [])
            logging.info("Fetched %d posts from Reddit for keyword '%s'.", len(posts), keyword)
            return [post["data"] for post in posts]
        except Exception as e:
            logging.error("Failed to fetch news from Reddit: %s", e)
            return []

    def fetch_news_from_twitter(self, keyword: str, max_results: int = 50) -> List[Dict]:
        """
        Fetch recent tweets mentioning a specific keyword using Twitter API.

        Args:
            keyword: The keyword to search for in tweets.
            max_results: Maximum number of tweets to fetch (default: 50).

        Returns:
            A list of tweets.
        """
        url = self.sources["twitter"]
        headers = {"Authorization": f"Bearer {self.api_keys.get('twitter')}"}
        params = {"query": keyword, "max_results": max_results, "tweet.fields": "created_at,text,author_id"}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            tweets = response.json().get("data", [])
            logging.info("Fetched %d tweets for keyword '%s'.", len(tweets), keyword)
            return tweets
        except Exception as e:
            logging.error("Failed to fetch tweets: %s", e)
            return []

    def aggregate_news(self, keyword: str, language: str = "en", page_size: int = 50) -> Dict[str, List[Dict]]:
        """
        Aggregate news from all available sources.

        Args:
            keyword: The keyword to search for.
            language: Language of the news articles (default: English).
            page_size: Number of articles to fetch per source (default: 50).

        Returns:
            A dictionary containing aggregated news data from multiple sources.
        """
        return {
            "news_api": self.fetch_news_from_newsapi(keyword, language, page_size),
            "reddit": self.fetch_news_from_reddit(keyword),
            "twitter": self.fetch_news_from_twitter(keyword, page_size)
        }

    def schedule_monitoring(self, keyword: str, interval: int = 3600):
        """
        Schedule periodic monitoring for a specific keyword.

        Args:
            keyword: The keyword to monitor.
            interval: Time interval between fetches in seconds (default: 1 hour).
        """
        logging.info("Starting scheduled monitoring for keyword '%s' every %d seconds.", keyword, interval)
        while True:
            aggregated_news = self.aggregate_news(keyword)
            logging.info("Aggregated news for '%s': %s", keyword, aggregated_news)
            time.sleep(interval)

if __name__ == "__main__":
    api_keys = {
        "news_api": "your_newsapi_key",
        "twitter": "your_twitter_bearer_token",
    }

    service = RealTimeNewsMonitoringService(api_keys)
    keyword_to_monitor = "Artificial Intelligence"

    # Run a single aggregation
    aggregated_news = service.aggregate_news(keyword_to_monitor)
    print(aggregated_news)

    # Uncomment to schedule continuous monitoring
    # service.schedule_monitoring(keyword_to_monitor, interval=3600)

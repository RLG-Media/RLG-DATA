from googlenews import GoogleNews  # Ensure you have installed it via: pip install GoogleNews
from flask import current_app
from typing import Dict, Any, List, Union
from shared.utils import log_error, log_info  # Shared utilities for logging
import logging

# Optionally, configure logging if not already configured elsewhere in your app.
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

class GoogleNewsService:
    """
    Service class for interacting with Google News to fetch the latest headlines and news articles.
    Designed for both RLG Data and RLG Fans.
    """

    def __init__(self, language: str = "en", region: str = "US") -> None:
        """
        Initialize the Google News Service with the specified language and region.

        Args:
            language (str): The language code for the news (default: "en").
            region (str): The region code for the news (default: "US").
        """
        try:
            self.google_news = GoogleNews(lang=language, region=region)
            log_info(f"Google News Service initialized with language: {language} and region: {region}")
        except Exception as e:
            log_error(f"Error initializing Google News: {e}")
            raise

    def get_headlines(self, query: str, limit: int = 10) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Fetch Google News headlines for a given query.

        Args:
            query (str): The query to search headlines for.
            limit (int): The maximum number of headlines to return (default: 10).

        Returns:
            Union[List[Dict[str, Any]], Dict[str, Any]]: A list of dictionaries with headline data or an error dictionary.
        """
        try:
            log_info(f"Fetching Google News headlines for query: {query}")
            self.google_news.search(query)
            results = self.google_news.results(sort=True)

            if not results:
                log_info(f"No results found for query: {query}")
                return []

            headlines = []
            for result in results[:limit]:
                headlines.append({
                    "title": result.get("title", "No Title Available"),
                    "url": result.get("link", "No URL Available")
                })

            log_info(f"Fetched {len(headlines)} headlines for query: {query}")
            return headlines
        except Exception as e:
            log_error(f"Failed to fetch Google News data for query '{query}': {e}")
            return {"error": "Failed to fetch news data. Please try again later."}

    def get_trending_news(self, limit: int = 10) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Fetch trending news articles from Google News.

        Args:
            limit (int): The maximum number of trending articles to return (default: 10).

        Returns:
            Union[List[Dict[str, Any]], Dict[str, Any]]: A list of trending news articles or an error dictionary.
        """
        try:
            log_info("Fetching trending news from Google News")
            # "Trending" is used as a query to fetch trending topics.
            self.google_news.get_news("Trending")
            results = self.google_news.results(sort=True)

            if not results:
                log_info("No trending news found")
                return []

            trending_news = []
            for result in results[:limit]:
                trending_news.append({
                    "title": result.get("title", "No Title Available"),
                    "url": result.get("link", "No URL Available")
                })

            log_info(f"Fetched {len(trending_news)} trending news articles")
            return trending_news
        except Exception as e:
            log_error(f"Failed to fetch trending news: {e}")
            return {"error": "Failed to fetch trending news. Please try again later."}

# -------------------------------
# Example Usage (for testing purposes)
# -------------------------------
if __name__ == "__main__":
    # Initialize the Google News Service with default settings
    news_service = GoogleNewsService(language="en", region="US")

    # Fetch headlines for a specific query
    headlines = news_service.get_headlines(query="AI Technology", limit=5)
    print("Headlines for 'AI Technology':")
    print(headlines)

    # Fetch trending news articles
    trending = news_service.get_trending_news(limit=5)
    print("Trending News Articles:")
    print(trending)

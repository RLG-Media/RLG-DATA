from pytrends.request import TrendReq
import logging
import pandas as pd
from typing import List, Optional, Dict, Any
import re

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("google_trends_services.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GoogleTrendsService:
    """
    Service class for interacting with Google Trends to fetch trending searches,
    interest over time data, and related queries. This service is designed for both
    RLG Data and RLG Fans to gain SEO insights and monitor market trends.
    """

    def __init__(self, hl: str = 'en-US', tz: int = 360) -> None:
        """
        Initialize the Google Trends Service with the specified language and timezone.

        Args:
            hl (str): Language setting for Google Trends (default: 'en-US').
            tz (int): Timezone offset in minutes (default: 360).
        """
        try:
            self.pytrends = TrendReq(hl=hl, tz=tz)
            logger.info("Google Trends Service initialized successfully with hl=%s, tz=%d", hl, tz)
        except Exception as e:
            logger.error("Failed to initialize Google Trends Service: %s", e)
            raise

    def get_trending_searches(self, country: str = 'united_states') -> Optional[pd.DataFrame]:
        """
        Fetch trending searches for a specific country.

        Args:
            country (str): Country from which to fetch trends (e.g., 'united_states').

        Returns:
            Optional[pd.DataFrame]: DataFrame of trending search topics or None on error.
        """
        try:
            trending_searches = self.pytrends.trending_searches(pn=country)
            logger.info("Successfully fetched trending searches for %s", country)
            return trending_searches
        except Exception as e:
            logger.error("Failed to fetch trending searches for %s: %s", country, e)
            return None

    def get_interest_over_time(self, keywords: List[str], timeframe: str = 'today 12-m') -> Optional[pd.DataFrame]:
        """
        Retrieve interest over time data for the specified keywords.

        Args:
            keywords (List[str]): List of keywords to fetch trends for.
            timeframe (str): Timeframe for trends (default: 'today 12-m').

        Returns:
            Optional[pd.DataFrame]: DataFrame containing interest over time data or None on error.
        """
        try:
            self.pytrends.build_payload(keywords, timeframe=timeframe)
            interest_data = self.pytrends.interest_over_time()
            if interest_data.empty:
                logger.warning("No interest over time data returned for keywords: %s", keywords)
            else:
                logger.info("Successfully fetched interest over time for keywords: %s", keywords)
            return interest_data
        except Exception as e:
            logger.error("Failed to fetch interest over time data for keywords %s: %s", keywords, e)
            return None

    def get_related_queries(self, keyword: str, top: int = 10) -> Optional[Dict[str, Any]]:
        """
        Fetch related queries for a given keyword.

        Args:
            keyword (str): The base keyword to fetch related queries for.
            top (int): Number of top related queries to return (default: 10).

        Returns:
            Optional[Dict[str, Any]]: Dictionary containing related queries data, or None on error.
        """
        try:
            related_queries = self.pytrends.related_queries(keyword, top=top)
            logger.info("Successfully fetched related queries for keyword: %s", keyword)
            return related_queries
        except Exception as e:
            logger.error("Failed to fetch related queries for keyword %s: %s", keyword, e)
            return None

# -------------------------------
# Example Usage (for testing purposes)
# -------------------------------
if __name__ == "__main__":
    gtrends_service = GoogleTrendsService()
    
    # Fetch trending searches for the US
    trending_searches_us = gtrends_service.get_trending_searches(country='united_states')
    if trending_searches_us is not None:
        print("Trending Searches (US):")
        print(trending_searches_us)
    else:
        print("No trending searches available for the US.")
    
    # Fetch interest over time for specific keywords
    interest_over_time_data = gtrends_service.get_interest_over_time(keywords=['AI', 'Machine Learning'])
    if interest_over_time_data is not None:
        print("Interest Over Time:")
        print(interest_over_time_data)
    else:
        print("No interest over time data available.")
    
    # Fetch related queries for a given keyword
    related_queries = gtrends_service.get_related_queries(keyword='AI', top=5)
    if related_queries is not None:
        print("Related Queries for 'AI':")
        print(related_queries)
    else:
        print("No related queries available for 'AI'.")

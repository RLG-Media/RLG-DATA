import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from textblob import TextBlob
from collections import Counter

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("trending_insights.log"), logging.StreamHandler()]
)

class ContentTrendingInsights:
    """
    A tool for tracking and analyzing trending content across multiple platforms.
    Supports Twitter (X), Facebook, Instagram, TikTok, LinkedIn, Reddit, Pinterest, YouTube, and more.
    """

    def __init__(self, api_keys: Dict[str, str]):
        """
        Initialize the trending insights tracker.

        Args:
            api_keys (Dict[str, str]): API keys for various social media platforms.
        """
        self.api_keys = api_keys
        self.platforms = [
            "twitter", "facebook", "instagram", "tiktok", "linkedin", 
            "reddit", "pinterest", "youtube"
        ]
        self.trending_data = {}

    def fetch_trending_topics(self, platform: str, location: Optional[str] = "global") -> List[Dict]:
        """
        Fetch trending topics from a specific platform.

        Args:
            platform (str): The platform name (e.g., "twitter", "youtube").
            location (Optional[str]): The region for trending data.

        Returns:
            List[Dict]: A list of trending topics with metadata.
        """
        logging.info(f"Fetching trending topics for {platform} in {location}...")

        if platform == "twitter":
            return self.fetch_twitter_trends(location)
        elif platform == "youtube":
            return self.fetch_youtube_trends(location)
        elif platform == "reddit":
            return self.fetch_reddit_trends()
        else:
            logging.warning(f"Trending data for {platform} is not yet implemented.")
            return []

    def fetch_twitter_trends(self, location: str) -> List[Dict]:
        """
        Fetch trending topics from Twitter (X).

        Args:
            location (str): The region for trending data.

        Returns:
            List[Dict]: Trending topics from Twitter.
        """
        url = "https://api.twitter.com/1.1/trends/place.json"
        headers = {"Authorization": f"Bearer {self.api_keys['twitter']}"}
        params = {"id": 1 if location.lower() == "global" else self.get_woeid(location)}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            trends = [{"name": trend["name"], "tweet_volume": trend.get("tweet_volume", 0)} for trend in data[0]["trends"]]
            logging.info(f"Fetched {len(trends)} Twitter trends for {location}.")
            return trends
        except Exception as e:
            logging.error(f"Failed to fetch Twitter trends: {e}")
            return []

    def fetch_youtube_trends(self, location: str) -> List[Dict]:
        """
        Fetch trending videos from YouTube.

        Args:
            location (str): The country code for trending data.

        Returns:
            List[Dict]: Trending videos on YouTube.
        """
        url = f"https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part": "snippet,statistics",
            "chart": "mostPopular",
            "regionCode": location.upper(),
            "maxResults": 10,
            "key": self.api_keys["youtube"]
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            videos = [{"title": item["snippet"]["title"], "views": item["statistics"]["viewCount"]} for item in data["items"]]
            logging.info(f"Fetched {len(videos)} trending YouTube videos for {location}.")
            return videos
        except Exception as e:
            logging.error(f"Failed to fetch YouTube trends: {e}")
            return []

    def fetch_reddit_trends(self) -> List[Dict]:
        """
        Fetch trending posts from Reddit.

        Returns:
            List[Dict]: Trending Reddit posts.
        """
        url = "https://www.reddit.com/r/all/top/.json?limit=10"
        headers = {"User-Agent": "trending-insights/1.0"}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            posts = [{"title": post["data"]["title"], "upvotes": post["data"]["ups"]} for post in data["data"]["children"]]
            logging.info(f"Fetched {len(posts)} trending Reddit posts.")
            return posts
        except Exception as e:
            logging.error(f"Failed to fetch Reddit trends: {e}")
            return []

    def analyze_sentiment(self, text: str) -> str:
        """
        Perform sentiment analysis on text.

        Args:
            text (str): The text to analyze.

        Returns:
            str: "Positive", "Neutral", or "Negative"
        """
        analysis = TextBlob(text).sentiment.polarity
        if analysis > 0:
            return "Positive"
        elif analysis < 0:
            return "Negative"
        return "Neutral"

    def get_woeid(self, location: str) -> int:
        """
        Map a location name to a Twitter WOEID.

        Args:
            location (str): The location name.

        Returns:
            int: The corresponding WOEID.
        """
        woeid_mapping = {
            "global": 1, "south africa": 23424942, "usa": 23424977, "uk": 23424975
        }
        return woeid_mapping.get(location.lower(), 1)

    def compile_insights(self, locations: List[str]) -> Dict:
        """
        Compile trending insights across all platforms.

        Args:
            locations (List[str]): List of regions to fetch data for.

        Returns:
            Dict: A compiled report of trending topics.
        """
        logging.info("Compiling trending insights...")
        insights = {}

        for location in locations:
            insights[location] = {}

            for platform in self.platforms:
                trends = self.fetch_trending_topics(platform, location)
                insights[location][platform] = [
                    {
                        "name": item["name"] if "name" in item else item["title"],
                        "sentiment": self.analyze_sentiment(item["name"] if "name" in item else item["title"]),
                        "engagement": item.get("tweet_volume") or item.get("views") or item.get("upvotes", 0)
                    }
                    for item in trends
                ]

        return insights

# Example usage
if __name__ == "__main__":
    api_keys = {
        "twitter": "your-twitter-api-key",
        "youtube": "your-youtube-api-key"
    }

    trending_tool = ContentTrendingInsights(api_keys)
    insights = trending_tool.compile_insights(["global", "south africa", "usa"])
    
    print(json.dumps(insights, indent=4))

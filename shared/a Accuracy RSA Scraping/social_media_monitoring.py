import logging
from typing import List, Dict, Optional
from datetime import datetime
import tweepy
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("social_media_monitoring.log"),
        logging.StreamHandler()
    ]
)

class SocialMediaMonitoringService:
    """
    Service for monitoring social media platforms for RLG Data and RLG Fans.
    Supports Twitter, Instagram, Facebook, TikTok, LinkedIn, Pinterest, Reddit, Snapchat, and Threads.
    Includes sentiment analysis, scheduling, and reporting.
    """

    def __init__(self, twitter_api_keys: Optional[Dict[str, str]] = None):
        """
        Initialize the SocialMediaMonitoringService with optional API keys.

        Args:
            twitter_api_keys: Dictionary containing Twitter API keys.
                              Required keys: "consumer_key", "consumer_secret", "access_token", "access_token_secret".
        """
        self.twitter_api = None

        if twitter_api_keys:
            self.twitter_api = self._initialize_twitter_api(twitter_api_keys)
            logging.info("Twitter API initialized.")

    def _initialize_twitter_api(self, keys: Dict[str, str]):
        """
        Initialize the Twitter API client.

        Args:
            keys: Twitter API keys.

        Returns:
            Initialized Tweepy API client.
        """
        auth = tweepy.OAuth1UserHandler(
            keys["consumer_key"],
            keys["consumer_secret"],
            keys["access_token"],
            keys["access_token_secret"]
        )
        return tweepy.API(auth)

    def fetch_twitter_mentions(self, keyword: str, count: int = 50) -> List[Dict]:
        """
        Fetch recent tweets mentioning a specific keyword.

        Args:
            keyword: The keyword to search for in tweets.
            count: The number of tweets to fetch (default: 50).

        Returns:
            A list of dictionaries containing tweet data.
        """
        if not self.twitter_api:
            logging.error("Twitter API is not initialized.")
            return []

        try:
            tweets = self.twitter_api.search_tweets(q=keyword, count=count, tweet_mode="extended")
            results = []
            for tweet in tweets:
                results.append({
                    "id": tweet.id_str,
                    "text": tweet.full_text,
                    "user": tweet.user.screen_name,
                    "created_at": tweet.created_at.isoformat()
                })
            logging.info("Fetched %d tweets mentioning '%s'.", len(results), keyword)
            return results
        except Exception as e:
            logging.error("Failed to fetch tweets: %s", e)
            return []

    def fetch_instagram_posts(self, hashtag: str, access_token: str) -> List[Dict]:
        """
        Fetch recent Instagram posts for a specific hashtag.

        Args:
            hashtag: The hashtag to search for.
            access_token: Instagram Graph API access token.

        Returns:
            A list of dictionaries containing Instagram post data.
        """
        base_url = "https://graph.instagram.com/v12.0/ig_hashtag_search"
        try:
            hashtag_response = requests.get(
                base_url,
                params={"q": hashtag, "access_token": access_token}
            )
            hashtag_data = hashtag_response.json()

            if "id" not in hashtag_data:
                logging.error("Failed to fetch Instagram hashtag ID for '%s'.", hashtag)
                return []

            hashtag_id = hashtag_data["id"]
            posts_url = f"https://graph.instagram.com/{hashtag_id}/recent_media"

            posts_response = requests.get(
                posts_url,
                params={"fields": "id,caption,media_type,media_url,timestamp", "access_token": access_token}
            )
            posts_data = posts_response.json()

            logging.info("Fetched Instagram posts for hashtag '%s'.", hashtag)
            return posts_data.get("data", [])
        except Exception as e:
            logging.error("Failed to fetch Instagram posts: %s", e)
            return []

    def fetch_facebook_posts(self, page_id: str, access_token: str) -> List[Dict]:
        """
        Fetch recent posts from a Facebook page.

        Args:
            page_id: The ID of the Facebook page.
            access_token: Facebook Graph API access token.

        Returns:
            A list of dictionaries containing Facebook post data.
        """
        base_url = f"https://graph.facebook.com/v12.0/{page_id}/posts"
        try:
            response = requests.get(
                base_url,
                params={"fields": "id,message,created_time", "access_token": access_token}
            )
            posts_data = response.json()
            logging.info("Fetched posts from Facebook page ID '%s'.", page_id)
            return posts_data.get("data", [])
        except Exception as e:
            logging.error("Failed to fetch Facebook posts: %s", e)
            return []

    def fetch_tiktok_posts(self, hashtag: str, access_token: str) -> List[Dict]:
        """
        Fetch recent TikTok posts for a specific hashtag.

        Args:
            hashtag: The hashtag to search for.
            access_token: TikTok API access token.

        Returns:
            A list of dictionaries containing TikTok post data.
        """
        # Placeholder for TikTok API integration
        logging.warning("TikTok API integration not yet implemented.")
        return []

    def fetch_linkedin_posts(self, keyword: str, access_token: str) -> List[Dict]:
        """
        Fetch recent LinkedIn posts mentioning a keyword.

        Args:
            keyword: The keyword to search for.
            access_token: LinkedIn API access token.

        Returns:
            A list of dictionaries containing LinkedIn post data.
        """
        # Placeholder for LinkedIn API integration
        logging.warning("LinkedIn API integration not yet implemented.")
        return []

    def fetch_pinterest_posts(self, keyword: str, access_token: str) -> List[Dict]:
        """
        Fetch recent Pinterest posts for a specific keyword.

        Args:
            keyword: The keyword to search for.
            access_token: Pinterest API access token.

        Returns:
            A list of dictionaries containing Pinterest post data.
        """
        # Placeholder for Pinterest API integration
        logging.warning("Pinterest API integration not yet implemented.")
        return []

    def fetch_reddit_posts(self, subreddit: str, keyword: str) -> List[Dict]:
        """
        Fetch recent Reddit posts for a specific subreddit and keyword.

        Args:
            subreddit: The subreddit to search in.
            keyword: The keyword to search for.

        Returns:
            A list of dictionaries containing Reddit post data.
        """
        base_url = f"https://www.reddit.com/r/{subreddit}/search.json"
        try:
            response = requests.get(
                base_url,
                params={"q": keyword, "restrict_sr": 1},
                headers={"User-Agent": "RLG Social Media Monitor"}
            )
            posts_data = response.json()
            logging.info("Fetched posts from subreddit '%s' with keyword '%s'.", subreddit, keyword)
            return posts_data.get("data", {}).get("children", [])
        except Exception as e:
            logging.error("Failed to fetch Reddit posts: %s", e)
            return []

    def fetch_snapchat_data(self, keyword: str, access_token: str) -> List[Dict]:
        """
        Fetch recent Snapchat data for a specific keyword.

        Args:
            keyword: The keyword to search for.
            access_token: Snapchat API access token.

        Returns:
            A list of dictionaries containing Snapchat data.
        """
        # Placeholder for Snapchat API integration
        logging.warning("Snapchat API integration not yet implemented.")
        return []

    def fetch_threads_posts(self, keyword: str, access_token: str) -> List[Dict]:
        """
        Fetch recent Threads posts mentioning a keyword.

        Args:
            keyword: The keyword to search for.
            access_token: Threads API access token.

        Returns:
            A list of dictionaries containing Threads post data.
        """
        # Placeholder for Threads API integration
        logging.warning("Threads API integration not yet implemented.")
        return []

    def perform_sentiment_analysis(self, posts: List[Dict]) -> List[Dict]:
        """
        Perform sentiment analysis on social media posts.

        Args:
            posts: A list of dictionaries containing post data.

        Returns:
            A list of dictionaries with sentiment scores added.
        """
        from nltk.sentiment import SentimentIntensityAnalyzer
        nltk.download("vader_lexicon", quiet=True)

        analyzer = SentimentIntensityAnalyzer()
        for post in posts:
            post["sentiment"] = analyzer.polarity_scores(post.get("text", ""))
        logging.info("Sentiment analysis completed for %d posts.", len(posts))
        return posts

    def schedule_scraping(self, platform: str, interval: int, **kwargs):
        """
        Schedule scraping tasks for a specific platform.

        Args:
            platform: The platform to scrape (e.g., Twitter, Facebook).
           

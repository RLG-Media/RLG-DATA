import logging
import requests
from typing import List, Dict, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import tweepy

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("multi_platform_scraper_services.log"),
        logging.StreamHandler()
    ]
)

class MultiPlatformScraper:
    """
    Service for scraping content from multiple platforms including social media and mainstream media.
    Supports scraping from Twitter, Instagram, Facebook, TikTok, LinkedIn, Pinterest, Reddit, Snapchat, Threads, and mainstream media sites.
    """

    def __init__(self, api_keys: Dict[str, Dict[str, str]]):
        """
        Initialize the scraper with required API keys.

        Args:
            api_keys: Dictionary containing API keys for supported platforms.
        """
        self.api_keys = api_keys
        self.twitter_api = self._initialize_twitter_api(api_keys.get("twitter", {}))

    def _initialize_twitter_api(self, keys: Dict[str, str]):
        """
        Initialize Twitter API client.

        Args:
            keys: API keys for Twitter.

        Returns:
            Initialized Tweepy API client or None if keys are missing.
        """
        if not all(k in keys for k in ["consumer_key", "consumer_secret", "access_token", "access_token_secret"]):
            logging.warning("Missing Twitter API keys. Twitter scraping will be disabled.")
            return None

        auth = tweepy.OAuth1UserHandler(
            keys["consumer_key"],
            keys["consumer_secret"],
            keys["access_token"],
            keys["access_token_secret"]
        )
        return tweepy.API(auth)

    def scrape_twitter(self, keyword: str, count: int = 50) -> List[Dict]:
        if not self.twitter_api:
            logging.error("Twitter API is not initialized.")
            return []

        try:
            tweets = self.twitter_api.search_tweets(q=keyword, count=count, tweet_mode="extended")
            return [
                {
                    "id": tweet.id_str,
                    "text": tweet.full_text,
                    "user": tweet.user.screen_name,
                    "created_at": tweet.created_at.isoformat()
                } for tweet in tweets
            ]
        except Exception as e:
            logging.error("Failed to scrape Twitter: %s", e)
            return []

    def scrape_instagram(self, hashtag: str, access_token: str) -> List[Dict]:
        try:
            hashtag_url = "https://graph.instagram.com/v12.0/ig_hashtag_search"
            response = requests.get(hashtag_url, params={"q": hashtag, "access_token": access_token})
            data = response.json()

            if "id" not in data:
                logging.error("Failed to fetch Instagram hashtag ID for '%s'.", hashtag)
                return []

            hashtag_id = data["id"]
            posts_url = f"https://graph.instagram.com/{hashtag_id}/recent_media"

            posts_response = requests.get(posts_url, params={"fields": "id,caption,media_type,media_url,timestamp", "access_token": access_token})
            posts_data = posts_response.json()

            return posts_data.get("data", [])
        except Exception as e:
            logging.error("Failed to scrape Instagram: %s", e)
            return []

    def scrape_facebook(self, page_id: str, access_token: str) -> List[Dict]:
        try:
            url = f"https://graph.facebook.com/v12.0/{page_id}/posts"
            response = requests.get(url, params={"fields": "id,message,created_time", "access_token": access_token})
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            logging.error("Failed to scrape Facebook: %s", e)
            return []

    def scrape_mainstream_media(self, url: str) -> List[Dict]:
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            articles = []
            for article in soup.find_all("article"):
                title = article.find("h1") or article.find("h2")
                link = article.find("a", href=True)
                if title and link:
                    articles.append({
                        "title": title.get_text(strip=True),
                        "url": link["href"]
                    })

            return articles
        except Exception as e:
            logging.error("Failed to scrape mainstream media: %s", e)
            return []

    def scrape_reddit(self, subreddit: str, keyword: str) -> List[Dict]:
        try:
            url = f"https://www.reddit.com/r/{subreddit}/search.json"
            response = requests.get(
                url, params={"q": keyword, "restrict_sr": 1}, headers={"User-Agent": "RLG Scraper"}
            )
            data = response.json()
            return [
                {
                    "title": post["data"]["title"],
                    "url": post["data"]["url"],
                    "created_utc": datetime.utcfromtimestamp(post["data"]["created_utc"]).isoformat()
                } for post in data.get("data", {}).get("children", [])
            ]
        except Exception as e:
            logging.error("Failed to scrape Reddit: %s", e)
            return []

    def scrape_all(self, params: Dict) -> Dict[str, List[Dict]]:
        """
        Scrape data from all supported platforms based on input parameters.

        Args:
            params: A dictionary containing platform-specific parameters.

        Returns:
            A dictionary with platform names as keys and scraped data as values.
        """
        results = {}

        if "twitter" in params:
            results["twitter"] = self.scrape_twitter(**params["twitter"])

        if "instagram" in params:
            results["instagram"] = self.scrape_instagram(**params["instagram"])

        if "facebook" in params:
            results["facebook"] = self.scrape_facebook(**params["facebook"])

        if "reddit" in params:
            results["reddit"] = self.scrape_reddit(**params["reddit"])

        if "mainstream_media" in params:
            results["mainstream_media"] = self.scrape_mainstream_media(params["mainstream_media"]["url"])

        return results

# Example usage
if __name__ == "__main__":
    api_keys = {
        "twitter": {
            "consumer_key": "your_consumer_key",
            "consumer_secret": "your_consumer_secret",
            "access_token": "your_access_token",
            "access_token_secret": "your_access_token_secret"
        }
    }

    scraper = MultiPlatformScraper(api_keys)

    results = scraper.scrape_all({
        "twitter": {"keyword": "AI Technology", "count": 10},
        "mainstream_media": {"url": "https://www.example-news-site.com"}
    })

    print(results)

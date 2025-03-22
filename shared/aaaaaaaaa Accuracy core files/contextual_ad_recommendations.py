import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("ad_recommendations.log"), logging.StreamHandler()]
)

class ContextualAdRecommendations:
    """
    AI-powered contextual ad recommendation system for RLG Data & RLG Fans.
    Uses natural language processing (NLP) to analyze content and recommend ads dynamically.
    """

    def __init__(self, api_keys: Dict[str, str]):
        """
        Initialize the contextual ad recommendation system.

        Args:
            api_keys (Dict[str, str]): API keys for ad platforms (Google, Facebook, TikTok, etc.).
        """
        self.api_keys = api_keys
        self.ad_platforms = ["google", "facebook", "instagram", "twitter", "tiktok", "linkedin"]
        self.ad_data = {}

    def fetch_ad_inventory(self, platform: str, category: Optional[str] = None) -> List[Dict]:
        """
        Fetch ad inventory from an advertising platform.

        Args:
            platform (str): The advertising platform name (e.g., "google", "facebook").
            category (Optional[str]): The category of ads to fetch.

        Returns:
            List[Dict]: Available ads with metadata.
        """
        logging.info(f"Fetching ad inventory for {platform} in category {category or 'all'}...")

        if platform == "google":
            return self.fetch_google_ads(category)
        elif platform == "facebook":
            return self.fetch_facebook_ads(category)
        elif platform == "tiktok":
            return self.fetch_tiktok_ads(category)
        else:
            logging.warning(f"Ad data for {platform} is not yet implemented.")
            return []

    def fetch_google_ads(self, category: Optional[str]) -> List[Dict]:
        """
        Fetch ads from Google Ads.

        Args:
            category (Optional[str]): The category of ads to fetch.

        Returns:
            List[Dict]: Available Google Ads.
        """
        url = "https://googleads.googleapis.com/v10/customers/{customer_id}/ads"
        headers = {"Authorization": f"Bearer {self.api_keys['google']}"}
        params = {"category": category} if category else {}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            ads = response.json()["ads"]
            logging.info(f"Fetched {len(ads)} Google Ads for category {category or 'all'}.")
            return [{"title": ad["headline"], "description": ad["description"], "clicks": ad["click_through_rate"]} for ad in ads]
        except Exception as e:
            logging.error(f"Failed to fetch Google Ads: {e}")
            return []

    def fetch_facebook_ads(self, category: Optional[str]) -> List[Dict]:
        """
        Fetch ads from Facebook Ads.

        Args:
            category (Optional[str]): The category of ads to fetch.

        Returns:
            List[Dict]: Available Facebook Ads.
        """
        url = "https://graph.facebook.com/v18.0/act_{account_id}/ads"
        headers = {"Authorization": f"Bearer {self.api_keys['facebook']}"}
        params = {"fields": "name,adset,clicks", "category": category} if category else {}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            ads = response.json()["data"]
            logging.info(f"Fetched {len(ads)} Facebook Ads for category {category or 'all'}.")
            return [{"title": ad["name"], "description": ad.get("adset", "No description"), "clicks": ad["clicks"]} for ad in ads]
        except Exception as e:
            logging.error(f"Failed to fetch Facebook Ads: {e}")
            return []

    def fetch_tiktok_ads(self, category: Optional[str]) -> List[Dict]:
        """
        Fetch ads from TikTok Ads.

        Args:
            category (Optional[str]): The category of ads to fetch.

        Returns:
            List[Dict]: Available TikTok Ads.
        """
        url = "https://business-api.tiktok.com/open_api/v1.2/ad/info/"
        headers = {"Authorization": f"Bearer {self.api_keys['tiktok']}"}
        params = {"category": category} if category else {}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            ads = response.json()["data"]["list"]
            logging.info(f"Fetched {len(ads)} TikTok Ads for category {category or 'all'}.")
            return [{"title": ad["ad_name"], "description": ad.get("ad_text", "No description"), "clicks": ad["clicks"]} for ad in ads]
        except Exception as e:
            logging.error(f"Failed to fetch TikTok Ads: {e}")
            return []

    def analyze_content(self, content: str) -> str:
        """
        Perform sentiment analysis on user content.

        Args:
            content (str): The content to analyze.

        Returns:
            str: "Positive", "Neutral", or "Negative"
        """
        analysis = TextBlob(content).sentiment.polarity
        if analysis > 0:
            return "Positive"
        elif analysis < 0:
            return "Negative"
        return "Neutral"

    def recommend_ads(self, user_content: str, location: str) -> List[Dict]:
        """
        Recommend contextual ads based on user content and location.

        Args:
            user_content (str): The content a user is engaging with.
            location (str): The user's location for region-based ad optimization.

        Returns:
            List[Dict]: Recommended ads.
        """
        logging.info(f"Generating ad recommendations for {location}...")
        recommended_ads = []

        for platform in self.ad_platforms:
            ads = self.fetch_ad_inventory(platform)
            if not ads:
                continue

            # Text similarity analysis
            ad_texts = [ad["title"] + " " + ad["description"] for ad in ads]
            vectorizer = TfidfVectorizer(stop_words="english")
            ad_vectors = vectorizer.fit_transform(ad_texts + [user_content])
            similarity_scores = cosine_similarity(ad_vectors[-1], ad_vectors[:-1]).flatten()

            top_ads = sorted(zip(ads, similarity_scores), key=lambda x: x[1], reverse=True)[:5]

            for ad, score in top_ads:
                recommended_ads.append({
                    "platform": platform,
                    "title": ad["title"],
                    "description": ad["description"],
                    "clicks": ad["clicks"],
                    "match_score": round(score * 100, 2),
                    "sentiment": self.analyze_content(ad["description"])
                })

        return recommended_ads

# Example Usage
if __name__ == "__main__":
    api_keys = {
        "google": "your-google-api-key",
        "facebook": "your-facebook-api-key",
        "tiktok": "your-tiktok-api-key"
    }

    ad_recommender = ContextualAdRecommendations(api_keys)
    user_text = "I'm looking for the best smartphones under $1000."
    recommendations = ad_recommender.recommend_ads(user_text, "south africa")

    print(json.dumps(recommendations, indent=4))

# unlocked_service.py - Service for interacting with Unlocked platform

import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime

class UnlockedService:
    """
    Service for interacting with Unlocked, providing functionalities for scraping
    creator metrics, tracking trending content, and generating growth recommendations.
    """
    BASE_URL = "https://unlocked.com"

    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.logger = logging.getLogger("UnlockedService")

    def fetch_creator_metrics(self, creator_username):
        """
        Fetches creator metrics from Unlocked, such as follower count, likes, and total posts.
        """
        profile_url = f"{self.BASE_URL}/{creator_username}"
        try:
            response = self.session.get(profile_url)
            response.raise_for_status()
            return self.parse_creator_metrics(response.text)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching metrics for {creator_username}: {e}")
            return None

    def parse_creator_metrics(self, html_content):
        """
        Parses the HTML content of an Unlocked profile page to extract key metrics.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        metrics = {
            "follower_count": self.extract_follower_count(soup),
            "likes": self.extract_likes(soup),
            "post_count": self.extract_post_count(soup),
            "engagement_rate": self.calculate_engagement_rate(soup)
        }
        self.logger.info(f"Parsed creator metrics: {metrics}")
        return metrics

    def extract_follower_count(self, soup):
        """
        Extracts the follower count from the profile page.
        """
        follower_tag = soup.find("span", class_="followers-count")
        return int(follower_tag.text.replace(",", "")) if follower_tag else 0

    def extract_likes(self, soup):
        """
        Extracts the total number of likes from the profile page.
        """
        likes_tag = soup.find("span", class_="likes-count")
        return int(likes_tag.text.replace(",", "")) if likes_tag else 0

    def extract_post_count(self, soup):
        """
        Extracts the total number of posts from the profile page.
        """
        posts_tag = soup.find("span", class_="posts-count")
        return int(posts_tag.text.replace(",", "")) if posts_tag else 0

    def calculate_engagement_rate(self, soup):
        """
        Calculates the engagement rate based on likes and follower count.
        """
        follower_count = self.extract_follower_count(soup)
        likes = self.extract_likes(soup)
        return round((likes / follower_count) * 100, 2) if follower_count > 0 else 0.0

    def fetch_trending_content(self):
        """
        Fetches trending content from Unlocked to identify popular content and topics.
        """
        trending_url = f"{self.BASE_URL}/trending"
        try:
            response = self.session.get(trending_url)
            response.raise_for_status()
            return self.parse_trending_content(response.text)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching trending content: {e}")
            return []

    def parse_trending_content(self, html_content):
        """
        Parses trending content data from HTML, extracting title, likes, and posted date.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        trending_content = []
        for content in soup.find_all("div", class_="trending-item"):
            content_data = {
                "title": content.find("h3", class_="content-title").text.strip(),
                "likes": int(content.find("span", class_="content-likes").text.replace(",", "")),
                "posted_date": content.find("span", class_="content-date").text.strip()
            }
            trending_content.append(content_data)
        return trending_content

    def generate_growth_recommendations(self, metrics):
        """
        Generates growth recommendations based on the creator's current metrics.
        """
        recommendations = []

        if metrics["follower_count"] < 500:
            recommendations.append("Consider exclusive content offers to attract more followers.")
        if metrics["likes"] < 1000:
            recommendations.append("Engage with your audience via live Q&A to increase likes.")
        if metrics["engagement_rate"] < 8.0:
            recommendations.append("Use polls and interactive content to boost engagement rate.")

        self.logger.info(f"Generated recommendations: {recommendations}")
        return recommendations

    def log_metrics(self, metrics):
        """
        Logs creator metrics for tracking growth and performance over time.
        """
        metrics_log = {
            "follower_count": metrics["follower_count"],
            "likes": metrics["likes"],
            "post_count": metrics["post_count"],
            "engagement_rate": metrics["engagement_rate"],
            "timestamp": datetime.utcnow()
        }
        self.logger.info(f"Logged metrics: {metrics_log}")
        return metrics_log

# End of unlocked_service.py

# flirtback_service.py - Service to interact with the Flirtback platform and gather analytics

import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime

class FlirtbackService:
    """
    Service for interacting with Flirtback to gather content metrics, analyze trends,
    and provide recommendations to enhance creators' engagement and visibility.
    """
    BASE_URL = "https://flirtback.com"

    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.logger = logging.getLogger("FlirtbackService")

    def fetch_creator_metrics(self, username):
        """
        Fetches metrics for a creator on Flirtback, including followers, likes, and engagement rate.
        """
        profile_url = f"{self.BASE_URL}/user/{username}"
        try:
            response = self.session.get(profile_url)
            response.raise_for_status()
            return self.parse_creator_metrics(response.text)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching metrics for {username}: {e}")
            return None

    def parse_creator_metrics(self, html_content):
        """
        Parse creator metrics including follower count, likes, and engagement stats.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        metrics = {
            "follower_count": self.extract_follower_count(soup),
            "like_count": self.extract_like_count(soup),
            "engagement_rate": self.calculate_engagement_rate(soup)
        }
        self.logger.info(f"Parsed creator metrics: {metrics}")
        return metrics

    def extract_follower_count(self, soup):
        """
        Extract follower count from creator's profile page.
        """
        follower_tag = soup.find("span", class_="follower-count")
        return int(follower_tag.text.replace(",", "")) if follower_tag else 0

    def extract_like_count(self, soup):
        """
        Extract total like count from creator's profile page.
        """
        like_tag = soup.find("span", class_="like-count")
        return int(like_tag.text.replace(",", "")) if like_tag else 0

    def calculate_engagement_rate(self, soup):
        """
        Calculate engagement rate based on likes and followers.
        """
        likes = self.extract_like_count(soup)
        followers = self.extract_follower_count(soup)
        return round((likes / followers) * 100, 2) if followers > 0 else 0.0

    def fetch_trending_content(self):
        """
        Fetch trending content on Flirtback to analyze popular content themes.
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
        Parse trending content to retrieve titles, likes, comments, and other metrics.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        trending_content = []
        for content in soup.find_all("div", class_="trending-item"):
            content_data = {
                "title": content.find("h2", class_="content-title").text.strip(),
                "likes": int(content.find("span", class_="content-likes").text.replace(",", "")),
                "comments": int(content.find("span", class_="content-comments").text.replace(",", "")),
                "views": int(content.find("span", class_="content-views").text.replace(",", "")),
                "posted_date": content.find("span", class_="content-date").text.strip()
            }
            trending_content.append(content_data)
        return trending_content

    def generate_content_recommendations(self, metrics):
        """
        Generate actionable recommendations for creators based on their performance metrics.
        """
        recommendations = []
        
        if metrics["follower_count"] < 1000:
            recommendations.append("Consider engaging with your followers through live streams and interactive content.")
        if metrics["engagement_rate"] < 5.0:
            recommendations.append("Increase engagement by responding to comments and holding Q&A sessions.")
        
        self.logger.info(f"Generated recommendations: {recommendations}")
        return recommendations

    def log_metrics(self, metrics):
        """
        Log metrics for tracking performance over time, including follower count and engagement.
        """
        metrics_log = {
            "follower_count": metrics["follower_count"],
            "like_count": metrics["like_count"],
            "engagement_rate": metrics["engagement_rate"],
            "timestamp": datetime.utcnow()
        }
        self.logger.info(f"Logged metrics: {metrics_log}")
        return metrics_log

# End of flirtback_service.py

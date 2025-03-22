# justforfans_service.py - Service for interacting with the JustForFans platform

import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime

class JustForFansService:
    """
    Service for interacting with JustForFans to gather metrics, track trends,
    and generate recommendations to improve creators' performance and monetization.
    """
    BASE_URL = "https://justfor.fans"

    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.logger = logging.getLogger("JustForFansService")

    def fetch_creator_metrics(self, username):
        """
        Fetches a creator's key metrics on JustForFans, such as followers, likes, and posts.
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
        Parse creator metrics, including follower count, like count, post count, and engagement rate.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        metrics = {
            "follower_count": self.extract_follower_count(soup),
            "like_count": self.extract_like_count(soup),
            "post_count": self.extract_post_count(soup),
            "engagement_rate": self.calculate_engagement_rate(soup)
        }
        self.logger.info(f"Parsed creator metrics: {metrics}")
        return metrics

    def extract_follower_count(self, soup):
        """
        Extract follower count from the creator's profile page.
        """
        follower_tag = soup.find("span", class_="follower-count")
        return int(follower_tag.text.replace(",", "")) if follower_tag else 0

    def extract_like_count(self, soup):
        """
        Extract like count from the creator's profile page.
        """
        like_tag = soup.find("span", class_="like-count")
        return int(like_tag.text.replace(",", "")) if like_tag else 0

    def extract_post_count(self, soup):
        """
        Extract the number of posts from the creator's profile page.
        """
        post_tag = soup.find("span", class_="post-count")
        return int(post_tag.text.replace(",", "")) if post_tag else 0

    def calculate_engagement_rate(self, soup):
        """
        Calculate engagement rate based on likes and followers.
        """
        likes = self.extract_like_count(soup)
        followers = self.extract_follower_count(soup)
        return round((likes / followers) * 100, 2) if followers > 0 else 0.0

    def fetch_trending_content(self):
        """
        Fetch trending content on JustForFans to identify popular content types and themes.
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
        Parse trending content to retrieve titles, likes, comments, and views.
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
        Generate recommendations based on a creator's metrics to enhance engagement and monetization.
        """
        recommendations = []
        
        if metrics["follower_count"] < 1000:
            recommendations.append("Boost follower engagement by offering exclusive content or live Q&A sessions.")
        if metrics["engagement_rate"] < 5.0:
            recommendations.append("Increase engagement with polls, stories, and behind-the-scenes content.")
        
        self.logger.info(f"Generated recommendations: {recommendations}")
        return recommendations

    def log_metrics(self, metrics):
        """
        Log metrics for tracking performance over time, including follower count and engagement.
        """
        metrics_log = {
            "follower_count": metrics["follower_count"],
            "like_count": metrics["like_count"],
            "post_count": metrics["post_count"],
            "engagement_rate": metrics["engagement_rate"],
            "timestamp": datetime.utcnow()
        }
        self.logger.info(f"Logged metrics: {metrics_log}")
        return metrics_log

# End of justforfans_service.py

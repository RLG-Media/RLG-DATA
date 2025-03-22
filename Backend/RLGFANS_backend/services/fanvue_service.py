# fanvue_service.py - Service to interact with the Fanvue platform and gather analytics

import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime

class FanvueService:
    """
    Service for interacting with Fanvue, providing profile metrics, trending content analysis,
    and content strategy recommendations to enhance creators' visibility and engagement.
    """
    BASE_URL = "https://fanvue.com"

    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.logger = logging.getLogger("FanvueService")

    def fetch_profile_metrics(self, username):
        """
        Fetch profile metrics for a creator on Fanvue, such as follower count, engagement rate,
        and subscription growth.
        """
        profile_url = f"{self.BASE_URL}/user/{username}"
        try:
            response = self.session.get(profile_url)
            response.raise_for_status()
            return self.parse_profile_metrics(response.text)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching profile metrics for {username}: {e}")
            return None

    def parse_profile_metrics(self, html_content):
        """
        Parse profile metrics, including follower count, engagement rate, and recent posts' performance.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        profile_metrics = {
            "follower_count": self.extract_follower_count(soup),
            "engagement_rate": self.extract_engagement_rate(soup),
            "recent_posts": self.extract_recent_posts(soup)
        }
        self.logger.info(f"Parsed profile metrics: {profile_metrics}")
        return profile_metrics

    def extract_follower_count(self, soup):
        """
        Extract follower count from the profile page.
        """
        follower_tag = soup.find("span", class_="follower-count")
        return int(follower_tag.text.replace(",", "")) if follower_tag else 0

    def extract_engagement_rate(self, soup):
        """
        Extract engagement rate from the profile page.
        """
        engagement_tag = soup.find("span", class_="engagement-rate")
        return float(engagement_tag.text.strip('%')) if engagement_tag else 0.0

    def extract_recent_posts(self, soup):
        """
        Extract recent posts' performance data, including likes, comments, and post date.
        """
        posts = []
        for post in soup.find_all("div", class_="post-item"):
            post_data = {
                "title": post.find("h3", class_="post-title").text.strip(),
                "likes": int(post.find("span", class_="post-likes").text.replace(",", "")),
                "comments": int(post.find("span", class_="post-comments").text.replace(",", "")),
                "date": post.find("span", class_="post-date").text.strip()
            }
            posts.append(post_data)
        return posts

    def fetch_trending_content(self):
        """
        Fetch trending content on Fanvue, providing insights on popular content themes and metrics.
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
        Parse trending content, including metrics like views, likes, and comments.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        trending_content = []
        for content in soup.find_all("div", class_="content-item"):
            content_data = {
                "title": content.find("h2", class_="content-title").text.strip(),
                "views": int(content.find("span", class_="content-views").text.replace(",", "")),
                "likes": int(content.find("span", class_="content-likes").text.replace(",", "")),
                "comments": int(content.find("span", class_="content-comments").text.replace(",", "")),
                "posted_date": content.find("span", class_="content-date").text.strip()
            }
            trending_content.append(content_data)
        return trending_content

    def generate_content_recommendations(self, metrics):
        """
        Generate recommendations based on profile metrics to improve engagement and follower growth.
        """
        recommendations = []
        
        if metrics["follower_count"] < 500:
            recommendations.append("Run a follower drive or offer incentives to new subscribers.")
        if metrics["engagement_rate"] < 2.5:
            recommendations.append("Increase engagement by posting interactive content.")
        
        self.logger.info(f"Generated recommendations: {recommendations}")
        return recommendations

    def log_metrics(self, metrics):
        """
        Log key metrics for tracking creator performance over time, such as follower count and engagement.
        """
        metrics_log = {
            "follower_count": metrics["follower_count"],
            "engagement_rate": metrics["engagement_rate"],
            "timestamp": datetime.utcnow()
        }
        self.logger.info(f"Logged metrics: {metrics_log}")
        return metrics_log

# End of fanvue_service.py

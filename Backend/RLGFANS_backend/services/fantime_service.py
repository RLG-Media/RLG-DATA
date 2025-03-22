# fantime_service.py - Service to interact with the Fantime platform and gather analytics

import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime

class FantimeService:
    """
    Service to interact with Fantime platform, providing data on profile metrics, content
    engagement, and recommendations to help creators enhance their visibility and monetization.
    """
    BASE_URL = "https://fantime.com"

    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.logger = logging.getLogger("FantimeService")

    def fetch_profile_metrics(self, username):
        """
        Fetch profile metrics for a creator on Fantime, including follower count, engagement rate,
        and subscription growth rate.
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
        Parse profile metrics including follower count, engagement rate, subscription rate,
        and recent posts' performance.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        profile_metrics = {
            "follower_count": self.extract_follower_count(soup),
            "engagement_rate": self.extract_engagement_rate(soup),
            "subscription_rate": self.extract_subscription_rate(soup),
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

    def extract_subscription_rate(self, soup):
        """
        Extract subscription growth rate data for the creator.
        """
        subscription_tag = soup.find("span", class_="subscription-rate")
        return subscription_tag.text.strip() if subscription_tag else "Not available"

    def extract_recent_posts(self, soup):
        """
        Extract recent posts' performance data including likes, comments, and post date.
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
        Fetch trending content data on Fantime, providing insights on popular content themes.
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
        Parse trending content details, including popularity metrics like views, likes, and comments.
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
        Generate recommendations based on profile metrics, focusing on engagement improvement
        and subscription growth.
        """
        recommendations = []
        
        if metrics["follower_count"] < 1000:
            recommendations.append("Consider running exclusive promotions to increase followers.")
        if metrics["engagement_rate"] < 3.0:
            recommendations.append("Use interactive posts to boost engagement.")
        if metrics["subscription_rate"] == "Not available":
            recommendations.append("Focus on subscription-based content to improve monetization.")

        self.logger.info(f"Generated recommendations: {recommendations}")
        return recommendations

    def log_metrics(self, metrics):
        """
        Log profile metrics for performance tracking, such as follower count, engagement rate, and
        subscription growth rate.
        """
        metrics_log = {
            "follower_count": metrics["follower_count"],
            "engagement_rate": metrics["engagement_rate"],
            "subscription_rate": metrics["subscription_rate"],
            "timestamp": datetime.utcnow()
        }
        self.logger.info(f"Logged metrics: {metrics_log}")
        return metrics_log

# End of fantime_service.py

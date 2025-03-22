# fansmetrics_service.py - Service to handle data retrieval and analysis for FansMetrics

import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime

class FansMetricsService:
    """
    Service to interact with FansMetrics data for tracking performance metrics
    and engagement analytics. Provides insights and recommendations to help creators
    and brands optimize content.
    """
    BASE_URL = "https://fansmetrics.com"

    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.logger = logging.getLogger("FansMetricsService")

    def fetch_profile_metrics(self, username):
        """
        Fetch performance metrics for a specific creator from FansMetrics.
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
        Parse profile metrics including follower count, engagement rate, revenue estimation,
        and recent content performance.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        profile_metrics = {
            "follower_count": self.extract_follower_count(soup),
            "engagement_rate": self.extract_engagement_rate(soup),
            "estimated_revenue": self.extract_estimated_revenue(soup),
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

    def extract_estimated_revenue(self, soup):
        """
        Extract estimated revenue data from the profile page.
        """
        revenue_tag = soup.find("span", class_="estimated-revenue")
        return revenue_tag.text.strip() if revenue_tag else "Not available"

    def extract_recent_posts(self, soup):
        """
        Extract recent posts performance data including likes, comments, and date posted.
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

    def fetch_trending_creators(self):
        """
        Fetch data on trending creators from FansMetrics to analyze popular content strategies.
        """
        trending_url = f"{self.BASE_URL}/trending"
        try:
            response = self.session.get(trending_url)
            response.raise_for_status()
            return self.parse_trending_creators(response.text)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching trending creators: {e}")
            return []

    def parse_trending_creators(self, html_content):
        """
        Parse the data of trending creators, highlighting their engagement and content strategies.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        trending_creators = []
        for creator in soup.find_all("div", class_="creator-item"):
            creator_data = {
                "username": creator.find("h2", class_="creator-username").text.strip(),
                "follower_count": int(creator.find("span", class_="creator-followers").text.replace(",", "")),
                "engagement_rate": float(creator.find("span", class_="creator-engagement").text.strip('%')),
                "profile_url": creator.find("a", class_="creator-link")["href"]
            }
            trending_creators.append(creator_data)
        return trending_creators

    def generate_recommendations(self, metrics):
        """
        Generate recommendations for content and engagement optimization based on metrics.
        """
        recommendations = []

        if metrics["follower_count"] < 1000:
            recommendations.append("Focus on follower growth strategies such as shoutouts and collaborations.")
        if metrics["engagement_rate"] < 2.0:
            recommendations.append("Increase interactive content and engage with followers to boost engagement.")

        self.logger.info(f"Generated recommendations: {recommendations}")
        return recommendations

    def log_metrics(self, metrics):
        """
        Log metrics such as engagement rate, follower count, and estimated revenue for performance tracking.
        """
        metrics_log = {
            "follower_count": metrics["follower_count"],
            "engagement_rate": metrics["engagement_rate"],
            "estimated_revenue": metrics["estimated_revenue"],
            "timestamp": datetime.utcnow()
        }
        self.logger.info(f"Logged metrics: {metrics_log}")
        return metrics_log

# End of fansmetrics_service.py

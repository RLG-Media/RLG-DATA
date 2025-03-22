# okfans_services.py - Service for interacting with OkFans

import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime

class OkFansService:
    """
    Service to interact with OkFans, providing data scraping for metrics,
    tracking trending content, and generating recommendations for creators.
    """
    BASE_URL = "https://www.okfans.com"

    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.logger = logging.getLogger("OkFansService")

    def fetch_creator_metrics(self, username):
        """
        Fetch key metrics for a creator on OkFans, such as subscriber count,
        post count, and view metrics.
        """
        profile_url = f"{self.BASE_URL}/{username}"
        try:
            response = self.session.get(profile_url)
            response.raise_for_status()
            return self.parse_creator_metrics(response.text)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching metrics for {username}: {e}")
            return None

    def parse_creator_metrics(self, html_content):
        """
        Parses the HTML content of an OkFans profile page to extract metrics.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        metrics = {
            "subscriber_count": self.extract_subscriber_count(soup),
            "post_count": self.extract_post_count(soup),
            "view_count": self.extract_view_count(soup),
            "engagement_rate": self.calculate_engagement_rate(soup)
        }
        self.logger.info(f"Parsed creator metrics: {metrics}")
        return metrics

    def extract_subscriber_count(self, soup):
        """
        Extract the subscriber count from the profile page.
        """
        subscriber_tag = soup.find("span", class_="subscriber-count")
        return int(subscriber_tag.text.replace(",", "")) if subscriber_tag else 0

    def extract_post_count(self, soup):
        """
        Extract the number of posts from the profile page.
        """
        post_tag = soup.find("span", class_="post-count")
        return int(post_tag.text.replace(",", "")) if post_tag else 0

    def extract_view_count(self, soup):
        """
        Extract the view count from the profile page.
        """
        view_tag = soup.find("span", class_="view-count")
        return int(view_tag.text.replace(",", "")) if view_tag else 0

    def calculate_engagement_rate(self, soup):
        """
        Calculate engagement rate based on views and subscribers.
        """
        views = self.extract_view_count(soup)
        subscribers = self.extract_subscriber_count(soup)
        return round((views / subscribers) * 100, 2) if subscribers > 0 else 0.0

    def fetch_trending_content(self):
        """
        Fetch trending content on OkFans, identifying popular post types and engagement.
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
        Parse trending content to retrieve data such as title, likes, and views.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        trending_content = []
        for content in soup.find_all("div", class_="trending-item"):
            content_data = {
                "title": content.find("h2", class_="content-title").text.strip(),
                "likes": int(content.find("span", class_="content-likes").text.replace(",", "")),
                "views": int(content.find("span", class_="content-views").text.replace(",", "")),
                "posted_date": content.find("span", class_="content-date").text.strip()
            }
            trending_content.append(content_data)
        return trending_content

    def generate_content_recommendations(self, metrics):
        """
        Generate content recommendations based on the creator's metrics to boost
        engagement and monetization.
        """
        recommendations = []

        if metrics["subscriber_count"] < 1000:
            recommendations.append("Promote exclusive offers to attract more subscribers.")
        if metrics["engagement_rate"] < 10.0:
            recommendations.append("Try engaging with followers via live sessions to improve engagement.")
        
        self.logger.info(f"Generated recommendations: {recommendations}")
        return recommendations

    def log_metrics(self, metrics):
        """
        Log creator metrics for performance tracking over time, such as subscribers,
        post count, views, and engagement rate.
        """
        metrics_log = {
            "subscriber_count": metrics["subscriber_count"],
            "post_count": metrics["post_count"],
            "view_count": metrics["view_count"],
            "engagement_rate": metrics["engagement_rate"],
            "timestamp": datetime.utcnow()
        }
        self.logger.info(f"Logged metrics: {metrics_log}")
        return metrics_log

# End of okfans_services.py

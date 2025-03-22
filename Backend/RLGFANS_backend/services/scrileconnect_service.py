# scrileconnect_service.py - Service for interacting with Scrile Connect

import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime

class ScrileConnectService:
    """
    Service to interact with Scrile Connect, providing data scraping for creator metrics,
    tracking trending content, and generating growth strategies tailored for creators.
    """
    BASE_URL = "https://scrileconnect.com"

    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.logger = logging.getLogger("ScrileConnectService")

    def fetch_creator_metrics(self, creator_username):
        """
        Fetches key metrics for a creator on Scrile Connect, including follower count,
        subscription earnings, and content engagement rates.
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
        Parses the HTML content of a Scrile Connect profile page to extract key metrics.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        metrics = {
            "follower_count": self.extract_follower_count(soup),
            "monthly_earnings": self.extract_monthly_earnings(soup),
            "post_count": self.extract_post_count(soup),
            "engagement_rate": self.calculate_engagement_rate(soup)
        }
        self.logger.info(f"Parsed creator metrics: {metrics}")
        return metrics

    def extract_follower_count(self, soup):
        """
        Extract the number of followers from the profile page.
        """
        follower_tag = soup.find("span", class_="follower-count")
        return int(follower_tag.text.replace(",", "")) if follower_tag else 0

    def extract_monthly_earnings(self, soup):
        """
        Extract the monthly earnings from the profile page.
        """
        earnings_tag = soup.find("span", class_="earnings-amount")
        if earnings_tag:
            earnings = earnings_tag.text.replace("$", "").replace(",", "")
            return int(earnings)
        return 0

    def extract_post_count(self, soup):
        """
        Extract the total number of posts from the profile page.
        """
        post_tag = soup.find("span", class_="post-count")
        return int(post_tag.text.replace(",", "")) if post_tag else 0

    def calculate_engagement_rate(self, soup):
        """
        Calculate the engagement rate based on likes, comments, and follower count.
        """
        follower_count = self.extract_follower_count(soup)
        engagement_tag = soup.find("span", class_="engagement-metric")
        engagement_count = int(engagement_tag.text.replace(",", "")) if engagement_tag else 0
        return round((engagement_count / follower_count) * 100, 2) if follower_count > 0 else 0.0

    def fetch_trending_content(self):
        """
        Scrapes trending content on Scrile Connect to identify popular post types and topics.
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
        Parses HTML to retrieve trending content data such as titles, likes, and comments.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        trending_content = []
        for content in soup.find_all("div", class_="trending-item"):
            content_data = {
                "title": content.find("h3", class_="content-title").text.strip(),
                "likes": int(content.find("span", class_="content-likes").text.replace(",", "")),
                "comments": int(content.find("span", class_="content-comments").text.replace(",", "")),
                "posted_date": content.find("span", class_="content-date").text.strip()
            }
            trending_content.append(content_data)
        return trending_content

    def generate_growth_recommendations(self, metrics):
        """
        Generates growth and monetization recommendations based on the creator's metrics.
        """
        recommendations = []

        if metrics["follower_count"] < 500:
            recommendations.append("Consider collaborations to grow your follower base.")
        if metrics["monthly_earnings"] < 3000:
            recommendations.append("Add exclusive content tiers to increase earnings.")
        if metrics["engagement_rate"] < 10.0:
            recommendations.append("Use interactive posts to boost engagement rates.")

        self.logger.info(f"Generated recommendations: {recommendations}")
        return recommendations

    def log_metrics(self, metrics):
        """
        Logs creator metrics for performance tracking over time, including followers,
        monthly earnings, post count, and engagement rate.
        """
        metrics_log = {
            "follower_count": metrics["follower_count"],
            "monthly_earnings": metrics["monthly_earnings"],
            "post_count": metrics["post_count"],
            "engagement_rate": metrics["engagement_rate"],
            "timestamp": datetime.utcnow()
        }
        self.logger.info(f"Logged metrics: {metrics_log}")
        return metrics_log

# End of scrileconnect_service.py

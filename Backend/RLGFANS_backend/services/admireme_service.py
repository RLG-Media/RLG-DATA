# admireme_service.py - Service to handle AdmireMe.VIP interactions

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging

class AdmireMeService:
    """
    Service for scraping, tracking, and analyzing data on AdmireMe.VIP.
    Provides insights on content trends, engagement metrics, and monetization opportunities.
    """
    BASE_URL = "https://admireme.vip"

    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.logger = logging.getLogger("AdmireMeService")
    
    def fetch_profile_data(self, username):
        """
        Fetch profile information for a specific AdmireMe creator.
        """
        profile_url = f"{self.BASE_URL}/{username}"
        try:
            response = self.session.get(profile_url)
            response.raise_for_status()
            return self.parse_profile_data(response.text)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching profile data for {username}: {e}")
            return None

    def parse_profile_data(self, html_content):
        """
        Parse profile data, including followers, likes, and engagement metrics.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        profile_data = {
            "follower_count": self.extract_follower_count(soup),
            "total_likes": self.extract_total_likes(soup),
            "posts": self.extract_posts(soup),
            "profile_url": soup.find("link", rel="canonical")["href"]
        }
        self.logger.info(f"Parsed profile data: {profile_data}")
        return profile_data

    def extract_follower_count(self, soup):
        """
        Extract follower count from profile page.
        """
        follower_tag = soup.find("span", class_="follower-count")
        return int(follower_tag.text.replace(",", "")) if follower_tag else 0

    def extract_total_likes(self, soup):
        """
        Extract total likes count from profile page.
        """
        likes_tag = soup.find("span", class_="likes-count")
        return int(likes_tag.text.replace(",", "")) if likes_tag else 0

    def extract_posts(self, soup):
        """
        Extract list of posts, including title, likes, and comments.
        """
        posts = []
        for post in soup.find_all("div", class_="post-card"):
            post_data = {
                "title": post.find("h2", class_="post-title").text.strip(),
                "likes": int(post.find("span", class_="post-likes").text.strip().replace(",", "")),
                "comments": int(post.find("span", class_="post-comments").text.strip().replace(",", "")),
                "date": post.find("span", class_="post-date").text.strip()
            }
            posts.append(post_data)
        return posts

    def fetch_trending_content(self):
        """
        Fetch trending content on AdmireMe.VIP, extracting posts with high engagement.
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
        Parse trending content data from the trending page.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        trending_posts = []
        for post in soup.find_all("div", class_="trending-post"):
            post_data = {
                "title": post.find("h2", class_="post-title").text.strip(),
                "likes": int(post.find("span", class_="post-likes").text.strip().replace(",", "")),
                "comments": int(post.find("span", class_="post-comments").text.strip().replace(",", "")),
                "url": post.find("a", class_="post-link")["href"]
            }
            trending_posts.append(post_data)
        return trending_posts

    def generate_recommendations(self, profile_data):
        """
        Generate content recommendations for AdmireMe based on engagement metrics.
        """
        recommendations = []
        
        if profile_data["follower_count"] < 500:
            recommendations.append("Increase follower engagement through daily posts and interactive content.")
        if profile_data["total_likes"] < 1000:
            recommendations.append("Consider collaborations with other creators to boost likes and visibility.")
        
        self.logger.info(f"Generated recommendations: {recommendations}")
        return recommendations

    def log_metrics(self, profile_data):
        """
        Log key metrics like followers, total likes, and engagement for analysis and reporting.
        """
        metrics_log = {
            "follower_count": profile_data["follower_count"],
            "total_likes": profile_data["total_likes"],
            "engagement_rate": self.calculate_engagement(profile_data),
            "timestamp": datetime.utcnow()
        }
        self.logger.info(f"Logged metrics: {metrics_log}")
        return metrics_log

    def calculate_engagement(self, profile_data):
        """
        Calculate engagement rate based on likes and follower count.
        """
        total_likes = profile_data.get("total_likes", 0)
        follower_count = profile_data.get("follower_count", 1)  # Avoid division by zero
        engagement_rate = (total_likes / follower_count) * 100
        return round(engagement_rate, 2)

# End of admireme_service.py

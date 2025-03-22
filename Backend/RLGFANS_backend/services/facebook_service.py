# facebook_service.py

import os
import requests
from datetime import datetime, timedelta

# Set up environment variables for access tokens
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
FACEBOOK_GRAPH_API_URL = "https://graph.facebook.com/v12.0"

class FacebookService:
    """
    Service for interacting with the Facebook Graph API to retrieve page insights, engagement metrics,
    and content analysis.
    """

    @staticmethod
    def get_page_insights(page_id):
        """
        Retrieves insights for a Facebook page, including metrics like page views, likes, and reach.

        :param page_id: The Facebook page ID.
        :return: A dictionary with key insights data.
        """
        try:
            url = f"{FACEBOOK_GRAPH_API_URL}/{page_id}/insights"
            params = {
                "metric": "page_views_total,page_fan_adds_unique,page_impressions_unique",
                "access_token": FACEBOOK_ACCESS_TOKEN
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            insights_data = response.json()

            insights = {
                "views": insights_data['data'][0].get('values', [])[0].get('value', 0),
                "new_likes": insights_data['data'][1].get('values', [])[0].get('value', 0),
                "reach": insights_data['data'][2].get('values', [])[0].get('value', 0)
            }
            return insights
        except requests.RequestException as e:
            print(f"Error retrieving page insights: {e}")
            return {}

    @staticmethod
    def get_post_engagement(post_id):
        """
        Fetches engagement metrics for a specific post, such as reactions, comments, and shares.

        :param post_id: The ID of the Facebook post.
        :return: A dictionary with engagement metrics.
        """
        try:
            url = f"{FACEBOOK_GRAPH_API_URL}/{post_id}/insights"
            params = {
                "metric": "post_engaged_users,post_reactions_by_type_total,post_comments,post_shares",
                "access_token": FACEBOOK_ACCESS_TOKEN
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            engagement_data = response.json()

            engagement = {
                "engaged_users": engagement_data['data'][0].get('values', [])[0].get('value', 0),
                "reactions": engagement_data['data'][1].get('values', [])[0].get('value', {}),
                "comments": engagement_data['data'][2].get('values', [])[0].get('value', 0),
                "shares": engagement_data['data'][3].get('values', [])[0].get('value', 0)
            }
            return engagement
        except requests.RequestException as e:
            print(f"Error retrieving post engagement: {e}")
            return {}

    @staticmethod
    def get_recent_posts(page_id, since_days=30):
        """
        Retrieves recent posts from a Facebook page within a specified number of days.

        :param page_id: The Facebook page ID.
        :param since_days: The number of days to look back for recent posts (default is 30).
        :return: A list of recent posts with basic details.
        """
        since_date = (datetime.now() - timedelta(days=since_days)).isoformat()
        try:
            url = f"{FACEBOOK_GRAPH_API_URL}/{page_id}/posts"
            params = {
                "fields": "id,message,created_time,permalink_url",
                "since": since_date,
                "access_token": FACEBOOK_ACCESS_TOKEN
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            posts_data = response.json()

            posts = [
                {
                    "id": post['id'],
                    "message": post.get('message', ''),
                    "created_time": post['created_time'],
                    "url": post['permalink_url']
                }
                for post in posts_data.get('data', [])
            ]
            return posts
        except requests.RequestException as e:
            print(f"Error retrieving recent posts: {e}")
            return []

    @staticmethod
    def analyze_content_strategy(page_id):
        """
        Analyzes content strategy based on recent post performance and engagement metrics.

        :param page_id: The Facebook page ID.
        :return: Dictionary containing content strategy recommendations.
        """
        try:
            recent_posts = FacebookService.get_recent_posts(page_id, since_days=30)
            total_engagements = 0
            high_engagement_posts = []

            # Collect engagement data for each post
            for post in recent_posts:
                engagement = FacebookService.get_post_engagement(post["id"])
                post_engagement = engagement.get("engaged_users", 0)
                total_engagements += post_engagement

                # Identify high-engagement posts for strategy recommendations
                if post_engagement > 100:
                    high_engagement_posts.append({
                        "post_id": post["id"],
                        "message": post.get("message", ""),
                        "engaged_users": post_engagement,
                        "url": post["url"]
                    })

            average_engagement = total_engagements / len(recent_posts) if recent_posts else 0

            # Generate recommendations based on post performance
            recommendations = {
                "average_engagement": average_engagement,
                "high_engagement_posts": high_engagement_posts,
                "strategy": []
            }

            if average_engagement < 50:
                recommendations["strategy"].append("Increase the frequency of interactive content, such as polls or Q&As.")
            if len(high_engagement_posts) < 3:
                recommendations["strategy"].append("Experiment with posting at different times to increase reach.")
            recommendations["strategy"].append("Consider boosting high-engagement posts to reach a larger audience.")

            return recommendations

        except Exception as e:
            print(f"Error analyzing content strategy: {e}")
            return {}

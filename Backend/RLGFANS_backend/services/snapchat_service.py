# snapchat_service.py

import os
import requests
from datetime import datetime, timedelta

# Load environment variables
SNAPCHAT_ACCESS_TOKEN = os.getenv("SNAPCHAT_ACCESS_TOKEN")
SNAPCHAT_API_URL = "https://adsapi.snapchat.com/v1"

class SnapchatService:
    """
    Service for interacting with Snapchat's Marketing API to retrieve user insights, content engagement,
    and to provide strategic recommendations for creators and brands on Snapchat.
    """

    @staticmethod
    def get_account_metrics(account_id):
        """
        Retrieves key account metrics, such as total impressions, unique views, and engagement rate.

        :param account_id: Snapchat account ID.
        :return: Dictionary containing account metrics.
        """
        try:
            url = f"{SNAPCHAT_API_URL}/accounts/{account_id}/insights"
            headers = {"Authorization": f"Bearer {SNAPCHAT_ACCESS_TOKEN}"}
            params = {
                "metrics": "impressions,swipe_ups,engagements",
                "start_time": (datetime.now() - timedelta(days=30)).isoformat(),
                "end_time": datetime.now().isoformat()
            }
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            metrics_data = response.json().get("data", {}).get("metrics", {})

            metrics = {
                "impressions": metrics_data.get("impressions", 0),
                "swipe_ups": metrics_data.get("swipe_ups", 0),
                "engagements": metrics_data.get("engagements", 0)
            }
            metrics["engagement_rate"] = (
                metrics["engagements"] / metrics["impressions"] * 100
                if metrics["impressions"] > 0 else 0
            )
            return metrics
        except requests.RequestException as e:
            print(f"Error fetching account metrics: {e}")
            return {}

    @staticmethod
    def get_recent_stories(account_id, since_days=7):
        """
        Retrieves recent stories posted by the account within a specified timeframe.

        :param account_id: Snapchat account ID.
        :param since_days: Number of days back to retrieve stories (default is 7).
        :return: List of recent stories with engagement data.
        """
        since_date = (datetime.now() - timedelta(days=since_days)).isoformat()
        try:
            url = f"{SNAPCHAT_API_URL}/accounts/{account_id}/media"
            headers = {"Authorization": f"Bearer {SNAPCHAT_ACCESS_TOKEN}"}
            params = {
                "start_time": since_date,
                "end_time": datetime.now().isoformat(),
                "fields": "id,title,impressions,swipe_ups,created_time"
            }
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            stories_data = response.json().get("data", [])

            stories = [
                {
                    "id": story["id"],
                    "title": story.get("title", "Untitled"),
                    "impressions": story.get("impressions", 0),
                    "swipe_ups": story.get("swipe_ups", 0),
                    "created_time": story["created_time"]
                }
                for story in stories_data
            ]
            return stories
        except requests.RequestException as e:
            print(f"Error fetching recent stories: {e}")
            return []

    @staticmethod
    def analyze_content_performance(account_id):
        """
        Analyzes recent story performance to provide insights on engagement and reach effectiveness.

        :param account_id: Snapchat account ID.
        :return: Dictionary containing analysis and recommendations for content strategy.
        """
        try:
            recent_stories = SnapchatService.get_recent_stories(account_id)
            total_impressions = sum(story["impressions"] for story in recent_stories)
            total_swipe_ups = sum(story["swipe_ups"] for story in recent_stories)
            story_count = len(recent_stories)
            
            # Calculate average engagement
            avg_swipe_up_rate = (total_swipe_ups / total_impressions * 100) if total_impressions else 0

            # High-performing stories based on swipe ups
            high_performing_stories = [
                story for story in recent_stories if story["swipe_ups"] > 50
            ]

            recommendations = {
                "average_swipe_up_rate": avg_swipe_up_rate,
                "high_performing_stories": high_performing_stories,
                "strategy": []
            }

            # Provide recommendations based on engagement rates
            if avg_swipe_up_rate < 2:
                recommendations["strategy"].append(
                    "Consider using more engaging story formats, such as polls or interactive quizzes."
                )
            if story_count < 5:
                recommendations["strategy"].append(
                    "Increase posting frequency to maintain audience engagement."
                )
            recommendations["strategy"].append(
                "Experiment with posting at different times to increase story reach."
            )

            return recommendations
        except Exception as e:
            print(f"Error analyzing content performance: {e}")
            return {}

    @staticmethod
    def boost_high_performance_stories(account_id):
        """
        Suggests boosting high-performing stories to increase reach and engagement.

        :param account_id: Snapchat account ID.
        :return: List of story IDs recommended for boosting.
        """
        try:
            high_performance_stories = SnapchatService.analyze_content_performance(account_id)["high_performing_stories"]
            return [story["id"] for story in high_performance_stories]
        except Exception as e:
            print(f"Error in boosting recommendations: {e}")
            return []

# tiktok_service.py

import os
import requests
from datetime import datetime, timedelta

# Environment variables
TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN")
TIKTOK_API_URL = "https://open-api.tiktok.com"

class TikTokService:
    """
    Service for interacting with TikTok's API to retrieve metrics, content insights, and
    provide recommendations for creators to enhance engagement and monetization on TikTok.
    """

    @staticmethod
    def get_user_metrics(user_id):
        """
        Retrieves TikTok user metrics such as follower count, total likes, and average engagement rate.

        :param user_id: TikTok user ID.
        :return: Dictionary containing user metrics.
        """
        try:
            url = f"{TIKTOK_API_URL}/user/{user_id}/metrics"
            headers = {"Authorization": f"Bearer {TIKTOK_ACCESS_TOKEN}"}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            metrics_data = response.json().get("data", {})

            metrics = {
                "followers": metrics_data.get("followers", 0),
                "total_likes": metrics_data.get("total_likes", 0),
                "total_comments": metrics_data.get("total_comments", 0),
                "total_shares": metrics_data.get("total_shares", 0),
            }
            metrics["engagement_rate"] = (
                (metrics["total_likes"] + metrics["total_comments"] + metrics["total_shares"])
                / max(metrics["followers"], 1)
                * 100
            )
            return metrics
        except requests.RequestException as e:
            print(f"Error fetching user metrics: {e}")
            return {}

    @staticmethod
    def get_trending_content(hashtag, limit=5):
        """
        Fetches trending TikTok content for a specific hashtag.

        :param hashtag: Hashtag to search for trending content.
        :param limit: Maximum number of trending videos to retrieve.
        :return: List of trending videos with key metrics.
        """
        try:
            url = f"{TIKTOK_API_URL}/hashtags/{hashtag}/trending"
            headers = {"Authorization": f"Bearer {TIKTOK_ACCESS_TOKEN}"}
            params = {"limit": limit}
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            videos_data = response.json().get("data", [])

            trending_videos = [
                {
                    "video_id": video["id"],
                    "title": video.get("title", "No Title"),
                    "likes": video.get("like_count", 0),
                    "comments": video.get("comment_count", 0),
                    "shares": video.get("share_count", 0),
                    "created_time": video["created_time"]
                }
                for video in videos_data
            ]
            return trending_videos
        except requests.RequestException as e:
            print(f"Error fetching trending content: {e}")
            return []

    @staticmethod
    def analyze_content_performance(user_id):
        """
        Analyzes recent content performance to provide insights on engagement trends.

        :param user_id: TikTok user ID.
        :return: Dictionary containing performance analysis and recommendations.
        """
        try:
            recent_videos = TikTokService.get_user_recent_videos(user_id)
            total_likes = sum(video["like_count"] for video in recent_videos)
            total_comments = sum(video["comment_count"] for video in recent_videos)
            total_shares = sum(video["share_count"] for video in recent_videos)
            video_count = len(recent_videos)

            # Calculate average engagement metrics
            avg_like_count = total_likes / max(video_count, 1)
            avg_comment_count = total_comments / max(video_count, 1)
            avg_share_count = total_shares / max(video_count, 1)

            recommendations = {
                "average_likes": avg_like_count,
                "average_comments": avg_comment_count,
                "average_shares": avg_share_count,
                "strategy": []
            }

            # Provide recommendations based on engagement trends
            if avg_like_count < 100:
                recommendations["strategy"].append(
                    "Consider using trending sounds or effects to increase visibility."
                )
            if avg_comment_count < 10:
                recommendations["strategy"].append(
                    "Engage with your audience by asking questions in captions."
                )
            recommendations["strategy"].append(
                "Optimize posting time to align with peak engagement hours for higher reach."
            )

            return recommendations
        except Exception as e:
            print(f"Error analyzing content performance: {e}")
            return {}

    @staticmethod
    def get_user_recent_videos(user_id, since_days=30):
        """
        Retrieves recent videos posted by the user within a specified timeframe.

        :param user_id: TikTok user ID.
        :param since_days: Number of days back to retrieve videos (default is 30).
        :return: List of recent videos with engagement data.
        """
        since_date = (datetime.now() - timedelta(days=since_days)).isoformat()
        try:
            url = f"{TIKTOK_API_URL}/user/{user_id}/videos"
            headers = {"Authorization": f"Bearer {TIKTOK_ACCESS_TOKEN}"}
            params = {
                "start_time": since_date,
                "end_time": datetime.now().isoformat()
            }
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            videos_data = response.json().get("data", [])

            videos = [
                {
                    "id": video["id"],
                    "like_count": video.get("like_count", 0),
                    "comment_count": video.get("comment_count", 0),
                    "share_count": video.get("share_count", 0),
                    "created_time": video["created_time"]
                }
                for video in videos_data
            ]
            return videos
        except requests.RequestException as e:
            print(f"Error fetching recent videos: {e}")
            return []

    @staticmethod
    def recommend_boosted_content(user_id):
        """
        Suggests recent videos with the highest engagement rates for promotion.

        :param user_id: TikTok user ID.
        :return: List of recommended video IDs for boosting.
        """
        try:
            videos = TikTokService.get_user_recent_videos(user_id)
            boosted_content = [
                video for video in videos if video["like_count"] > 1000
            ]
            return [video["id"] for video in boosted_content]
        except Exception as e:
            print(f"Error in boosting recommendations: {e}")
            return []

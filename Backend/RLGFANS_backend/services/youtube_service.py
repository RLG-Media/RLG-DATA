# youtube_service.py

import os
import requests
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# Initialize the YouTube API client using the API key
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

class YouTubeService:
    """
    Service for interacting with the YouTube API, analyzing trends, engagement, and monetization opportunities.
    """

    @staticmethod
    def get_trending_videos(region_code="US", max_results=10):
        """
        Fetches the top trending videos in a specified region.

        :param region_code: The country code for regional trends (default is "US").
        :param max_results: Maximum number of results to fetch (default is 10).
        :return: List of trending video details.
        """
        try:
            request = youtube.videos().list(
                part="snippet,statistics",
                chart="mostPopular",
                regionCode=region_code,
                maxResults=max_results
            )
            response = request.execute()
            trending_videos = [
                {
                    "title": item['snippet']['title'],
                    "channel": item['snippet']['channelTitle'],
                    "published_at": item['snippet']['publishedAt'],
                    "views": item['statistics'].get('viewCount', 0),
                    "likes": item['statistics'].get('likeCount', 0),
                    "comments": item['statistics'].get('commentCount', 0)
                }
                for item in response.get("items", [])
            ]
            return trending_videos

        except Exception as e:
            print(f"Error fetching trending videos: {e}")
            return []

    @staticmethod
    def search_videos(query, max_results=10):
        """
        Searches for videos based on a specific query.

        :param query: Search term for YouTube.
        :param max_results: Maximum number of results to fetch (default is 10).
        :return: List of video details matching the search term.
        """
        try:
            request = youtube.search().list(
                part="snippet",
                q=query,
                type="video",
                maxResults=max_results
            )
            response = request.execute()
            search_results = [
                {
                    "title": item['snippet']['title'],
                    "channel": item['snippet']['channelTitle'],
                    "published_at": item['snippet']['publishedAt'],
                    "description": item['snippet']['description'],
                    "thumbnail": item['snippet']['thumbnails']['default']['url']
                }
                for item in response.get("items", [])
            ]
            return search_results

        except Exception as e:
            print(f"Error searching for videos: {e}")
            return []

    @staticmethod
    def analyze_channel_performance(channel_id, days=30):
        """
        Analyzes channel performance metrics over a specified number of days.

        :param channel_id: YouTube channel ID.
        :param days: Number of days to analyze (default is 30).
        :return: Dictionary with performance metrics including views, subscribers, and engagement.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        try:
            request = youtube.channels().list(
                part="snippet,statistics",
                id=channel_id
            )
            response = request.execute()
            stats = response['items'][0]['statistics']
            channel_performance = {
                "title": response['items'][0]['snippet']['title'],
                "subscribers": stats.get('subscriberCount', 0),
                "total_views": stats.get('viewCount', 0),
                "total_videos": stats.get('videoCount', 0),
                "engagement_rate": YouTubeService.calculate_engagement(stats)
            }
            return channel_performance

        except Exception as e:
            print(f"Error analyzing channel performance: {e}")
            return {}

    @staticmethod
    def calculate_engagement(stats):
        """
        Calculates engagement rate based on view, like, and comment counts.

        :param stats: Dictionary with statistics data.
        :return: Engagement rate as a percentage.
        """
        try:
            views = int(stats.get('viewCount', 0))
            likes = int(stats.get('likeCount', 0))
            comments = int(stats.get('commentCount', 0))
            engagement = ((likes + comments) / views) * 100 if views > 0 else 0
            return round(engagement, 2)
        except Exception as e:
            print(f"Error calculating engagement rate: {e}")
            return 0

    @staticmethod
    def recommend_content_strategy(channel_id, region_code="US"):
        """
        Recommends content strategy based on trending content and channel performance.

        :param channel_id: YouTube channel ID.
        :param region_code: The region code for fetching trending content.
        :return: Recommendations based on data insights.
        """
        try:
            trending_videos = YouTubeService.get_trending_videos(region_code, max_results=5)
            channel_performance = YouTubeService.analyze_channel_performance(channel_id)

            recommendations = {
                "trending_content_suggestions": trending_videos,
                "channel_performance": channel_performance,
                "strategy": []
            }

            # Suggest types of content and topics based on trends and engagement
            if channel_performance.get("engagement_rate", 0) < 5:
                recommendations["strategy"].append("Increase engagement with Q&A videos or polls.")
            if int(channel_performance.get("total_videos", 0)) < 50:
                recommendations["strategy"].append("Post consistently to grow audience base.")
            if int(channel_performance.get("subscribers", 0)) < 1000:
                recommendations["strategy"].append("Collaborate with similar creators to boost visibility.")

            return recommendations

        except Exception as e:
            print(f"Error creating content strategy recommendations: {e}")
            return {}


# test_data_processing.py - Unit tests for data processing functions in RLG Fans

import unittest
from data_processing import (
    process_trending_content,
    extract_keywords,
    analyze_user_activity,
    process_platform_metrics
)

class TestDataProcessing(unittest.TestCase):

    def setUp(self):
        """
        Set up mock data for testing.
        """
        self.sample_content = [
            {"text": "Love this new feature on OnlyFans! #exclusive", "likes": 120, "comments": 30},
            {"text": "Check out my new video on Patreon!", "likes": 90, "comments": 20},
            {"text": "Here's a behind-the-scenes on my fansly page! #BTS", "likes": 200, "comments": 50},
        ]
        self.sample_keywords = "exclusive, video, BTS"
        self.user_activity_data = [
            {"username": "creator1", "views": 1500, "subscribers": 300, "new_messages": 40},
            {"username": "creator2", "views": 2000, "subscribers": 500, "new_messages": 60},
        ]
        self.platform_metrics = {
            "OnlyFans": {"followers": 1000, "engagement_rate": 2.5},
            "Patreon": {"followers": 500, "engagement_rate": 3.0},
            "Fansly": {"followers": 750, "engagement_rate": 1.8},
        }

    def test_process_trending_content(self):
        """
        Test the processing of trending content data.
        """
        trending_results = process_trending_content(self.sample_content)
        self.assertTrue(trending_results)
        self.assertIsInstance(trending_results, dict)
        self.assertIn("most_liked", trending_results)
        self.assertGreaterEqual(trending_results["most_liked"]["likes"], 90)

    def test_extract_keywords(self):
        """
        Test keyword extraction from given content.
        """
        keywords = extract_keywords(self.sample_content)
        self.assertTrue(keywords)
        self.assertIsInstance(keywords, list)
        self.assertIn("video", keywords)
        self.assertIn("BTS", keywords)

    def test_analyze_user_activity(self):
        """
        Test user activity analysis based on sample data.
        """
        activity_summary = analyze_user_activity(self.user_activity_data)
        self.assertTrue(activity_summary)
        self.assertIsInstance(activity_summary, dict)
        self.assertEqual(activity_summary["total_views"], 3500)
        self.assertEqual(activity_summary["average_messages"], 50)

    def test_process_platform_metrics(self):
        """
        Test platform metrics processing for engagement insights.
        """
        metrics_summary = process_platform_metrics(self.platform_metrics)
        self.assertTrue(metrics_summary)
        self.assertIsInstance(metrics_summary, dict)
        self.assertIn("highest_engagement", metrics_summary)
        self.assertEqual(metrics_summary["highest_engagement"]["platform"], "Patreon")

if __name__ == "__main__":
    unittest.main()

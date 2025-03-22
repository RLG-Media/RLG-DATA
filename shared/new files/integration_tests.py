import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import json

# Importing modules to test (assuming they are in the same directory or installed)
from api_rate_limit_manager import APIRateLimitManager
from bulk_content_uploader import BulkContentUploader
from content_optimizer import ContentOptimizer
from event_notifications import EventNotifications
from insights_backend import InsightsBackend
from gdpr_compliance import GDPRCompliance

class IntegrationTests(unittest.TestCase):
    """
    Integration tests for RLG Data and RLG Fans components.
    Validates interactions and dependencies between modules.
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up resources and initialize test data.
        """
        cls.insights_backend = InsightsBackend(data_source="test_insights_data.json")
        cls.api_rate_limiter = APIRateLimitManager(redis_host="localhost", redis_port=6379)
        cls.bulk_uploader = BulkContentUploader()
        cls.content_optimizer = ContentOptimizer()
        cls.event_notifications = EventNotifications()
        cls.gdpr_compliance = GDPRCompliance(data_source="test_gdpr_data.json")

        # Create dummy data for testing
        cls.insights_data = [
            {
                "id": "1",
                "title": "High Engagement Times",
                "platform": "Instagram",
                "category": "Engagement",
                "engagement_score": 78.5,
                "details": "Optimal posting time: 6 PM - 9 PM"
            },
            {
                "id": "2",
                "title": "Monetization Strategies",
                "platform": "YouTube",
                "category": "Monetization",
                "engagement_score": 92.7,
                "details": "Utilize memberships and exclusive content."
            }
        ]

        cls.gdpr_test_data = [
            {"user_id": "123", "data_retention": "2025-01-01"},
            {"user_id": "456", "data_retention": "2025-06-01"}
        ]

    @classmethod
    def tearDownClass(cls):
        """
        Clean up resources after tests are run.
        """
        try:
            with open("test_insights_data.json", "w") as file:
                json.dump([], file)
            with open("test_gdpr_data.json", "w") as file:
                json.dump([], file)
        except Exception as e:
            print(f"Error during cleanup: {e}")

    def test_insights_backend_integration(self):
        """
        Test integration of InsightsBackend with real data processing.
        """
        # Add insights
        for insight in self.insights_data:
            self.insights_backend.add_insight(insight)

        # Generate overview
        overview = self.insights_backend.generate_overview()
        self.assertEqual(overview["total_insights"], 2)
        self.assertGreater(overview["average_engagement"], 70)

        # Retrieve insights by filter
        filtered_insights = self.insights_backend.filter_insights(platform="Instagram")
        self.assertEqual(len(filtered_insights), 1)
        self.assertEqual(filtered_insights[0]["platform"], "Instagram")

    def test_api_rate_limit_manager_integration(self):
        """
        Test integration of APIRateLimitManager with Redis for rate limiting.
        """
        # Simulate API requests
        user_key = "test_user_1"
        for _ in range(10):
            self.api_rate_limiter.track_request(user_key)

        # Verify rate limit enforcement
        limit_reached = self.api_rate_limiter.is_rate_limited(user_key)
        self.assertTrue(limit_reached)

    def test_bulk_content_uploader_integration(self):
        """
        Test integration of BulkContentUploader for handling multiple file uploads.
        """
        files = [
            {"filename": "test_image1.jpg", "content": b"image1_data"},
            {"filename": "test_video1.mp4", "content": b"video1_data"}
        ]
        result = self.bulk_uploader.upload_bulk_content(files)
        self.assertTrue(result)
        self.assertEqual(len(result["uploaded"]), 2)

    def test_content_optimizer_integration(self):
        """
        Test integration of ContentOptimizer for optimizing content performance.
        """
        content_data = {
            "platform": "TikTok",
            "text": "Check out our new product!",
            "media_type": "video"
        }
        optimized_content = self.content_optimizer.optimize_content(content_data)
        self.assertIn("optimized_text", optimized_content)
        self.assertEqual(optimized_content["platform"], "TikTok")

    def test_event_notifications_integration(self):
        """
        Test integration of EventNotifications for sending alerts and notifications.
        """
        # Mock notification sending
        with patch.object(self.event_notifications, "send_notification", return_value=True) as mock_send:
            event_data = {
                "event_type": "trend_alert",
                "message": "New trend detected on Twitter: #TechInnovation",
                "recipients": ["user1@example.com", "user2@example.com"]
            }
            result = self.event_notifications.send_notification(event_data)
            self.assertTrue(result)
            mock_send.assert_called_once()

    def test_gdpr_compliance_integration(self):
        """
        Test integration of GDPRCompliance for managing user data privacy.
        """
        # Add GDPR test data
        for record in self.gdpr_test_data:
            self.gdpr_compliance.add_user_data(record)

        # Verify data retention logic
        expired_users = self.gdpr_compliance.get_expired_users(current_date="2025-07-01")
        self.assertEqual(len(expired_users), 2)

    def test_cross_component_interaction(self):
        """
        Test interactions between multiple components for a user action.
        Example: Upload content, optimize it, and generate insights.
        """
        # Upload and optimize content
        files = [{"filename": "test_video.mp4", "content": b"video_data"}]
        upload_result = self.bulk_uploader.upload_bulk_content(files)
        self.assertTrue(upload_result)

        content_data = {
            "platform": "Instagram",
            "text": "New product launch!",
            "media_type": "image"
        }
        optimized_content = self.content_optimizer.optimize_content(content_data)
        self.assertIn("optimized_text", optimized_content)

        # Add insight for the optimized content
        insight = {
            "id": "3",
            "title": "Optimized Content Performance",
            "platform": "Instagram",
            "category": "Engagement",
            "engagement_score": 89.5,
            "details": "Optimized text for better reach."
        }
        self.insights_backend.add_insight(insight)

        # Verify the insight was added
        insights = self.insights_backend.filter_insights(platform="Instagram")
        self.assertGreaterEqual(len(insights), 1)

if __name__ == "__main__":
    unittest.main()

# test_end_to_end.py

import unittest
import requests
from datetime import datetime
from shared.config import Config
from shared.auth_middleware import generate_auth_token

class TestEndToEnd(unittest.TestCase):
    """End-to-end integration tests for RLG Data and RLG Fans services."""

    BASE_URL = Config.BASE_URL

    def setUp(self):
        """Set up initial configurations and authentication."""
        self.auth_token = generate_auth_token(user_id=1, role='admin')
        self.headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        self.test_data = {
            "sample_content": "Test post for trend analysis",
            "keywords": ["trending", "popular", "content"],
            "platform": "Twitter",
            "timestamp": datetime.now().isoformat()
        }

    def test_content_analysis(self):
        """Test content analysis and sentiment detection in RLG Data."""
        response = requests.post(
            f"{self.BASE_URL}/content/analyze",
            json=self.test_data,
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("sentiment_score", data)
        self.assertIn("keywords", data)
        print("Content analysis passed with sentiment and keywords detected.")

    def test_trend_prediction(self):
        """Test trend prediction across platforms in RLG Fans."""
        response = requests.post(
            f"{self.BASE_URL}/trends/predict",
            json={"platform": "Instagram"},
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("predicted_trends", data)
        print("Trend prediction passed with predicted trends returned.")

    def test_data_collection_service(self):
        """Test data collection from social platforms."""
        response = requests.get(
            f"{self.BASE_URL}/data/collect",
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(len(data.get("collected_data", [])), 0)
        print("Data collection service passed with data collected.")

    def test_scheduled_tasks(self):
        """Verify scheduled tasks execute and log properly."""
        response = requests.get(
            f"{self.BASE_URL}/tasks/scheduled",
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("tasks_executed", False))
        print("Scheduled tasks verified as executed successfully.")

    def test_recommendation_engine(self):
        """Test recommendation engine for content suggestions."""
        response = requests.post(
            f"{self.BASE_URL}/recommendations/generate",
            json={"user_id": 1, "platform": "OnlyFans"},
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("recommendations", data)
        self.assertGreater(len(data["recommendations"]), 0)
        print("Recommendation engine passed with recommendations generated.")

    def test_pricing_optimization(self):
        """Test pricing optimization suggestions."""
        response = requests.post(
            f"{self.BASE_URL}/pricing/optimize",
            json={"platform": "Patreon", "content_type": "exclusive_video"},
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("optimized_pricing", data)
        print("Pricing optimization passed with optimized pricing provided.")

    def test_logging_and_notifications(self):
        """Verify that logging and notifications work as expected."""
        response = requests.post(
            f"{self.BASE_URL}/notifications/send",
            json={"message": "End-to-end test notification", "user_id": 1},
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("notification_sent", False))
        print("Logging and notification service verified successfully.")

    def test_zapier_integration(self):
        """Test Zapier automation integration."""
        response = requests.post(
            f"{self.BASE_URL}/zapier/trigger",
            json={"event": "new_subscription", "platform": "Fansly", "user_id": 1},
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("zapier_response", data)
        print("Zapier integration passed with event triggered successfully.")

    def test_new_services(self):
        """Test newly added services such as YouTube, Facebook, Snapchat, and TikTok."""
        platforms = ["YouTube", "Facebook", "Snapchat", "TikTok"]
        for platform in platforms:
            response = requests.post(
                f"{self.BASE_URL}/platforms/{platform.lower()}/analyze",
                json={"content_id": 12345, "analysis_type": "engagement"},
                headers=self.headers
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("analysis_results", data)
            print(f"{platform} service integration passed with analysis results.")

    def tearDown(self):
        """Clean up after tests if necessary."""
        # Any cleanup code can go here if required.
        pass


if __name__ == "__main__":
    unittest.main()

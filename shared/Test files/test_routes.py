import unittest
from app import create_app
from flask import url_for
from unittest.mock import patch

class TestRoutes(unittest.TestCase):
    def setUp(self):
        """Set up test client for testing routes."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    @patch('app.routes.fetch_mentions')
    def test_mentions_route(self, mock_fetch_mentions):
        """Test mentions route for RLG Data."""
        mock_fetch_mentions.return_value = [
            {"platform": "Twitter", "mentions": 100},
            {"platform": "Instagram", "mentions": 120},
            {"platform": "YouTube", "mentions": 80},
        ]
        response = self.client.get(url_for('routes.get_mentions'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"platform": "Twitter"', response.data)
        self.assertIn(b'"mentions": 100', response.data)

    @patch('app.routes.fetch_fans_mentions')
    def test_fans_mentions_route(self, mock_fetch_fans_mentions):
        """Test mentions route for RLG Fans."""
        mock_fetch_fans_mentions.return_value = [
            {"platform": "OnlyFans", "mentions": 80},
            {"platform": "Fansly", "mentions": 60},
            {"platform": "Sheer", "mentions": 40},
        ]
        response = self.client.get(url_for('routes.get_fans_mentions'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"platform": "OnlyFans"', response.data)
        self.assertIn(b'"mentions": 80', response.data)

    @patch('app.routes.fetch_sentiment')
    def test_sentiment_route(self, mock_fetch_sentiment):
        """Test sentiment analysis route for RLG Data."""
        mock_fetch_sentiment.return_value = {
            "positive": 50,
            "neutral": 30,
            "negative": 20
        }
        response = self.client.get(url_for('routes.get_sentiment'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"positive": 50', response.data)

    @patch('app.routes.fetch_fans_sentiment')
    def test_fans_sentiment_route(self, mock_fetch_fans_sentiment):
        """Test sentiment analysis route for RLG Fans."""
        mock_fetch_fans_sentiment.return_value = {
            "positive": 45,
            "neutral": 35,
            "negative": 20
        }
        response = self.client.get(url_for('routes.get_fans_sentiment'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"positive": 45', response.data)

    @patch('app.routes.fetch_engagement')
    def test_engagement_route(self, mock_fetch_engagement):
        """Test engagement data route for RLG Data."""
        mock_fetch_engagement.return_value = [
            {"week": "Week 1", "engagement_rate": 25},
            {"week": "Week 2", "engagement_rate": 30}
        ]
        response = self.client.get(url_for('routes.get_engagement'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"week": "Week 1"', response.data)

    @patch('app.routes.fetch_fans_engagement')
    def test_fans_engagement_route(self, mock_fetch_fans_engagement):
        """Test engagement data route for RLG Fans."""
        mock_fetch_fans_engagement.return_value = [
            {"week": "Week 1", "engagement_rate": 20},
            {"week": "Week 2", "engagement_rate": 28}
        ]
        response = self.client.get(url_for('routes.get_fans_engagement'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"engagement_rate": 20', response.data)

    @patch('app.routes.fetch_trending_content')
    def test_trending_content_route(self, mock_fetch_trending_content):
        """Test trending content route for RLG Data."""
        mock_fetch_trending_content.return_value = [
            {"content": "Trending Post 1", "engagement": 1500},
            {"content": "Trending Post 2", "engagement": 1200}
        ]
        response = self.client.get(url_for('routes.get_trending_content'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"content": "Trending Post 1"', response.data)

    @patch('app.routes.fetch_fans_trending_content')
    def test_fans_trending_content_route(self, mock_fetch_fans_trending_content):
        """Test trending content route for RLG Fans."""
        mock_fetch_fans_trending_content.return_value = [
            {"content": "Exclusive Fans Post 1", "engagement": 500},
            {"content": "Exclusive Fans Post 2", "engagement": 400}
        ]
        response = self.client.get(url_for('routes.get_fans_trending_content'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"content": "Exclusive Fans Post 1"', response.data)

    def test_dashboard_route(self):
        """Test access to the main dashboard page."""
        response = self.client.get(url_for('routes.dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)

    def test_service_overview_route(self):
        """Test access to the service overview page."""
        response = self.client.get(url_for('routes.service_overview'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Service Overview', response.data)

if __name__ == "__main__":
    unittest.main()

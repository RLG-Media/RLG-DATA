import unittest
from unittest.mock import patch, MagicMock
from flask import url_for, jsonify
from app import create_app, db
from routes import routes_blueprint
from flask_jwt_extended import create_access_token

class TestRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Setup Flask app and register blueprint for testing
        cls.app = create_app()
        cls.app.register_blueprint(routes_blueprint)
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()

        # Initialize database for testing
        with cls.app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        # Drop database tables after tests
        with cls.app.app_context():
            db.drop_all()

    def setUp(self):
        self.headers = {"Authorization": f"Bearer {self.get_token()}"}

    def get_token(self):
        """Helper function to create a JWT token for authorization."""
        with self.app.app_context():
            return create_access_token(identity="test_user")

    @patch('invite.send_invite')
    def test_invite_send(self, mock_send_invite):
        # Mock successful invitation sending
        mock_send_invite.return_value = jsonify(message="Invite sent successfully")
        response = self.client.post('/invite/send', json={
            'email': 'test@example.com',
            'role': 'user'
        }, headers=self.headers)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Invite sent successfully", response.get_data(as_text=True))

    @patch('onlyfans_services.OnlyFansService.get_user_data')
    def test_fetch_onlyfans_data(self, mock_get_user_data):
        mock_get_user_data.return_value = {
            "username": "test_user",
            "followers_count": 1000
        }
        response = self.client.get('/onlyfans/fetch/test_user', headers=self.headers)

        self.assertEqual(response.status_code, 200)
        self.assertIn("test_user", response.get_data(as_text=True))

    @patch('discord_services.DiscordService.send_message')
    def test_send_discord_message(self, mock_send_message):
        mock_send_message.return_value = True
        response = self.client.post('/discord/message', json={
            'channel_id': '12345',
            'message': 'Hello, Discord!'
        }, headers=self.headers)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Message sent to Discord successfully", response.get_data(as_text=True))

    @patch('reddit_services.RedditService.search_subreddit')
    def test_search_reddit(self, mock_search_subreddit):
        mock_search_subreddit.return_value = [{"title": "Test Post", "score": 100}]
        response = self.client.get('/reddit/search', query_string={
            'subreddit': 'testsub',
            'query': 'test'
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn("Test Post", response.get_data(as_text=True))

    @patch('google_trends_services.GoogleTrendsService.get_trending_searches')
    def test_google_trends_trending(self, mock_get_trending_searches):
        mock_get_trending_searches.return_value = [{"title": "Trending Topic"}]
        response = self.client.get('/google-trends/trending', query_string={
            'country': 'united_states'
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn("Trending Topic", response.get_data(as_text=True))

    @patch('facebook_services.FacebookService.get_page_insights')
    def test_fetch_facebook_page_insights(self, mock_get_page_insights):
        mock_get_page_insights.return_value = {"likes": 1500}
        response = self.client.get('/facebook/page-insights', query_string={
            'page_id': '12345'
        }, headers=self.headers)

        self.assertEqual(response.status_code, 200)
        self.assertIn("likes", response.get_data(as_text=True))

    @patch('instagram_services.InstagramService.get_profile')
    def test_fetch_instagram_profile(self, mock_get_profile):
        mock_get_profile.return_value = {"username": "test_insta"}
        response = self.client.get('/instagram/profile', query_string={
            'profile_id': 'test_insta'
        }, headers=self.headers)

        self.assertEqual(response.status_code, 200)
        self.assertIn("test_insta", response.get_data(as_text=True))

if __name__ == "__main__":
    unittest.main()

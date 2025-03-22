# test_routes.py - Unit tests for RLG Fans API routes

import unittest
from app import app, db
from flask_jwt_extended import create_access_token
from models import User, Subscription

class TestRoutes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Set up the test client and database before running tests.
        """
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # Use in-memory DB for testing
        cls.client = app.test_client()
        with app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        """
        Clean up database after tests are completed.
        """
        with app.app_context():
            db.drop_all()

    def setUp(self):
        """
        Create a sample user and subscription data for testing.
        """
        with app.app_context():
            user = User(username="testuser", email="testuser@example.com")
            user.set_password("testpassword")
            db.session.add(user)
            db.session.commit()
            self.user = user
            self.access_token = create_access_token(identity=user.id)

    def test_subscribe_user(self):
        """
        Test subscribing a user to a premium plan.
        """
        response = self.client.post(
            "/api/subscribe",
            json={"price_id": "price_premium"},
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("subscription_id", response.json)

    def test_cancel_subscription(self):
        """
        Test canceling a user subscription.
        """
        # Ensure user is subscribed first
        with app.app_context():
            subscription = Subscription(user_id=self.user.id, status="active", plan="premium")
            db.session.add(subscription)
            db.session.commit()

        response = self.client.delete(
            "/api/cancel_subscription",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("subscription_status", response.json)
        self.assertEqual(response.json["subscription_status"], "canceled")

    def test_fetch_trending_content(self):
        """
        Test retrieving trending content across supported platforms.
        """
        response = self.client.get(
            "/api/trending_content",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("trending", response.json)

    def test_scrape_content(self):
        """
        Test content scraping functionality for specified URLs.
        """
        response = self.client.post(
            "/api/scrape_content",
            json={"url": "https://example.com/content"},
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        self.assertEqual(response.status_code, 202)  # Accepted for processing
        self.assertIn("message", response.json)

    def test_get_subscription_status(self):
        """
        Test checking the user's current subscription status.
        """
        with app.app_context():
            subscription = Subscription(user_id=self.user.id, status="active", plan="premium")
            db.session.add(subscription)
            db.session.commit()

        response = self.client.get(
            "/api/subscription_status",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.json)
        self.assertEqual(response.json["status"], "active")

if __name__ == "__main__":
    unittest.main()

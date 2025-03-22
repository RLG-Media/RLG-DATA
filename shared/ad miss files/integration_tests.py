"""
integration_test.py
Comprehensive integration testing for RLG Data and RLG Fans.
Covers API endpoints, service integrations, database interactions, and overall system workflows.
"""

import unittest
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Constants for the testing environment
BASE_URL_DATA = "http://localhost:8000/rlg-data/api"
BASE_URL_FANS = "http://localhost:8000/rlg-fans/api"
DATABASE_URL = "postgresql://test_user:test_password@localhost:5432/test_db"

# Setup the database session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

class TestIntegration(unittest.TestCase):
    """
    Integration tests for RLG Data and RLG Fans.
    """

    @classmethod
    def setUpClass(cls):
        """
        Runs before all tests. Set up any shared resources.
        """
        cls.test_user = {
            "username": "testuser",
            "password": "Test@1234",
            "email": "testuser@example.com",
        }
        cls.auth_headers = {}

    def test_1_user_registration(self):
        """
        Test user registration for both RLG Data and RLG Fans.
        """
        for base_url in [BASE_URL_DATA, BASE_URL_FANS]:
            response = requests.post(
                f"{base_url}/register",
                json=self.test_user,
            )
            self.assertEqual(response.status_code, 201)
            self.assertIn("message", response.json())
            self.assertEqual(response.json()["message"], "User registered successfully.")

    def test_2_user_login(self):
        """
        Test user login for both RLG Data and RLG Fans.
        """
        for base_url in [BASE_URL_DATA, BASE_URL_FANS]:
            response = requests.post(
                f"{base_url}/login",
                json={
                    "username": self.test_user["username"],
                    "password": self.test_user["password"],
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn("token", response.json())
            self.auth_headers[base_url] = {
                "Authorization": f"Bearer {response.json()['token']}"
            }

    def test_3_data_retrieval(self):
        """
        Test data retrieval endpoints for RLG Data and RLG Fans.
        """
        for base_url in [BASE_URL_DATA, BASE_URL_FANS]:
            response = requests.get(
                f"{base_url}/data",
                headers=self.auth_headers[base_url],
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn("data", response.json())

    def test_4_service_integration(self):
        """
        Test external service integrations (e.g., social media, analytics).
        """
        endpoints = [
            "social-media/insights",
            "analytics/recommendations",
            "content/scheduler",
        ]
        for base_url in [BASE_URL_DATA, BASE_URL_FANS]:
            for endpoint in endpoints:
                response = requests.get(
                    f"{base_url}/{endpoint}",
                    headers=self.auth_headers[base_url],
                )
                self.assertEqual(response.status_code, 200)
                self.assertIn("status", response.json())
                self.assertEqual(response.json()["status"], "success")

    def test_5_database_integration(self):
        """
        Test database interactions and data consistency.
        """
        # Check if the test user exists in the database
        user_query = session.execute(
            "SELECT * FROM users WHERE username = :username",
            {"username": self.test_user["username"]},
        )
        user = user_query.fetchone()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, self.test_user["email"])

    def test_6_error_handling(self):
        """
        Test error handling for invalid requests.
        """
        for base_url in [BASE_URL_DATA, BASE_URL_FANS]:
            response = requests.post(
                f"{base_url}/login",
                json={
                    "username": self.test_user["username"],
                    "password": "WrongPassword",
                },
            )
            self.assertEqual(response.status_code, 401)
            self.assertIn("error", response.json())
            self.assertEqual(response.json()["error"], "Invalid credentials.")

    @classmethod
    def tearDownClass(cls):
        """
        Runs after all tests. Clean up any resources.
        """
        # Delete test user from database
        session.execute(
            "DELETE FROM users WHERE username = :username",
            {"username": cls.test_user["username"]},
        )
        session.commit()
        session.close()

if __name__ == "__main__":
    unittest.main()

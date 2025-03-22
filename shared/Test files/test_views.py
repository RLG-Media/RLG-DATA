import unittest
from app import create_app
from flask import json

class TestViews(unittest.TestCase):
    """
    Test cases for the views and endpoints in the RLG Data and RLG Fans application.
    
    These tests cover:
      - The home page
      - The dashboard
      - Service-related pages (e.g., facebook, instagram, youtube, tiktok)
      - 404 error handling for non-existent routes
      - Search endpoint (POST)
      - Data export endpoint
      - Error-handling routes
      - Authentication-required pages (redirects to login)
      - Signup and login form submissions
    """

    @classmethod
    def setUpClass(cls):
        """Set up resources before running tests: initialize the app and test client."""
        cls.app = create_app(config_name="testing")  # Use a dedicated testing configuration
        cls.client = cls.app.test_client()

    def test_home_page(self):
        """Test that the home page loads successfully and contains expected content."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome to RLG DATA", response.data)

    def test_dashboard_page(self):
        """Test that the dashboard page loads successfully and contains 'Dashboard' text."""
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Dashboard", response.data)

    def test_service_pages(self):
        """Test that various service pages load successfully and include the service name."""
        services = ["facebook", "instagram", "youtube", "tiktok"]
        for service in services:
            with self.subTest(service=service):
                response = self.client.get(f"/services/{service}")
                self.assertEqual(response.status_code, 200)
                self.assertIn(service.encode(), response.data)

    def test_404_error(self):
        """Test that a non-existent route returns a 404 error with 'Page Not Found' message."""
        response = self.client.get("/nonexistent")
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Page Not Found", response.data)

    def test_search_endpoint(self):
        """Test the search endpoint using a POST request with JSON data."""
        response = self.client.post(
            "/search",
            data=json.dumps({"query": "test"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn("results", response_data)
        self.assertIsInstance(response_data["results"], list)

    def test_api_data_export(self):
        """Test the data export endpoint to ensure it returns JSON data with the key 'export_data'."""
        response = self.client.get("/export")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        response_data = json.loads(response.data)
        self.assertIn("export_data", response_data)

    def test_error_handling(self):
        """Test that a route specifically designed to trigger an error behaves as expected."""
        with self.assertRaises(Exception):
            self.client.get("/trigger-error")  # Assumes that this route raises an Exception

    def test_auth_required_pages(self):
        """Test that pages requiring authentication redirect to the login page."""
        auth_pages = ["/settings", "/profile", "/admin"]
        for page in auth_pages:
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertEqual(response.status_code, 302)  # Should redirect to login
                self.assertIn("/login", response.headers.get("Location", ""))

    def test_signup_post(self):
        """Test the signup endpoint with form submission and verify success response."""
        response = self.client.post(
            "/signup",
            data={"username": "testuser", "password": "testpass"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Signup successful", response.data)

    def test_login_post(self):
        """Test the login endpoint with form submission and verify success response."""
        response = self.client.post(
            "/login",
            data={"username": "testuser", "password": "testpass"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Login successful", response.data)

    @classmethod
    def tearDownClass(cls):
        """Clean up any resources after tests are run (if needed)."""
        pass  # Add teardown logic as required

if __name__ == "__main__":
    unittest.main()

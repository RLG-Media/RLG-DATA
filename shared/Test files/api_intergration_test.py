import unittest
import requests
from unittest.mock import patch, Mock

BASE_URL = "http://localhost:5000/api"

class APIIntegrationTest(unittest.TestCase):
    """Test suite for API integration in RLG DATA and RLG FANS."""

    def setUp(self):
        """Set up common test configurations."""
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer mock_token"
        }
        self.sample_payload = {
            "user_id": "test_user",
            "service": "analytics",
            "action": "fetch_data"
        }

    @patch('requests.get')
    def test_get_user_profile(self, mock_get):
        """Test retrieving user profile information."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": {"user_id": "test_user", "name": "John Doe"}}
        mock_get.return_value = mock_response

        response = requests.get(f"{BASE_URL}/user/profile", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("success", response.json()["status"])
        self.assertEqual(response.json()["data"]["user_id"], "test_user")

    @patch('requests.post')
    def test_fetch_analytics_data(self, mock_post):
        """Test fetching analytics data for RLG DATA."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": {"views": 1200, "likes": 300}}
        mock_post.return_value = mock_response

        response = requests.post(f"{BASE_URL}/data/analytics", json=self.sample_payload, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("success", response.json()["status"])
        self.assertIn("views", response.json()["data"])

    @patch('requests.post')
    def test_create_fan_post(self, mock_post):
        """Test creating a fan-specific post for RLG FANS."""
        payload = {
            "user_id": "test_user",
            "content": "Exclusive content for my fans!",
            "platform": "fansly"
        }
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"status": "success", "message": "Post created successfully."}
        mock_post.return_value = mock_response

        response = requests.post(f"{BASE_URL}/fans/posts", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 201)
        self.assertIn("success", response.json()["status"])
        self.assertIn("Post created successfully", response.json()["message"])

    @patch('requests.get')
    def test_handle_404_error(self, mock_get):
        """Test handling a 404 Not Found error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"status": "error", "message": "Resource not found"}
        mock_get.return_value = mock_response

        response = requests.get(f"{BASE_URL}/nonexistent/endpoint", headers=self.headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json()["status"])
        self.assertIn("Resource not found", response.json()["message"])

    @patch('requests.post')
    def test_handle_unauthorized_access(self, mock_post):
        """Test handling unauthorized access error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"status": "error", "message": "Unauthorized access"}
        mock_post.return_value = mock_response

        response = requests.post(f"{BASE_URL}/data/analytics", json=self.sample_payload, headers={"Authorization": "Invalid token"})
        self.assertEqual(response.status_code, 401)
        self.assertIn("error", response.json()["status"])
        self.assertIn("Unauthorized access", response.json()["message"])

    @patch('requests.delete')
    def test_delete_user_data(self, mock_delete):
        """Test deleting user data."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "message": "User data deleted successfully"}
        mock_delete.return_value = mock_response

        response = requests.delete(f"{BASE_URL}/user/data", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("success", response.json()["status"])
        self.assertIn("User data deleted successfully", response.json()["message"])

    def tearDown(self):
        """Clean up resources after each test."""
        pass


if __name__ == "__main__":
    unittest.main()

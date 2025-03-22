import unittest
from unittest.mock import patch, MagicMock
from fanfix_services import FanfixService

class TestFanfixService(unittest.TestCase):
    def setUp(self):
        # Initialize FanfixService with a mock access token
        self.service = FanfixService(access_token="test_token")

    @patch('fanfix_services.requests.get')
    def test_get_profile_success(self, mock_get):
        # Mock a successful response from the Fanfix API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "username": "test_user",
            "followers": 1200,
            "posts": 45
        }
        mock_get.return_value = mock_response

        profile = self.service.get_profile("test_user")

        # Assert the response contains expected data
        self.assertEqual(profile['username'], "test_user")
        self.assertEqual(profile['followers'], 1200)
        self.assertEqual(profile['posts'], 45)
        mock_get.assert_called_once_with(
            'https://api.fanfix.io/user/test_user',
            headers={'Authorization': 'Bearer test_token'}
        )

    @patch('fanfix_services.requests.get')
    def test_get_profile_not_found(self, mock_get):
        # Mock a 404 Not Found response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        profile = self.service.get_profile("nonexistent_user")

        # Assert that None is returned for a nonexistent profile
        self.assertIsNone(profile)
        mock_get.assert_called_once_with(
            'https://api.fanfix.io/user/nonexistent_user',
            headers={'Authorization': 'Bearer test_token'}
        )

    @patch('fanfix_services.requests.get')
    def test_get_profile_error(self, mock_get):
        # Mock a 500 Internal Server Error response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        profile = self.service.get_profile("test_user")

        # Assert that None is returned on error
        self.assertIsNone(profile)
        mock_get.assert_called_once_with(
            'https://api.fanfix.io/user/test_user',
            headers={'Authorization': 'Bearer test_token'}
        )

    @patch('fanfix_services.requests.get')
    def test_get_posts_success(self, mock_get):
        # Mock a successful response with posts data
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "1", "content": "First post", "likes": 100},
            {"id": "2", "content": "Second post", "likes": 150}
        ]
        mock_get.return_value = mock_response

        posts = self.service.get_posts("test_user")

        # Check response contents
        self.assertEqual(len(posts), 2)
        self.assertEqual(posts[0]["content"], "First post")
        self.assertEqual(posts[1]["likes"], 150)
        mock_get.assert_called_once_with(
            'https://api.fanfix.io/user/test_user/posts',
            headers={'Authorization': 'Bearer test_token'}
        )

    @patch('fanfix_services.requests.get')
    def test_get_posts_no_posts(self, mock_get):
        # Mock a 200 response with an empty post list
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        posts = self.service.get_posts("test_user")

        # Assert that an empty list is returned when there are no posts
        self.assertEqual(posts, [])
        mock_get.assert_called_once_with(
            'https://api.fanfix.io/user/test_user/posts',
            headers={'Authorization': 'Bearer test_token'}
        )

if __name__ == "__main__":
    unittest.main()

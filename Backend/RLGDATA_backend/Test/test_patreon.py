import unittest
from unittest.mock import patch, MagicMock
from patreon_services import PatreonService

class TestPatreonService(unittest.TestCase):
    def setUp(self):
        # Initialize PatreonService with a mock access token
        self.service = PatreonService(access_token="test_token")

    @patch('patreon_services.requests.get')
    def test_get_creator_profile_success(self, mock_get):
        # Mock a successful response from the Patreon API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "id": "12345",
                "attributes": {
                    "full_name": "Test Creator",
                    "followers_count": 5000,
                    "patron_count": 200
                }
            }
        }
        mock_get.return_value = mock_response

        profile = self.service.get_creator_profile("test_creator")

        # Assert that response contains expected data
        self.assertEqual(profile["full_name"], "Test Creator")
        self.assertEqual(profile["followers_count"], 5000)
        self.assertEqual(profile["patron_count"], 200)
        mock_get.assert_called_once_with(
            'https://www.patreon.com/api/creator/test_creator',
            headers={'Authorization': 'Bearer test_token'}
        )

    @patch('patreon_services.requests.get')
    def test_get_creator_profile_not_found(self, mock_get):
        # Mock a 404 Not Found response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        profile = self.service.get_creator_profile("nonexistent_creator")

        # Assert that None is returned for a nonexistent profile
        self.assertIsNone(profile)
        mock_get.assert_called_once_with(
            'https://www.patreon.com/api/creator/nonexistent_creator',
            headers={'Authorization': 'Bearer test_token'}
        )

    @patch('patreon_services.requests.get')
    def test_get_creator_profile_error(self, mock_get):
        # Mock a 500 Internal Server Error response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        profile = self.service.get_creator_profile("test_creator")

        # Assert that None is returned on error
        self.assertIsNone(profile)
        mock_get.assert_called_once_with(
            'https://www.patreon.com/api/creator/test_creator',
            headers={'Authorization': 'Bearer test_token'}
        )

    @patch('patreon_services.requests.get')
    def test_get_campaigns_success(self, mock_get):
        # Mock a successful response with campaigns data
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"id": "1", "attributes": {"title": "First Campaign", "goal": 1000}},
                {"id": "2", "attributes": {"title": "Second Campaign", "goal": 2000}}
            ]
        }
        mock_get.return_value = mock_response

        campaigns = self.service.get_campaigns("test_creator")

        # Assert that response contains expected campaigns data
        self.assertEqual(len(campaigns), 2)
        self.assertEqual(campaigns[0]["title"], "First Campaign")
        self.assertEqual(campaigns[1]["goal"], 2000)
        mock_get.assert_called_once_with(
            'https://www.patreon.com/api/creator/test_creator/campaigns',
            headers={'Authorization': 'Bearer test_token'}
        )

    @patch('patreon_services.requests.get')
    def test_get_campaigns_no_campaigns(self, mock_get):
        # Mock a 200 response with an empty list of campaigns
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_get.return_value = mock_response

        campaigns = self.service.get_campaigns("test_creator")

        # Assert that an empty list is returned when there are no campaigns
        self.assertEqual(campaigns, [])
        mock_get.assert_called_once_with(
            'https://www.patreon.com/api/creator/test_creator/campaigns',
            headers={'Authorization': 'Bearer test_token'}
        )

if __name__ == "__main__":
    unittest.main()

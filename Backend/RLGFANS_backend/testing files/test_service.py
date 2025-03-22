# test_service.py - Unit tests for RLG Fans service integrations

import unittest
from unittest.mock import patch, MagicMock
from services.admireme_service import AdmireMeService
from services.onlyfans_service import OnlyFansService
from services.fansly_service import FanslyService
from services.patreon_service import PatreonService

class TestAdmireMeService(unittest.TestCase):

    @patch("services.admireme_service.requests.get")
    def test_fetch_trending_content(self, mock_get):
        """
        Test fetching trending content from AdmireMe.
        """
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": "sample trending data"}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        service = AdmireMeService(api_key="test_key")
        response = service.fetch_trending_content()
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("data", response.json())
        self.assertEqual(response.json()["data"], "sample trending data")


class TestOnlyFansService(unittest.TestCase):

    @patch("services.onlyfans_service.requests.get")
    def test_fetch_user_data(self, mock_get):
        """
        Test fetching user data from OnlyFans.
        """
        mock_response = MagicMock()
        mock_response.json.return_value = {"user": {"name": "Test User"}}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        service = OnlyFansService(api_key="test_key")
        response = service.fetch_user_data("test_user")
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("user", response.json())
        self.assertEqual(response.json()["user"]["name"], "Test User")


class TestFanslyService(unittest.TestCase):

    @patch("services.fansly_service.requests.get")
    def test_get_subscriber_count(self, mock_get):
        """
        Test fetching subscriber count from Fansly.
        """
        mock_response = MagicMock()
        mock_response.json.return_value = {"subscribers": 1234}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        service = FanslyService(api_key="test_key")
        response = service.get_subscriber_count("test_user")
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("subscribers", response.json())
        self.assertEqual(response.json()["subscribers"], 1234)


class TestPatreonService(unittest.TestCase):

    @patch("services.patreon_service.requests.get")
    def test_get_campaign_info(self, mock_get):
        """
        Test fetching campaign info from Patreon.
        """
        mock_response = MagicMock()
        mock_response.json.return_value = {"campaign": {"title": "Test Campaign"}}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        service = PatreonService(api_key="test_key")
        response = service.get_campaign_info("test_campaign")
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("campaign", response.json())
        self.assertEqual(response.json()["campaign"]["title"], "Test Campaign")


if __name__ == "__main__":
    unittest.main()

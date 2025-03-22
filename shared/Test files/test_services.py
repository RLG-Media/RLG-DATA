import unittest
from unittest.mock import patch, MagicMock
from Backend.RLGDATA_backend.services import RLGDataService
from Backend.RLGFANS_backend.services import RLGFansService
from shared.data_transformer import DataTransformer
from shared.logging_config import get_logger
from shared.external_api_connections import ExternalAPIManager

# Initialize the shared logger from your logging configuration
logger = get_logger("test_services")

class TestServices(unittest.TestCase):
    """
    TestServices performs unit tests for core functionalities of RLG Data and RLG Fans.
    It tests mentions fetching, trending content retrieval, data transformation,
    and external API status checking.
    """

    def setUp(self) -> None:
        """Set up common variables and initialize services for testing."""
        self.rlg_data_service = RLGDataService()
        self.rlg_fans_service = RLGFansService()
        self.data_transformer = DataTransformer()
        self.external_api_manager = ExternalAPIManager()

    @patch('Backend.RLGDATA_backend.services.RLGDataService.fetch_mentions')
    def test_rlg_data_mentions_fetch(self, mock_fetch_mentions):
        """Test RLG Data mentions fetch functionality."""
        mock_fetch_mentions.return_value = [
            {"platform": "Twitter", "mentions": 120},
            {"platform": "Instagram", "mentions": 150}
        ]
        result = self.rlg_data_service.fetch_mentions()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['platform'], "Twitter")
        logger.info("RLG Data mentions fetch test passed.")

    @patch('Backend.RLGFANS_backend.services.RLGFansService.fetch_mentions')
    def test_rlg_fans_mentions_fetch(self, mock_fetch_mentions):
        """Test RLG Fans mentions fetch functionality."""
        mock_fetch_mentions.return_value = [
            {"platform": "OnlyFans", "mentions": 80},
            {"platform": "Fansly", "mentions": 65}
        ]
        result = self.rlg_fans_service.fetch_mentions()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['platform'], "OnlyFans")
        logger.info("RLG Fans mentions fetch test passed.")

    @patch('shared.external_api_connections.ExternalAPIManager.fetch_trending_data')
    def test_external_api_trending_data(self, mock_fetch_trending):
        """Test fetching trending content via external APIs."""
        mock_fetch_trending.return_value = [
            {"platform": "YouTube", "content": "Video 1", "views": 10000},
            {"platform": "TikTok", "content": "Dance Challenge", "views": 5000}
        ]
        result = self.external_api_manager.fetch_trending_data(["YouTube", "TikTok"])
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['platform'], "YouTube")
        logger.info("External API trending data test passed.")

    @patch('shared.data_transformer.DataTransformer.transform_mentions_data')
    def test_data_transformation_mentions(self, mock_transform_mentions):
        """Test data transformation for mentions."""
        mock_transform_mentions.return_value = [
            {"platform": "Twitter", "mentions": 120, "source": "RLG Data"},
            {"platform": "OnlyFans", "mentions": 80, "source": "RLG Fans"}
        ]
        data = [
            {"platform": "Twitter", "mentions": 120},
            {"platform": "OnlyFans", "mentions": 80}
        ]
        result = self.data_transformer.transform_mentions_data(data)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[1]['source'], "RLG Fans")
        logger.info("Data transformation for mentions test passed.")

    @patch('Backend.RLGDATA_backend.services.RLGDataService.fetch_trending_content')
    @patch('Backend.RLGFANS_backend.services.RLGFansService.fetch_trending_content')
    def test_trending_content_combined(self, mock_fetch_trending_fans, mock_fetch_trending_data):
        """Test trending content retrieval across both RLG Data and RLG Fans."""
        mock_fetch_trending_data.return_value = [
            {"content": "Trending post 1", "engagement": 1000},
            {"content": "Trending post 2", "engagement": 1200}
        ]
        mock_fetch_trending_fans.return_value = [
            {"content": "Fans post 1", "engagement": 300},
            {"content": "Fans post 2", "engagement": 450}
        ]

        data_trending = self.rlg_data_service.fetch_trending_content()
        fans_trending = self.rlg_fans_service.fetch_trending_content()

        self.assertEqual(len(data_trending), 2)
        self.assertEqual(data_trending[0]['content'], "Trending post 1")
        self.assertEqual(len(fans_trending), 2)
        self.assertEqual(fans_trending[0]['content'], "Fans post 1")
        logger.info("Trending content retrieval for both tools test passed.")

    @patch('shared.external_api_connections.ExternalAPIManager.check_api_status')
    def test_api_status_check(self, mock_api_status):
        """Test external API status checks."""
        mock_api_status.return_value = {"YouTube": "Healthy", "TikTok": "Degraded"}
        result = self.external_api_manager.check_api_status(["YouTube", "TikTok"])
        self.assertEqual(result["YouTube"], "Healthy")
        logger.info("External API status check test passed.")

if __name__ == "__main__":
    unittest.main()

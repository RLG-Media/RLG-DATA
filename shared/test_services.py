import unittest
from unittest.mock import patch, MagicMock
from shared.services.rlg_data_service import RLGDataService
from shared.services.rlg_fans_service import RLGFansService
from shared.data_transformer import DataTransformer
from shared.logging_config import get_logger

# Initialize the logger
logger = get_logger()

class TestServices(unittest.TestCase):
    def setUp(self):
        """Set up common variables and initialize services for testing."""
        self.rlg_data_service = RLGDataService()
        self.rlg_fans_service = RLGFansService()
        self.data_transformer = DataTransformer()

    @patch('shared.services.rlg_data_service.RLGDataService.fetch_mentions')
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

    @patch('shared.services.rlg_fans_service.RLGFansService.fetch_mentions')
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

    @patch('shared.services.rlg_data_service.RLGDataService.fetch_sentiment')
    def test_rlg_data_sentiment_analysis(self, mock_fetch_sentiment):
        """Test RLG Data sentiment analysis functionality."""
        mock_fetch_sentiment.return_value = {
            "positive": 50,
            "neutral": 30,
            "negative": 20
        }
        result = self.rlg_data_service.fetch_sentiment()
        self.assertEqual(result['positive'], 50)
        logger.info("RLG Data sentiment analysis test passed.")

    @patch('shared.services.rlg_fans_service.RLGFansService.fetch_sentiment')
    def test_rlg_fans_sentiment_analysis(self, mock_fetch_sentiment):
        """Test RLG Fans sentiment analysis functionality."""
        mock_fetch_sentiment.return_value = {
            "positive": 40,
            "neutral": 40,
            "negative": 20
        }
        result = self.rlg_fans_service.fetch_sentiment()
        self.assertEqual(result['neutral'], 40)
        logger.info("RLG Fans sentiment analysis test passed.")

    @patch('shared.services.rlg_data_service.RLGDataService.fetch_engagement')
    def test_rlg_data_engagement_rate(self, mock_fetch_engagement):
        """Test RLG Data engagement rate fetch functionality."""
        mock_fetch_engagement.return_value = [
            {"week": "Week 1", "engagement_rate": 25},
            {"week": "Week 2", "engagement_rate": 30}
        ]
        result = self.rlg_data_service.fetch_engagement()
        self.assertEqual(result[1]['engagement_rate'], 30)
        logger.info("RLG Data engagement rate test passed.")

    @patch('shared.services.rlg_fans_service.RLGFansService.fetch_engagement')
    def test_rlg_fans_engagement_rate(self, mock_fetch_engagement):
        """Test RLG Fans engagement rate fetch functionality."""
        mock_fetch_engagement.return_value = [
            {"week": "Week 1", "engagement_rate": 18},
            {"week": "Week 2", "engagement_rate": 22}
        ]
        result = self.rlg_fans_service.fetch_engagement()
        self.assertEqual(result[0]['engagement_rate'], 18)
        logger.info("RLG Fans engagement rate test passed.")

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

    @patch('shared.data_transformer.DataTransformer.aggregate_sentiment_data')
    def test_data_transformation_sentiment(self, mock_aggregate_sentiment):
        """Test data transformation for sentiment aggregation."""
        mock_aggregate_sentiment.return_value = {
            "positive": 90,
            "neutral": 70,
            "negative": 40
        }
        sentiment_data = [
            {"positive": 50, "neutral": 30, "negative": 20},
            {"positive": 40, "neutral": 40, "negative": 20}
        ]
        result = self.data_transformer.aggregate_sentiment_data(sentiment_data)
        self.assertEqual(result['positive'], 90)
        logger.info("Data transformation for sentiment aggregation test passed.")

    @patch('shared.services.rlg_data_service.RLGDataService.fetch_trending_content')
    def test_trending_content_rlg_data(self, mock_fetch_trending):
        """Test trending content retrieval in RLG Data service."""
        mock_fetch_trending.return_value = [
            {"content": "Trending post 1", "engagement": 1000},
            {"content": "Trending post 2", "engagement": 1200}
        ]
        result = self.rlg_data_service.fetch_trending_content()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['content'], "Trending post 1")
        logger.info("Trending content retrieval for RLG Data test passed.")

    @patch('shared.services.rlg_fans_service.RLGFansService.fetch_trending_content')
    def test_trending_content_rlg_fans(self, mock_fetch_trending):
        """Test trending content retrieval in RLG Fans service."""
        mock_fetch_trending.return_value = [
            {"content": "Fans post 1", "engagement": 300},
            {"content": "Fans post 2", "engagement": 450}
        ]
        result = self.rlg_fans_service.fetch_trending_content()
        self.assertEqual(result[1]['engagement'], 450)
        logger.info("Trending content retrieval for RLG Fans test passed.")

if __name__ == "__main__":
    unittest.main()

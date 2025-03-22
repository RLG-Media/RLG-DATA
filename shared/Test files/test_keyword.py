import unittest
from unittest.mock import patch, MagicMock
from seo_insights import SEOInsights

class TestSEOInsights(unittest.TestCase):
    """
    Unit tests for the SEOInsights class.
    """

    def setUp(self):
        """Set up the test environment."""
        self.seo_tool = SEOInsights()
        self.sample_keyword = "digital marketing"
        self.sample_domain = "example.com"

    @patch('seo_insights.requests.get')
    def test_get_search_volume(self, mock_get):
        """Test the get_search_volume method."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "search_information": {
                "total_results": 1200000,
                "search_time": 0.45
            },
            "organic_results": [
                {"snippet": "This is a sample snippet"}
            ]
        }
        mock_get.return_value = mock_response

        result = self.seo_tool.get_search_volume(self.sample_keyword)
        self.assertIn("total_results", result)
        self.assertEqual(result["total_results"], 1200000)
        self.assertTrue(result["featured_snippets"])

    @patch('seo_insights.requests.get')
    def test_get_competitors(self, mock_get):
        """Test the get_competitors method."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "organic_results": [
                {"title": "Competitor 1", "link": "http://competitor1.com", "snippet": "Snippet 1", "position": 1},
                {"title": "Competitor 2", "link": "http://competitor2.com", "snippet": "Snippet 2", "position": 2}
            ]
        }
        mock_get.return_value = mock_response

        result = self.seo_tool.get_competitors(self.sample_keyword)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "Competitor 1")
        self.assertEqual(result[1]["rank"], 2)

    @patch('seo_insights.requests.get')
    def test_fetch_website_traffic(self, mock_get):
        """Test the fetch_website_traffic method."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "visits": 50000,
            "engagement_score": 80
        }
        mock_get.return_value = mock_response

        result = self.seo_tool.fetch_website_traffic(self.sample_domain)
        self.assertEqual(result["monthly_visits"], 50000)
        self.assertEqual(result["engagement_score"], 80)

    @patch('seo_insights.requests.get')
    def test_analyze_keyword_strength(self, mock_get):
        """Test the analyze_keyword_strength method."""
        mock_search_volume_response = MagicMock()
        mock_search_volume_response.json.return_value = {
            "search_information": {
                "total_results": 1000000,
                "search_time": 0.5
            },
            "organic_results": [
                {"snippet": "Sample snippet"}
            ]
        }

        mock_competitors_response = MagicMock()
        mock_competitors_response.json.return_value = {
            "organic_results": [
                {"title": "Competitor 1", "position": 1},
                {"title": "Competitor 2", "position": 2}
            ]
        }

        mock_get.side_effect = [mock_search_volume_response, mock_competitors_response]

        result = self.seo_tool.analyze_keyword_strength(self.sample_keyword)
        self.assertIn("keyword", result)
        self.assertIn("total_results", result)
        self.assertIn("competition_level", result)
        self.assertTrue(result["has_featured_snippets"])

    @patch('seo_insights.requests.get')
    def test_generate_report(self, mock_get):
        """Test the generate_report method."""
        mock_search_volume_response = MagicMock()
        mock_search_volume_response.json.return_value = {
            "search_information": {
                "total_results": 1000000,
                "search_time": 0.5
            },
            "organic_results": [
                {"snippet": "Sample snippet"}
            ]
        }

        mock_competitors_response = MagicMock()
        mock_competitors_response.json.return_value = {
            "organic_results": [
                {"title": "Competitor 1", "position": 1},
                {"title": "Competitor 2", "position": 2}
            ]
        }

        mock_get.side_effect = [mock_search_volume_response, mock_competitors_response]

        result = self.seo_tool.generate_report(self.sample_keyword)
        self.assertIn("keyword", result)
        self.assertIn("search_volume", result)
        self.assertIn("competitors", result)
        self.assertIn("keyword_strength", result)

if __name__ == "__main__":
    unittest.main()

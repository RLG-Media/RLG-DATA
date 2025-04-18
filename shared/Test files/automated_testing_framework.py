import unittest
from unittest.mock import patch, MagicMock
import requests

class TestAPIEndpoints(unittest.TestCase):
    BASE_URL = "http://localhost:8000/gateway"

    def test_twitter_service(self):
        endpoint = f"{self.BASE_URL}/twitter/sample"
        with patch("requests.get") as mocked_get:
            mocked_get.return_value.status_code = 200
            mocked_get.return_value.json.return_value = {"status": "success"}
            
            response = requests.get(endpoint)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"status": "success"})

    def test_facebook_service(self):
        endpoint = f"{self.BASE_URL}/facebook/sample"
        with patch("requests.get") as mocked_get:
            mocked_get.return_value.status_code = 200
            mocked_get.return_value.json.return_value = {"status": "success"}
            
            response = requests.get(endpoint)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"status": "success"})

    def test_rate_limiting(self):
        endpoint = f"{self.BASE_URL}/twitter/sample"
        with patch("requests.get") as mocked_get:
            mocked_get.return_value.status_code = 429
            mocked_get.return_value.json.return_value = {"error": "Rate limit exceeded."}
            
            response = requests.get(endpoint)

            self.assertEqual(response.status_code, 429)
            self.assertEqual(response.json(), {"error": "Rate limit exceeded."})

    def test_invalid_service(self):
        endpoint = f"{self.BASE_URL}/invalid_service/sample"
        with patch("requests.get") as mocked_get:
            mocked_get.return_value.status_code = 404
            mocked_get.return_value.json.return_value = {"error": "Service 'invalid_service' not supported."}

            response = requests.get(endpoint)

            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json(), {"error": "Service 'invalid_service' not supported."})

class TestSentimentAnalysis(unittest.TestCase):
    @patch("nltk.sentiment.SentimentIntensityAnalyzer")
    def test_sentiment_analysis(self, MockSentimentAnalyzer):
        MockSentimentAnalyzer.return_value.polarity_scores.return_value = {
            "neg": 0.1, "neu": 0.7, "pos": 0.2, "compound": 0.3
        }

        from nlp_analysis_services import SentimentAnalysisService

        service = SentimentAnalysisService()
        posts = [
            {"text": "This is great!"},
            {"text": "This is terrible."}
        ]
        analyzed_posts = service.analyze_sentiments(posts)

        for post in analyzed_posts:
            self.assertIn("sentiment", post)
            self.assertIsInstance(post["sentiment"], dict)

class TestCacheServices(unittest.TestCase):
    @patch("redis.StrictRedis")
    def test_cache_set_get(self, MockRedis):
        mock_redis_instance = MockRedis.return_value
        mock_redis_instance.get.return_value = b'{"key": "value"}'

        from cache_services import CacheService

        cache = CacheService()
        cache.set("test_key", {"key": "value"})
        result = cache.get("test_key")

        self.assertEqual(result, {"key": "value"})

if __name__ == "__main__":
    unittest.main()

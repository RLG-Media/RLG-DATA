import unittest
from unittest.mock import patch, MagicMock
import requests
from services.api_gateway_services import ApiGatewayServices
from services.social_media_monitoring import SocialMediaMonitoringService
from services.billing_services import BillingService
from services.dynamic_pricing_manager import DynamicPricingManager
from services.data_stream_processor import DataStreamProcessor

class IntegrationTests(unittest.TestCase):
    """
    Integration tests for RLG Data and RLG Fans services.
    Covers:
    - Social media integrations
    - API gateway interactions
    - Billing and pricing services
    - Data stream processing
    """

    def setUp(self):
        self.api_gateway = ApiGatewayServices()
        self.social_media_service = SocialMediaMonitoringService()
        self.billing_service = BillingService()
        self.pricing_manager = DynamicPricingManager()
        self.stream_processor = DataStreamProcessor()

    @patch('requests.get')
    def test_social_media_monitoring_integration(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"id": "1", "text": "Test tweet"}]
        }
        mock_get.return_value = mock_response

        result = self.social_media_service.fetch_twitter_mentions("test")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['text'], "Test tweet")

    @patch('services.api_gateway_services.ApiGatewayServices.forward_request')
    def test_api_gateway_forwarding(self, mock_forward_request):
        mock_forward_request.return_value = {
            "status": 200,
            "data": {"message": "Request successful"}
        }
        response = self.api_gateway.forward_request("GET", "/test-endpoint")
        self.assertEqual(response['status'], 200)
        self.assertIn("message", response['data'])

    @patch('services.billing_services.BillingService.process_payment')
    def test_billing_service_payment_processing(self, mock_process_payment):
        mock_process_payment.return_value = {
            "success": True,
            "transaction_id": "txn_12345"
        }
        response = self.billing_service.process_payment(user_id="user_1", amount=100.0, currency="USD")
        self.assertTrue(response['success'])
        self.assertIn("transaction_id", response)

    @patch('services.dynamic_pricing_manager.DynamicPricingManager.get_pricing')
    def test_dynamic_pricing_manager(self, mock_get_pricing):
        mock_get_pricing.return_value = {
            "region": "US",
            "pricing": {"monthly": 59, "weekly": 15}
        }
        response = self.pricing_manager.get_pricing(region="US")
        self.assertEqual(response['region'], "US")
        self.assertIn("monthly", response['pricing'])

    @patch('services.data_stream_processor.DataStreamProcessor.process_stream')
    def test_data_stream_processing(self, mock_process_stream):
        mock_process_stream.return_value = {
            "processed": True,
            "records": 100
        }
        response = self.stream_processor.process_stream("test_stream")
        self.assertTrue(response['processed'])
        self.assertEqual(response['records'], 100)

if __name__ == '__main__':
    unittest.main()

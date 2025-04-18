# unit_tests.py

import unittest
from your_module import (
    ThirdPartyIntegration, 
    some_function_to_test, 
    AnotherClass
)

class TestThirdPartyIntegration(unittest.TestCase):
    def setUp(self):
        # Set up a mock or test instance of ThirdPartyIntegration
        self.api_integration = ThirdPartyIntegration('https://api.mock.com', 'mock_api_key')

    def test_get_data_success(self):
        # Test successful GET request
        mock_response = {"key": "value"}
        self.api_integration._send_request = lambda *args, **kwargs: mock_response
        response = self.api_integration.get_data('test_endpoint')
        self.assertEqual(response, mock_response)

    def test_post_data_success(self):
        # Test successful POST request
        mock_response = {"status": "success"}
        self.api_integration._send_request = lambda *args, **kwargs: mock_response
        response = self.api_integration.post_data('test_endpoint', {'key': 'value'})
        self.assertEqual(response, mock_response)

    def test_put_data_success(self):
        # Test successful PUT request
        mock_response = {"status": "updated"}
        self.api_integration._send_request = lambda *args, **kwargs: mock_response
        response = self.api_integration.put_data('test_endpoint', {'key': 'value'})
        self.assertEqual(response, mock_response)

    def test_delete_data_success(self):
        # Test successful DELETE request
        mock_response = {"status": "deleted"}
        self.api_integration._send_request = lambda *args, **kwargs: mock_response
        response = self.api_integration.delete_data('test_endpoint')
        self.assertEqual(response, mock_response)

    def test_send_request_http_error(self):
        # Test HTTP error handling
        self.api_integration._send_request = lambda *args, **kwargs: (_ for _ in ()).throw(RequestException('HTTP Error'))
        with self.assertRaises(RequestException):
            self.api_integration.get_data('test_endpoint')

    def test_send_request_request_error(self):
        # Test general request error handling
        self.api_integration._send_request = lambda *args, **kwargs: (_ for _ in ()).throw(Exception('Request Error'))
        with self.assertRaises(Exception):
            self.api_integration.get_data('test_endpoint')

class TestSomeFunction(unittest.TestCase):
    def test_some_function(self):
        # Example of a function to test
        result = some_function_to_test(5)
        self.assertEqual(result, 25)

class TestAnotherClass(unittest.TestCase):
    def setUp(self):
        self.another_class = AnotherClass()

    def test_another_class_method(self):
        # Example of testing methods from AnotherClass
        result = self.another_class.some_method('test input')
        self.assertEqual(result, 'expected output')

if __name__ == '__main__':
    unittest.main()

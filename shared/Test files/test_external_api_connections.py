# test_external_api_connections.py

import unittest
import requests
from shared.config import Config
from shared.auth_middleware import generate_auth_token
from time import sleep


class TestExternalAPIConnections(unittest.TestCase):
    """Test suite for validating connections with external APIs used in RLG Data and RLG Fans."""

    BASE_URL = Config.BASE_URL
    external_services = {
        "OnlyFans": "/api/onlyfans/validate",
        "Patreon": "/api/patreon/validate",
        "TikTok": "/api/tiktok/validate",
        "YouTube": "/api/youtube/validate",
        "Facebook": "/api/facebook/validate",
        "Snapchat": "/api/snapchat/validate",
        "Twitter": "/api/twitter/validate",
        "Instagram": "/api/instagram/validate",
        "FeetFinder": "/api/feetfinder/validate",
        "YouFanly": "/api/youfanly/validate",
        "Sheer": "/api/sheer/validate",
        "Fansly": "/api/fansly/validate",
        "Fapello": "/api/fapello/validate",
        "FanCentro": "/api/fancentro/validate",
        "ManyVids": "/api/manyvids/validate",
        "Fanvue": "/api/fanvue/validate",
        "Alua": "/api/alua/validate",
        "Fansify": "/api/fansify/validate",
    }

    def setUp(self):
        """Set up authentication and headers."""
        self.auth_token = generate_auth_token(user_id=1, role="admin")
        self.headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json",
        }
        self.test_payload = {
            "test_connection": True,  # Payload to confirm connectivity, if needed
        }

    def test_external_api_connections(self):
        """Test connection to each configured external API."""
        failed_connections = []

        for service_name, endpoint in self.external_services.items():
            response = requests.post(
                f"{self.BASE_URL}{endpoint}",
                json=self.test_payload,
                headers=self.headers,
            )
            if response.status_code == 200:
                data = response.json()
                self.assertTrue(
                    data.get("connection_status"),
                    f"{service_name} failed connection check",
                )
                print(f"{service_name} API connection validated successfully.")
            else:
                failed_connections.append((service_name, response.status_code))
                print(
                    f"Failed to connect to {service_name}. Status Code: {response.status_code}"
                )

            # Rate-limiting precaution
            sleep(0.5)

        self.assertEqual(
            len(failed_connections), 0, f"Failed API connections: {failed_connections}"
        )

    def test_api_response_times(self):
        """Ensure each external API responds within acceptable time limits."""
        max_response_time = 2.0  # seconds
        slow_apis = []

        for service_name, endpoint in self.external_services.items():
            response = requests.post(
                f"{self.BASE_URL}{endpoint}",
                json=self.test_payload,
                headers=self.headers,
            )
            response_time = response.elapsed.total_seconds()
            print(f"{service_name} API response time: {response_time:.2f} seconds")

            if response_time > max_response_time:
                slow_apis.append((service_name, response_time))
            else:
                self.assertTrue(
                    response.ok, f"{service_name} response returned error status"
                )

        self.assertEqual(
            len(slow_apis), 0, f"APIs with slow response times: {slow_apis}"
        )

    def test_authentication_security(self):
        """Check that each API connection requires valid authentication."""
        invalid_token_headers = {
            "Authorization": "Bearer invalid_token",
            "Content-Type": "application/json",
        }
        unauthorized_apis = []

        for service_name, endpoint in self.external_services.items():
            response = requests.post(
                f"{self.BASE_URL}{endpoint}",
                json=self.test_payload,
                headers=invalid_token_headers,
            )
            if response.status_code != 401:
                unauthorized_apis.append(service_name)
            print(
                f"{service_name} unauthorized access test: Status Code {response.status_code}"
            )

        self.assertEqual(
            len(unauthorized_apis),
            0,
            f"APIs allowing unauthorized access: {unauthorized_apis}",
        )

    def tearDown(self):
        """Clean up resources or state after tests."""
        # Clean-up actions if necessary
        pass


if __name__ == "__main__":
    unittest.main()

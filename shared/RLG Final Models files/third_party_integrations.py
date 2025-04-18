import logging
import requests
import json
from database import Database
from config import API_KEYS, INTEGRATION_SETTINGS
from auth_manager import OAuthManager

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class ThirdPartyIntegrations:
    """Manages all third-party API integrations for RLG Data & RLG Fans, including social media, analytics, and payments."""

    def __init__(self):
        self.db = Database()
        self.oauth_manager = OAuthManager()
        self.services = {
            "twitter": {"base_url": "https://api.twitter.com/2/", "auth_type": "OAuth2"},
            "facebook": {"base_url": "https://graph.facebook.com/v18.0/", "auth_type": "OAuth2"},
            "linkedin": {"base_url": "https://api.linkedin.com/v2/", "auth_type": "OAuth2"},
            "google_analytics": {"base_url": "https://analyticsreporting.googleapis.com/v4/", "auth_type": "OAuth2"},
            "stripe": {"base_url": "https://api.stripe.com/v1/", "auth_type": "API Key"},
            "paypal": {"base_url": "https://api-m.paypal.com/", "auth_type": "API Key"},
            "payfast": {"base_url": "https://api.payfast.co.za/", "auth_type": "API Key"},  # Added PayFast
        }

    def authenticate(self, service_name):
        """Handles authentication for third-party services."""
        service = self.services.get(service_name)
        if not service:
            logging.error(f"Service '{service_name}' not found.")
            return None

        if service["auth_type"] == "OAuth2":
            return self.oauth_manager.get_access_token(service_name)
        elif service["auth_type"] == "API Key":
            return API_KEYS.get(service_name)
        else:
            logging.error(f"Unknown authentication type for {service_name}.")
            return None

    def send_request(self, service_name, endpoint, method="GET", data=None):
        """Handles API requests to third-party services with automatic retries."""
        auth_token = self.authenticate(service_name)
        if not auth_token:
            logging.error(f"Authentication failed for {service_name}")
            return None

        headers = {"Authorization": f"Bearer {auth_token}"}
        url = f"{self.services[service_name]['base_url']}{endpoint}"
        retry_attempts = 3

        for attempt in range(retry_attempts):
            try:
                if method == "GET":
                    response = requests.get(url, headers=headers)
                elif method == "POST":
                    headers["Content-Type"] = "application/json"
                    response = requests.post(url, headers=headers, json=data)
                else:
                    logging.error("Unsupported HTTP method.")
                    return None

                response.raise_for_status()
                return response.json()

            except requests.exceptions.RequestException as e:
                logging.warning(f"Attempt {attempt + 1} failed for {service_name}: {e}")
                if attempt == retry_attempts - 1:
                    logging.error(f"All retry attempts failed for {service_name}")
                    return None

    def sync_data(self, service_name, endpoint):
        """Fetches and stores data from a third-party service."""
        data = self.send_request(service_name, endpoint)
        if data:
            self.db.insert(f"{service_name}_data", data)
            logging.info(f"Synced data from {service_name}: {endpoint}")
        return data

    def process_payment(self, provider, amount, currency="USD", customer_email=None):
        """Handles payments via Stripe, PayPal, and PayFast."""
        if provider not in ["stripe", "paypal", "payfast"]:
            logging.error("Unsupported payment provider.")
            return None

        if provider == "stripe":
            endpoint = "charges"
            payload = {"amount": amount, "currency": currency, "description": "RLG Data & RLG Fans Subscription"}
            if customer_email:
                payload["customer_email"] = customer_email
        elif provider == "paypal":
            endpoint = "v2/checkout/orders"
            payload = {"intent": "CAPTURE", "purchase_units": [{"amount": {"currency_code": currency, "value": amount}}]}
        elif provider == "payfast":
            endpoint = "transaction"
            payload = {
                "amount": amount,
                "currency": currency,
                "description": "RLG Data & RLG Fans Subscription",
                "buyer_email": customer_email,
            }

        return self.send_request(provider, endpoint, method="POST", data=payload)

# Initialize Integrations
third_party = ThirdPartyIntegrations()

# Example Usage
if __name__ == "__main__":
    # Sync latest Twitter analytics data
    twitter_data = third_party.sync_data("twitter", "tweets/search/recent?query=rlgdata")

    # Process payments via Stripe, PayPal, and PayFast
    stripe_payment = third_party.process_payment("stripe", 99.00, "USD", "user@example.com")
    paypal_payment = third_party.process_payment("paypal", 99.00, "USD", "user@example.com")
    payfast_payment = third_party.process_payment("payfast", 99.00, "ZAR", "user@example.com")

    logging.info(f"Twitter Data: {json.dumps(twitter_data, indent=2)}")
    logging.info(f"Stripe Payment: {json.dumps(stripe_payment, indent=2)}")
    logging.info(f"PayPal Payment: {json.dumps(paypal_payment, indent=2)}")
    logging.info(f"PayFast Payment: {json.dumps(payfast_payment, indent=2)}")

import logging
from typing import Dict, Optional
import stripe
import requests
from datetime import datetime

# Configure the logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("billing_logs.log"),
        logging.StreamHandler()
    ]
)

class BillingService:
    """
    Service class for managing billing and subscriptions for RLG Data and RLG Fans.
    Includes functionality for handling payment processing, subscription management, and invoicing.
    Supports Stripe and PayFast payment gateways.
    """

    def __init__(self, stripe_api_key: str, payfast_merchant_id: str, payfast_merchant_key: str, payfast_passphrase: Optional[str] = None):
        """
        Initialize the BillingService with API keys for Stripe and PayFast.

        Args:
            stripe_api_key: The secret API key for Stripe integration.
            payfast_merchant_id: The merchant ID for PayFast integration.
            payfast_merchant_key: The merchant key for PayFast integration.
            payfast_passphrase: Optional passphrase for PayFast (if enabled).
        """
        stripe.api_key = stripe_api_key
        self.currency = "usd"
        self.payfast_merchant_id = payfast_merchant_id
        self.payfast_merchant_key = payfast_merchant_key
        self.payfast_passphrase = payfast_passphrase
        self.payfast_base_url = "https://sandbox.payfast.co.za/eng/process"
        logging.info("BillingService initialized with Stripe and PayFast APIs.")

    # Stripe Methods
    def create_customer(self, email: str, name: Optional[str] = None) -> Dict:
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name
            )
            logging.info("Stripe customer created: %s", customer.id)
            return customer
        except stripe.error.StripeError as e:
            logging.error("Failed to create Stripe customer: %s", e)
            raise

    def create_subscription(self, customer_id: str, price_id: str) -> Dict:
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}]
            )
            logging.info("Stripe subscription created: %s", subscription.id)
            return subscription
        except stripe.error.StripeError as e:
            logging.error("Failed to create Stripe subscription: %s", e)
            raise

    def cancel_subscription(self, subscription_id: str) -> Dict:
        try:
            canceled_subscription = stripe.Subscription.delete(subscription_id)
            logging.info("Stripe subscription canceled: %s", subscription_id)
            return canceled_subscription
        except stripe.error.StripeError as e:
            logging.error("Failed to cancel Stripe subscription: %s", e)
            raise

    def retrieve_invoice(self, invoice_id: str) -> Dict:
        try:
            invoice = stripe.Invoice.retrieve(invoice_id)
            logging.info("Stripe invoice retrieved: %s", invoice_id)
            return invoice
        except stripe.error.StripeError as e:
            logging.error("Failed to retrieve Stripe invoice: %s", e)
            raise

    def generate_invoice(self, customer_id: str) -> Dict:
        try:
            invoice_item = stripe.InvoiceItem.create(
                customer=customer_id,
                amount=5000,  # Example amount (e.g., $50.00)
                currency=self.currency,
                description="Example Invoice Item"
            )
            logging.info("Stripe invoice item created for customer: %s", customer_id)

            invoice = stripe.Invoice.create(
                customer=customer_id,
                auto_advance=True  # Automatically finalize the invoice
            )
            logging.info("Stripe draft invoice generated: %s", invoice.id)
            return invoice
        except stripe.error.StripeError as e:
            logging.error("Failed to generate Stripe invoice: %s", e)
            raise

    def handle_webhook(self, payload: str, sig_header: str, endpoint_secret: str) -> Dict:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
            logging.info("Stripe webhook received: %s", event["type"])
            return event
        except stripe.error.SignatureVerificationError as e:
            logging.error("Stripe webhook signature verification failed: %s", e)
            raise
        except stripe.error.StripeError as e:
            logging.error("Failed to handle Stripe webhook: %s", e)
            raise

    # PayFast Methods
    def initiate_payfast_payment(self, amount: float, item_name: str, return_url: str, cancel_url: str, notify_url: str) -> str:
        """
        Initiate a payment request with PayFast.

        Args:
            amount: The amount to be paid.
            item_name: The name of the item being purchased.
            return_url: The URL to redirect to after payment success.
            cancel_url: The URL to redirect to after payment cancellation.
            notify_url: The URL PayFast will use to notify about payment status.

        Returns:
            The payment URL for PayFast.
        """
        data = {
            "merchant_id": self.payfast_merchant_id,
            "merchant_key": self.payfast_merchant_key,
            "amount": f"{amount:.2f}",
            "item_name": item_name,
            "return_url": return_url,
            "cancel_url": cancel_url,
            "notify_url": notify_url
        }

        if self.payfast_passphrase:
            data["passphrase"] = self.payfast_passphrase

        try:
            response = requests.post(self.payfast_base_url, data=data)
            response.raise_for_status()
            logging.info("PayFast payment initiated for item: %s", item_name)
            return response.url
        except requests.RequestException as e:
            logging.error("Failed to initiate PayFast payment: %s", e)
            raise

    def validate_payfast_notification(self, data: Dict) -> bool:
        """
        Validate a PayFast payment notification.

        Args:
            data: The notification data from PayFast.

        Returns:
            True if the notification is valid, False otherwise.
        """
        validate_url = f"{self.payfast_base_url}/validate"
        try:
            response = requests.post(validate_url, data=data)
            is_valid = response.text.strip() == "VALID"
            logging.info("PayFast notification validation result: %s", is_valid)
            return is_valid
        except requests.RequestException as e:
            logging.error("Failed to validate PayFast notification: %s", e)
            raise

# Example usage
if __name__ == "__main__":
    STRIPE_API_KEY = "your_stripe_secret_key"
    PAYFAST_MERCHANT_ID = "your_payfast_merchant_id"
    PAYFAST_MERCHANT_KEY = "your_payfast_merchant_key"
    PAYFAST_PASSPHRASE = "your_payfast_passphrase"  # Optional

    billing_service = BillingService(
        stripe_api_key=STRIPE_API_KEY,
        payfast_merchant_id=PAYFAST_MERCHANT_ID,
        payfast_merchant_key=PAYFAST_MERCHANT_KEY,
        payfast_passphrase=PAYFAST_PASSPHRASE
    )

    # Example for initiating a PayFast payment
    payfast_url = billing_service.initiate_payfast_payment(
        amount=100.0,
        item_name="Premium Subscription",
        return_url="https://example.com/success",
        cancel_url="https://example.com/cancel",
        notify_url="https://example.com/notify"
    )
    print(f"PayFast Payment URL: {payfast_url}")

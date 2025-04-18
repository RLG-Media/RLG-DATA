import stripe
import paypalrestsdk
import requests
import json
import os
import logging
from decimal import Decimal

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")
PAYFAST_MERCHANT_ID = os.getenv("PAYFAST_MERCHANT_ID")
PAYFAST_MERCHANT_KEY = os.getenv("PAYFAST_MERCHANT_KEY")
PAYFAST_PASS_PHRASE = os.getenv("PAYFAST_PASS_PHRASE")
PAYFAST_URL = "https://www.payfast.co.za/eng/process"  # Adjust based on sandbox or live

# Initialize Stripe
stripe.api_key = STRIPE_SECRET_KEY

# Initialize PayPal
paypalrestsdk.configure({
    "mode": "live",  # Change to "sandbox" for testing
    "client_id": PAYPAL_CLIENT_ID,
    "client_secret": PAYPAL_CLIENT_SECRET
})

def create_stripe_payment(amount, currency, description):
    """Create a Stripe Payment Intent."""
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=int(Decimal(amount) * 100),  # Convert to cents
            currency=currency.lower(),
            description=description,
            payment_method_types=["card"],
        )
        logging.info("Stripe payment created successfully.")
        return payment_intent.client_secret
    except Exception as e:
        logging.error(f"Stripe Payment Error: {e}")
        return None

def create_paypal_payment(amount, currency, description, return_url, cancel_url):
    """Create a PayPal Payment."""
    try:
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "redirect_urls": {"return_url": return_url, "cancel_url": cancel_url},
            "transactions": [{"amount": {"total": str(amount), "currency": currency}, "description": description}]
        })
        if payment.create():
            approval_url = next((link.href for link in payment.links if link.rel == "approval_url"), None)
            logging.info("PayPal payment created successfully.")
            return approval_url
        else:
            logging.error(f"PayPal Payment Error: {payment.error}")
            return None
    except Exception as e:
        logging.error(f"PayPal Payment Exception: {e}")
        return None

def create_payfast_payment(amount, item_name, item_description, return_url, cancel_url, notify_url):
    """Create a PayFast Payment."""
    try:
        payload = {
            "merchant_id": PAYFAST_MERCHANT_ID,
            "merchant_key": PAYFAST_MERCHANT_KEY,
            "amount": amount,
            "item_name": item_name,
            "item_description": item_description,
            "return_url": return_url,
            "cancel_url": cancel_url,
            "notify_url": notify_url,
            "passphrase": PAYFAST_PASS_PHRASE
        }
        response = requests.post(PAYFAST_URL, data=payload)
        if response.status_code == 200:
            logging.info("PayFast payment created successfully.")
            return response.url
        else:
            logging.error(f"PayFast Payment Error: {response.text}")
            return None
    except Exception as e:
        logging.error(f"PayFast Payment Exception: {e}")
        return None

def process_payment(method, amount, currency="USD", description="RLG Data & RLG Fans Subscription", return_url="https://yourwebsite.com/success", cancel_url="https://yourwebsite.com/cancel", notify_url="https://yourwebsite.com/notify"):
    """Process a payment based on the selected method."""
    if method == "stripe":
        return create_stripe_payment(amount, currency, description)
    elif method == "paypal":
        return create_paypal_payment(amount, currency, description, return_url, cancel_url)
    elif method == "payfast":
        return create_payfast_payment(amount, description, description, return_url, cancel_url, notify_url)
    else:
        logging.warning("Invalid payment method selected.")
        return "Invalid payment method."

if __name__ == "__main__":
    test_amount = 100
    test_currency = "USD"
    print("Stripe Payment:", process_payment("stripe", test_amount, test_currency))
    print("PayPal Payment:", process_payment("paypal", test_amount, test_currency))
    print("PayFast Payment:", process_payment("payfast", test_amount, "ZAR"))

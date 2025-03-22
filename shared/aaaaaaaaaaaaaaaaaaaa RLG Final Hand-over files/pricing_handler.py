import os
import logging
import requests
import geoip2.database
import stripe
import paypalrestsdk
from payfast import PayFast
from forex_python.converter import CurrencyRates

# ------------------------- CONFIGURATION -------------------------

LOG_FILE = "rlg_pricing_handler.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)

GEOIP_DB_PATH = "./GeoLite2-City.mmdb"
currency_converter = CurrencyRates()

STRIPE_API_KEY = "your_stripe_api_key"
PAYPAL_CLIENT_ID = "your_paypal_client_id"
PAYPAL_CLIENT_SECRET = "your_paypal_client_secret"
PAYFAST_MERCHANT_ID = "your_payfast_merchant_id"
PAYFAST_MERCHANT_KEY = "your_payfast_merchant_key"

stripe.api_key = STRIPE_API_KEY

paypalrestsdk.configure({
    "mode": "live",
    "client_id": PAYPAL_CLIENT_ID,
    "client_secret": PAYPAL_CLIENT_SECRET
})

payfast = PayFast(merchant_id=PAYFAST_MERCHANT_ID, merchant_key=PAYFAST_MERCHANT_KEY)

# ------------------------- PRICING RULES -------------------------

PRICING_RULES = {
    "Israel": {"weekly": 99, "monthly": 399, "annual": 3999, "currency": "USD"},
    "US": {"weekly": 15, "monthly": 59, "annual": 599, "currency": "USD"},
    "Europe": {"weekly": 15, "monthly": 59, "annual": 599, "currency": "EUR"},
    "Asia": {"weekly": 12, "monthly": 49, "annual": 499, "currency": "USD"},
    "Africa": {"weekly": 8, "monthly": 35, "annual": 350, "currency": "USD"},
    "SADC": {"weekly": 6, "monthly": 29, "annual": 290, "currency": "ZAR"},
    "Default": {"weekly": 15, "monthly": 59, "annual": 599, "currency": "USD"}
}

# ------------------------- GEOLOCATION HANDLING -------------------------

def get_user_location(ip_address):
    try:
        with geoip2.database.Reader(GEOIP_DB_PATH) as reader:
            response = reader.city(ip_address)
            return response.country.name, response.city.name
    except Exception as e:
        logging.error(f"Location detection failed: {e}")
        return "Unknown", "Unknown"


def is_vpn_or_proxy(ip_address):
    try:
        response = requests.get(f"https://vpnapi.io/api/{ip_address}?key=your_api_key")
        data = response.json()
        return data.get("security", {}).get("vpn") or data.get("security", {}).get("proxy")
    except Exception as e:
        logging.error(f"VPN detection failed: {e}")
        return False

# ------------------------- PRICING LOGIC -------------------------

def get_pricing(ip_address):
    country, _ = get_user_location(ip_address)
    pricing = PRICING_RULES.get(country, PRICING_RULES["Default"])
    return pricing


def convert_currency(price, from_currency, to_currency="USD"):
    try:
        return round(currency_converter.convert(from_currency, to_currency, price), 2)
    except Exception as e:
        logging.error(f"Currency conversion failed: {e}")
        return price

# ------------------------- PAYMENT PROCESSING -------------------------

def create_stripe_payment(amount, currency="USD"):
    try:
        intent = stripe.PaymentIntent.create(amount=int(amount * 100), currency=currency, payment_method_types=["card"])
        return intent.client_secret
    except Exception as e:
        logging.error(f"Stripe Error: {e}")
        return None


def create_paypal_payment(amount, currency="USD"):
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "transactions": [{"amount": {"total": str(amount), "currency": currency}, "description": "RLG Subscription"}],
        "redirect_urls": {"return_url": "https://yourwebsite.com/success", "cancel_url": "https://yourwebsite.com/cancel"}
    })
    if payment.create():
        return payment.links[1].href
    else:
        logging.error(f"PayPal Error: {payment.error}")
        return None


def create_payfast_payment(amount, currency="ZAR"):
    try:
        return payfast.generate_payment_url(amount=amount, item_name="RLG Subscription",
                                            return_url="https://yourwebsite.com/success",
                                            cancel_url="https://yourwebsite.com/cancel",
                                            notify_url="https://yourwebsite.com/notify")
    except Exception as e:
        logging.error(f"PayFast Error: {e}")
        return None


def process_payment(user_ip, method, plan):
    pricing = get_pricing(user_ip)
    amount = pricing.get(plan, PRICING_RULES["Default"]["monthly"])

    if method == "stripe":
        return create_stripe_payment(amount, pricing["currency"])
    elif method == "paypal":
        return create_paypal_payment(amount, pricing["currency"])
    elif method == "payfast":
        return create_payfast_payment(amount, pricing["currency"])
    else:
        return "Invalid payment method"

# ------------------------- TEST EXECUTION -------------------------

if __name__ == "__main__":
    test_ip = "8.8.8.8"
    print("Detected Pricing:", get_pricing(test_ip))
    print("Stripe Payment:", process_payment(test_ip, "stripe", "monthly"))
    print("PayPal Payment:", process_payment(test_ip, "paypal", "weekly"))
    print("PayFast Payment:", process_payment(test_ip, "payfast", "monthly"))

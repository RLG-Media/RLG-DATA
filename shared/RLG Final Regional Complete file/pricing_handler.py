import os
import logging
import requests
import stripe
import paypalrestsdk
from payfast import PayFast
from forex_python.converter import CurrencyRates
from geolocation_service import get_user_location, is_user_in_special_region, is_user_in_sadc_region

# ------------------------- CONFIGURATION -------------------------
LOG_FILE = "rlg_pricing_handler.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)
logger = logging.getLogger("PricingHandler")

# Path to GeoIP database (if needed) is configured in geolocation_service.py

# Initialize currency converter
currency_converter = CurrencyRates()

# Payment gateway configuration (replace with your secure keys or load from environment variables)
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", "your_stripe_api_key")
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID", "your_paypal_client_id")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET", "your_paypal_client_secret")
PAYFAST_MERCHANT_ID = os.getenv("PAYFAST_MERCHANT_ID", "your_payfast_merchant_id")
PAYFAST_MERCHANT_KEY = os.getenv("PAYFAST_MERCHANT_KEY", "your_payfast_merchant_key")

stripe.api_key = STRIPE_API_KEY

paypalrestsdk.configure({
    "mode": "live",  # or "sandbox" for testing
    "client_id": PAYPAL_CLIENT_ID,
    "client_secret": PAYPAL_CLIENT_SECRET
})

payfast = PayFast(merchant_id=PAYFAST_MERCHANT_ID, merchant_key=PAYFAST_MERCHANT_KEY)

# ------------------------- PRICING RULES -------------------------
# Special Region (Israel) - Hard locked pricing; users from Israel see this pricing exclusively.
SPECIAL_REGION_PRICING = {
    "weekly": 35,
    "monthly": 99,
    "annual": None,  # Annual pricing not defined here if not applicable
    "currency": "USD"
}

# SADC Region Pricing (for select African countries)
SADC_PRICING = {
    "weekly": 147,
    "monthly": 550,
    "annual": None,
    "currency": "ZAR"
}

# Global Default Pricing
DEFAULT_PRICING = {
    "weekly": 15,
    "monthly": 59,
    "annual": None,
    "currency": "USD"
}

# Define pricing rules for various regions
# Note: Ensure that the SADC region is determined based on a list of country codes or names in your geolocation service.
PRICING_RULES = {
    "IL": SPECIAL_REGION_PRICING,
    "SADC": SADC_PRICING,
    "DEFAULT": DEFAULT_PRICING
}

# ------------------------- HELPER FUNCTIONS -------------------------

def get_pricing_by_region(location_data):
    """
    Determines the appropriate pricing based on location.
    - If the user is in Israel (Special Region), returns SPECIAL_REGION_PRICING.
    - If the user is in one of the SADC countries, returns SADC_PRICING.
    - Otherwise, returns DEFAULT_PRICING.
    """
    if not location_data:
        raise ValueError("Location data is required to determine pricing.")

    country = location_data.get("country", "").upper()
    if is_user_in_special_region(location_data):
        logger.debug("User is in the Special Region (Israel).")
        return PRICING_RULES["IL"]
    elif is_user_in_sadc_region(location_data):
        logger.debug("User is in a SADC region.")
        return PRICING_RULES["SADC"]
    else:
        logger.debug("Applying default global pricing.")
        return PRICING_RULES["DEFAULT"]

def convert_currency(price, from_currency, to_currency="USD"):
    """
    Converts a given price from one currency to another.
    Returns the price rounded to 2 decimal places.
    """
    try:
        converted = currency_converter.convert(from_currency, to_currency, price)
        return round(converted, 2)
    except Exception as e:
        logger.error(f"Currency conversion failed: {e}")
        return price

# ------------------------- PAYMENT PROCESSING FUNCTIONS -------------------------

def create_stripe_payment(amount, currency="USD"):
    """
    Creates a Stripe Payment Intent.
    Returns the client secret if successful; otherwise, returns None.
    """
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert dollars to cents
            currency=currency,
            payment_method_types=["card"]
        )
        return intent.client_secret
    except Exception as e:
        logger.error(f"Stripe Error: {e}")
        return None

def create_paypal_payment(amount, currency="USD"):
    """
    Creates a PayPal payment.
    Returns the PayPal approval URL if successful; otherwise, returns None.
    """
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "transactions": [{
            "amount": {"total": str(amount), "currency": currency},
            "description": "RLG Data & RLG Fans Subscription"
        }],
        "redirect_urls": {
            "return_url": "https://yourwebsite.com/success",
            "cancel_url": "https://yourwebsite.com/cancel"
        }
    })
    if payment.create():
        # Typically, the approval URL is found among the payment links
        for link in payment.links:
            if link.rel == "approval_url":
                return link.href
        logger.error("Approval URL not found in PayPal response.")
        return None
    else:
        logger.error(f"PayPal Error: {payment.error}")
        return None

def create_payfast_payment(amount, currency="ZAR"):
    """
    Generates a PayFast payment URL.
    Returns the URL if successful; otherwise, returns None.
    """
    try:
        payment_url = payfast.generate_payment_url(
            amount=amount,
            item_name="RLG Subscription",
            return_url="https://yourwebsite.com/success",
            cancel_url="https://yourwebsite.com/cancel",
            notify_url="https://yourwebsite.com/notify"
        )
        return payment_url
    except Exception as e:
        logger.error(f"PayFast Error: {e}")
        return None

def process_payment(user_ip, method, plan):
    """
    Processes a payment based on the user's IP (which determines location/pricing),
    chosen payment method, and selected plan (weekly, monthly, etc.).

    Parameters:
        user_ip (str): The user's IP address for geolocation lookup.
        method (str): Payment method ('stripe', 'paypal', or 'payfast').
        plan (str): Pricing option ('weekly' or 'monthly').

    Returns:
        Payment intent/client secret or approval URL, or an error message.
    """
    # Fetch the user's pricing based on location data
    location_data = get_user_location(user_ip)
    pricing = get_pricing_by_region(location_data)
    
    # Get the base amount based on the plan. If plan not found, default to monthly pricing.
    amount = pricing.get(plan, pricing.get("monthly"))
    currency = pricing.get("currency", "USD")
    
    logger.info(f"Processing {method} payment for plan '{plan}' with amount {amount} {currency}")
    
    if method == "stripe":
        return create_stripe_payment(amount, currency)
    elif method == "paypal":
        return create_paypal_payment(amount, currency)
    elif method == "payfast":
        return create_payfast_payment(amount, currency)
    else:
        error_msg = "Invalid payment method"
        logger.error(error_msg)
        return error_msg

# ------------------------- USER PRICING FUNCTION -------------------------

def get_user_pricing(user_id, ip_address=None, pricing_option='monthly'):
    """
    Fetches user location and determines the pricing based on location and selected pricing option.
    
    Note: The pricing page is only available after registration to lock in the user's location.
          Special Region (Israel) pricing is hard-locked and cannot be changed by the user.
    
    Parameters:
        user_id (str): The user's unique identifier.
        ip_address (str, optional): IP address for location lookup (if None, uses the requester's IP).
        pricing_option (str, optional): Pricing option ('weekly' or 'monthly'). Defaults to 'monthly'.
    
    Returns:
        dict: Contains user_id, location data, selected pricing option, and the calculated price.
    
    Raises:
        ValueError: If location data cannot be fetched.
    """
    location_data = get_user_location(ip_address)
    if not location_data:
        raise ValueError(f"Unable to fetch location data for user {user_id}. Please check the IP address.")
    
    pricing = get_pricing_by_region(location_data)
    
    # For users in special regions (e.g., Israel), the pricing is locked permanently.
    if is_user_in_special_region(location_data):  # Special region lock
        logger.info(f"User {user_id} is locked to Special Region pricing.")
    # Additional enforcement for SADC pricing can be added similarly if needed.
    
    # Calculate the price based on the chosen option (defaulting to monthly if not 'weekly')
    selected_plan = pricing_option.lower()
    if selected_plan not in ['monthly', 'weekly']:
        raise ValueError("Invalid pricing option. Expected 'monthly' or 'weekly'.")
    
    amount = pricing.get(selected_plan, pricing.get("monthly"))
    
    return {
        'user_id': user_id,
        'location': location_data,
        'pricing_option': selected_plan,
        'price': amount,
        'currency': pricing.get("currency", "USD")
    }

# ------------------------- TEST EXECUTION -------------------------

if __name__ == "__main__":
    test_user_id = "test_user"
    test_ip = "8.8.8.8"  # Example IP address; replace with a real IP for testing
    test_pricing_option = "monthly"  # or "weekly"
    
    try:
        pricing_details = get_user_pricing(test_user_id, test_ip, test_pricing_option)
        print("Pricing Details for User:", json.dumps(pricing_details, indent=4))
        
        # Example payment processing (uncomment one to test)
        # stripe_payment = process_payment(test_ip, "stripe", test_pricing_option)
        # paypal_payment = process_payment(test_ip, "paypal", test_pricing_option)
        # payfast_payment = process_payment(test_ip, "payfast", test_pricing_option)
        # print("Stripe Payment Intent/Client Secret:", stripe_payment)
        # print("PayPal Approval URL:", paypal_payment)
        # print("PayFast Payment URL:", payfast_payment)
    except Exception as e:\n         print(f"Error: {e}")

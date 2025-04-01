import os
import json
import logging
from geolocation_service import get_user_location, is_user_in_special_region

# Configure logging
logger = logging.getLogger("PricingService")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

# Define pricing tiers
REGIONAL_PRICING = {
    "IL": {  # Special Region (Israel) - Hard Locked
        "Creator": {"weekly": 35, "monthly": 99},
        "Pro": {"weekly": 99, "monthly": 499},
        "Enterprise": {"monthly": 699},
        "RLG Media Pack": {"monthly": 2500}
    },
    "SADC": {  # SADC Region Pricing
        "Creator": {"weekly": 8, "monthly": 30},
        "Pro": {"weekly": 15, "monthly": 59},
        "Enterprise": {"monthly": 299},
        "RLG Media Pack": {"monthly": 1500}
    },
    "DEFAULT": {  # Global Standard Pricing
        "Creator": {"weekly": 15, "monthly": 59},
        "Pro": {"weekly": 35, "monthly": 99},
        "Enterprise": {"monthly": 299},
        "RLG Media Pack": {"monthly": 1500}
    }
}

# SADC countries for region-based pricing
SADC_COUNTRIES = {"south africa", "botswana", "namibia", "zimbabwe", "mozambique", "zambia", "malawi", "lesotho", "eswatini", "angola", "democratic republic of congo", "tanzania"}


def get_pricing(location_data):
    """
    Determine pricing based on location.
    """
    if location_data is None:
        raise ValueError("Location data is required to determine pricing.")
    
    country = location_data.get("country", "").lower()
    
    if is_user_in_special_region(location_data):
        pricing = REGIONAL_PRICING["IL"]
        logger.debug("Applying special region pricing (Israel).")
    elif country in SADC_COUNTRIES:
        pricing = REGIONAL_PRICING["SADC"]
        logger.debug("Applying SADC regional pricing.")
    else:
        pricing = REGIONAL_PRICING["DEFAULT"]
        logger.debug("Applying global pricing.")
    
    return pricing


def get_user_pricing(user_id, ip_address=None):
    """
    Fetches user location and determines the pricing based on location.
    """
    location_data = get_user_location(ip_address)
    
    if not location_data:
        raise ValueError(f"Unable to fetch location data for user {user_id}. Please check the IP address.")
    
    pricing = get_pricing(location_data)
    
    return {
        'user_id': user_id,
        'location': location_data,
        'pricing': pricing
    }


# -------------------------------
# Testing Example
# -------------------------------
if __name__ == "__main__":
    user_id = "test_user"
    ip_address = "8.8.8.8"  # Example IP address; replace with actual user IP

    try:
        pricing_details = get_user_pricing(user_id, ip_address)
        print(f"Pricing for User {user_id}: {json.dumps(pricing_details, indent=4)}")
    except Exception as e:
        print(f"Error determining pricing: {e}")

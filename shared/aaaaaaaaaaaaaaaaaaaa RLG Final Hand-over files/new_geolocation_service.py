import requests
import json
import logging
import os

# Configure logging
logger = logging.getLogger("GeolocationService")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

# Base URL for IP geolocation API
IPINFO_URL = "https://ipinfo.io/"
IPINFO_TOKEN = os.getenv("IPINFO_TOKEN")  # Ensure this is set in your environment

# Define regional pricing tiers
REGIONAL_PRICING = {
    'IL': {
        'Creator': {'weekly': 35, 'monthly': 99},
        'Pro': {'weekly': 65, 'monthly': 199},
        'Enterprise': {'monthly': 699},
        'RLG Media Pack': {'monthly': 2500}
    },
    'SADC': {
        'Creator': {'weekly': 10, 'monthly': 49},
        'Pro': {'weekly': 25, 'monthly': 79},
        'Enterprise': {'monthly': 249},
        'RLG Media Pack': {'monthly': 1200}
    },
    'DEFAULT': {
        'Creator': {'weekly': 15, 'monthly': 59},
        'Pro': {'weekly': 30, 'monthly': 89},
        'Enterprise': {'monthly': 299},
        'RLG Media Pack': {'monthly': 1500}
    }
}

SADC_COUNTRIES = {'ZA', 'BW', 'NA', 'MZ', 'ZW', 'LS', 'SZ', 'AO', 'ZM', 'MW', 'CD', 'TZ', 'MG'}


def get_user_location(ip_address=None):
    """Fetches geolocation data using the IPINFO API."""
    url = f"{IPINFO_URL}{ip_address}/json?token={IPINFO_TOKEN}" if ip_address else f"{IPINFO_URL}json?token={IPINFO_TOKEN}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            'country': data.get('country'),
            'region': data.get('region'),
            'city': data.get('city'),
            'location': data.get('loc')
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching geolocation data: {e}")
        return None


def determine_pricing_tier(location_data):
    """Determines pricing tier based on user's country."""
    country = location_data.get('country') if location_data else None
    if country == 'IL':
        return REGIONAL_PRICING['IL']
    elif country in SADC_COUNTRIES:
        return REGIONAL_PRICING['SADC']
    return REGIONAL_PRICING['DEFAULT']


def enforce_location_lock(user_id, location_data):
    """Ensures users remain locked to their region-based pricing."""
    if not location_data:
        return False
    country = location_data.get('country')
    logger.info(f"User {user_id} locked to pricing based on country: {country}")
    return True


def register_user(user_id, ip_address=None):
    """Registers a user and applies location-based pricing."""
    location_data = get_user_location(ip_address)
    if location_data:
        enforce_location_lock(user_id, location_data)
        pricing = determine_pricing_tier(location_data)
        logger.info(f"User {user_id} registered with pricing: {pricing}")
        return pricing
    else:
        logger.error(f"Could not fetch location data for user {user_id}.")
        return None


if __name__ == "__main__":
    test_user = "test_user_001"
    test_ip = "8.8.8.8"
    pricing_info = register_user(test_user, test_ip)
    if pricing_info:
        logger.info(f"Final pricing for {test_user}: {json.dumps(pricing_info, indent=2)}")

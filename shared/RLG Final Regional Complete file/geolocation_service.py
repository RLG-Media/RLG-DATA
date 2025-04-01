"""
geolocation_service.py

This module provides geolocation-based services for the RLG Platform.
It uses the ipinfo.io API to retrieve location details based on an IP address,
and then applies location-based logic for pricing:

  - If the user is in a special region (for example, Israel, country code "IL"),
    a hard "Special Region" pricing lock is applied.
  - If the user is in one of the SADC countries, SADC pricing tiers are applied.
  - Otherwise, default pricing tiers are used.

Additional functionality includes:
  - Fetching geolocation data.
  - Determining if a user is in a special region (Israel) or in a SADC region.
  - Locking pricing for users in special regions (which is enforced after registration).
  - Retrieving dynamic pricing based on region, country, city, or town.

For production, API keys and sensitive configurations should be stored securely (e.g., in environment variables or a secrets manager).
"""

import requests
import json
import logging

# Configure logging
logger = logging.getLogger("GeolocationService")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

# Base URL for the ipinfo.io API (include an access token if required in production)
IPINFO_URL = "https://ipinfo.io/"

# List of SADC country codes (you can extend this list as needed)
SADC_COUNTRIES = {"ZA", "BW", "NA", "MZ", "ZW", "LS", "SZ", "AO", "ZM", "MW", "CD", "TZ", "MG"}

# Pricing tiers for each region
SPECIAL_REGION_PRICING = {  # For Israel
    'Creator': {'weekly': 35, 'monthly': 99},
    'Pro': {'weekly': 99, 'monthly': 499},
    'Enterprise': {'monthly': 699},
    'RLG Media Pack': {'monthly': 2500}
}
SADC_PRICING = {
    'Creator': {'weekly': 8, 'monthly': 30},
    'Pro': {'weekly': 15, 'monthly': 59},
    'Enterprise': {'monthly': 299},
    'RLG Media Pack': {'monthly': 1500}
}
DEFAULT_PRICING = {
    'Creator': {'weekly': 15, 'monthly': 59},
    'Pro': {'weekly': 35, 'monthly': 99},
    'Enterprise': {'monthly': 299},
    'RLG Media Pack': {'monthly': 2000}
}

# Dynamic pricing dictionary combines all tiers.
REGIONAL_PRICING = {
    'IL': SPECIAL_REGION_PRICING,
    'SADC': SADC_PRICING,
    'DEFAULT': DEFAULT_PRICING
}

def get_user_location(ip_address=None):
    """
    Fetches geolocation data based on IP address using the ipinfo.io API.

    Parameters:
        ip_address (str): Optional. If provided, fetch location for that IP; otherwise, use the requester's IP.

    Returns:
        dict or None: A dictionary containing location data:
            - 'country': Country code.
            - 'region': Region/state.
            - 'city': City.
            - 'location': Coordinates (latitude,longitude) as a string.
        Returns None if there was an error.
    """
    url = f"{IPINFO_URL}{ip_address}/json" if ip_address else f"{IPINFO_URL}json"
    try:
        logger.debug(f"Fetching geolocation data from: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        location_data = {
            'country': data.get('country'),
            'region': data.get('region'),
            'city': data.get('city'),
            'location': data.get('loc')  # Typically "latitude,longitude"
        }
        logger.debug(f"Retrieved location data: {location_data}")
        return location_data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching geolocation data: {e}")
        return None
    except ValueError as e:
        logger.error(f"Error parsing geolocation response: {e}")
        return None

def is_user_in_special_region(location_data):
    """
    Determines if the user is in a special region (Israel).

    Parameters:
        location_data (dict): The geolocation data.

    Returns:
        bool: True if the user is in Israel (special region), False otherwise.
    """
    if location_data and location_data.get('country') == 'IL':
        logger.debug("User is in the special region (Israel).")
        return True
    logger.debug("User is not in the special region (Israel).")
    return False

def is_user_in_sadc_region(location_data):
    """
    Determines if the user is in one of the SADC countries.

    Parameters:
        location_data (dict): The geolocation data.

    Returns:
        bool: True if the user's country is in the SADC region, False otherwise.
    """
    if location_data and location_data.get('country') in SADC_COUNTRIES:
        logger.debug("User is in a SADC region.")
        return True
    logger.debug("User is not in a SADC region.")
    return False

def lock_special_region_pricing(user_id, location_data):
    """
    Locks the pricing for users in special regions (Israel).

    Parameters:
        user_id (str): The user's unique identifier.
        location_data (dict): The geolocation data.

    Returns:
        bool: True if the user is locked to special region pricing, False otherwise.
    """
    if is_user_in_special_region(location_data):
        user_pricing = {
            'user_id': user_id,
            'pricing_tier': 'Special Region',
            'pricing': SPECIAL_REGION_PRICING
        }
        logger.info(f"User {user_id} locked to Special Region pricing: {json.dumps(user_pricing)}")
        return True
    logger.info(f"User {user_id} is not in the Special Region. No pricing lock applied.")
    return False

def get_pricing(location_data):
    """
    Retrieves the pricing structure based on the user's location.

    Parameters:
        location_data (dict): The geolocation data.

    Returns:
        dict: A dictionary representing the pricing tiers.
    """
    if is_user_in_special_region(location_data):
        logger.debug("Applying special region (Israel) pricing.")
        return SPECIAL_REGION_PRICING
    elif is_user_in_sadc_region(location_data):
        logger.debug("Applying SADC region pricing.")
        return SADC_PRICING
    else:
        logger.debug("Applying default global pricing.")
        return DEFAULT_PRICING

def get_dynamic_pricing(location_data):
    """
    Retrieves dynamic pricing based on the user's country code.

    Parameters:
        location_data (dict): The geolocation data.

    Returns:
        dict: Pricing tiers for the specific region if available; otherwise, returns default pricing.
    """
    if not location_data or 'country' not in location_data:
        return REGIONAL_PRICING['DEFAULT']
    
    country = location_data.get('country')
    if country == 'IL':
        pricing = REGIONAL_PRICING['IL']
    elif country in SADC_COUNTRIES:
        pricing = REGIONAL_PRICING['SADC']
    else:
        pricing = REGIONAL_PRICING['DEFAULT']
    
    logger.debug(f"Dynamic pricing for country {country}: {pricing}")
    return pricing

def register_user(user_id, ip_address=None):
    """
    Registers a user with location-based pricing.

    This function fetches the user's geolocation data based on the provided IP address,
    enforces pricing locks if the user is in a special region, and returns the pricing structure.
    Note: The pricing page is only available after registration so that the user's location is locked and pricing is enforced accordingly.

    Parameters:
        user_id (str): The user's unique identifier.
        ip_address (str): Optional. The IP address to use for geolocation. If None, the API returns data for the requesting IP.

    Returns:
        dict or None: The pricing structure applied to the user, or None if location data could not be fetched.
    """
    location_data = get_user_location(ip_address)
    if location_data:
        # Lock pricing if in special region (Israel) or SADC region
        if is_user_in_special_region(location_data) or is_user_in_sadc_region(location_data):
            # For special regions, enforce a permanent pricing lock:
            enforce_special_region_lock(user_id, location_data)
            lock_special_region_pricing(user_id, location_data)
        pricing = get_pricing(location_data)
        logger.info(f"User {user_id} registered with pricing: {pricing}")
        return pricing
    else:
        logger.error(f"Error fetching location data for user {user_id}.")
        return None

def enforce_special_region_lock(user_id, location_data):
    """
    Enforces that the user remains permanently locked to region-specific pricing if identified as in a special region.
    
    For example, if a user is identified as being in Israel (special region), their pricing cannot be changed.
    
    Parameters:
        user_id (str): The user's unique identifier.
        location_data (dict): The geolocation data.
    
    Returns:
        bool: True if the user is permanently locked to region-specific pricing, False otherwise.
    """
    if is_user_in_special_region(location_data): 
        logger.info(f"User {user_id} is permanently locked to Special Region pricing due to location in Israel.")
        return True
    # For SADC or other regions, you may decide on a policy; for now, we'll allow dynamic updates.
    logger.info(f"User {user_id} is not permanently locked to a special region pricing.")
    return False

if __name__ == "__main__":
    # For standalone testing, use a sample user ID and IP address.
    user_id = "user123"
    ip_address = "8.8.8.8"  # Example IP address; replace with a real IP for testing.
    pricing_info = register_user(user_id, ip_address)
    if pricing_info:
        logger.info(f"Final pricing for user {user_id}: {json.dumps(pricing_info)}")
    else:
        logger.error("Failed to determine pricing for the user.")

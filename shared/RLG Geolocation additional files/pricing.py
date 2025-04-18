import os
from geolocation_service import get_user_location, is_user_in_special_region

def get_pricing(location_data, pricing_option):
    """
    Determine pricing based on location and selected pricing option (monthly or weekly).
    Supports:
    - Special regions (e.g., Israel)
    - Africa & SADC region pricing
    - Default global pricing

    Args:
        location_data (dict): User's location data containing country, region, city, etc.
        pricing_option (str): Selected pricing tier ('monthly' or 'weekly').

    Returns:
        float: The pricing value based on location and selected tier.

    Raises:
        ValueError: If location data is missing or pricing option is invalid.
    """
    if location_data is None:
        raise ValueError("Location data is required to determine pricing.")
    
    pricing_option = pricing_option.lower()
    if pricing_option not in ['monthly', 'weekly']:
        raise ValueError(f"Invalid pricing option: {pricing_option}. Expected 'monthly' or 'weekly'.")
    
    country = location_data.get("country", "").lower()
    
    # Special pricing for locked regions (e.g., Israel)
    if is_user_in_special_region(location_data):
        return 99 if pricing_option == 'monthly' else 35
    
    # Africa & SADC Region Pricing
    africa_sadc_countries = {"south africa", "botswana", "namibia", "zimbabwe", "mozambique", "zambia", "malawi", "lesotho", "eswatini", "angola", "democratic republic of congo", "tanzania"}
    if country in africa_sadc_countries:
        return 49 if pricing_option == 'monthly' else 12
    
    # Global Standard Pricing
    return 59 if pricing_option == 'monthly' else 15

def get_user_pricing(user_id, ip_address=None, pricing_option='monthly'):
    """
    Fetches user location and determines the pricing based on location and selected pricing option.

    Args:
        user_id (str): The ID of the user requesting pricing.
        ip_address (str, optional): IP address for location lookup. Defaults to None.
        pricing_option (str, optional): The pricing option ('monthly' or 'weekly'). Defaults to 'monthly'.

    Returns:
        dict: Pricing details for the user, including location and pricing value.

    Raises:
        ValueError: If location data cannot be fetched.
    """
    location_data = get_user_location(ip_address)
    
    if not location_data:
        raise ValueError(f"Unable to fetch location data for user {user_id}. Please check the IP address.")
    
    price = get_pricing(location_data, pricing_option)
    
    return {
        'user_id': user_id,
        'location': location_data,
        'pricing_option': pricing_option,
        'price': price
    }

# -------------------------------
# Testing Example
# -------------------------------
if __name__ == "__main__":
    user_id = "test_user"
    ip_address = "8.8.8.8"  # Example IP address; replace with actual user IP
    pricing_option = "monthly"  # or "weekly"

    try:
        pricing_details = get_user_pricing(user_id, ip_address, pricing_option)
        print(f"Pricing for User {user_id}: {pricing_details}")
    except Exception as e:
        print(f"Error determining pricing: {e}")

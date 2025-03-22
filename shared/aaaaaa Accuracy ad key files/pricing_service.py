from typing import Dict, Optional
import ipaddress
import requests
from datetime import datetime


class PricingService:
    """
    PricingService manages pricing tiers and handles geographical pricing rules
    for RLG Data and RLG Fans.
    """

    def __init__(self, default_pricing: Dict[str, Dict[str, float]], regional_pricing: Dict[str, Dict[str, Dict[str, float]]]):
        """
        Initialize the PricingService.

        Args:
            default_pricing (dict): Default pricing tiers (monthly and weekly) by tier name.
            regional_pricing (dict): Pricing tiers specific to regions, with tier details.
        """
        self.default_pricing = default_pricing
        self.regional_pricing = regional_pricing

    def get_pricing_by_region(self, ip_address: str) -> Optional[Dict[str, Dict[str, float]]]:
        """
        Retrieve pricing based on the user's geographical location.

        Args:
            ip_address (str): IP address of the user.

        Returns:
            dict: Pricing information for the region, or default pricing if no specific region is found.
        """
        region = self._get_region_by_ip(ip_address)
        if region in self.regional_pricing:
            print(f"[{datetime.now()}] Pricing determined for region: {region}")
            return self.regional_pricing[region]
        print(f"[{datetime.now()}] Default pricing applied for IP: {ip_address}")
        return self.default_pricing

    def _get_region_by_ip(self, ip_address: str) -> Optional[str]:
        """
        Determine the region based on an IP address using a geolocation API.

        Args:
            ip_address (str): IP address to determine the region.

        Returns:
            str: The region or None if determination fails.
        """
        try:
            # Example API URL: Replace with a valid geolocation service
            api_url = f"https://ip-geolocation-api.com/{ip_address}"
            response = requests.get(api_url)
            response_data = response.json()

            if response.status_code == 200:
                country = response_data.get("country_code")
                print(f"[{datetime.now()}] IP {ip_address} resolved to region: {country}")
                return country
            else:
                print(f"[{datetime.now()}] Failed to resolve IP: {ip_address}, Response: {response.status_code}")
        except Exception as e:
            print(f"[{datetime.now()}] Error in geolocation service: {e}")
        return None

    def validate_pricing_tier(self, region: str, tier_name: str) -> bool:
        """
        Validate the pricing tier based on the region.

        Args:
            region (str): The region to validate against.
            tier_name (str): The selected pricing tier (e.g., 'CREATOR', 'PRO').

        Returns:
            bool: True if valid, False otherwise.
        """
        region_pricing = self.regional_pricing.get(region, self.default_pricing)
        is_valid = tier_name in region_pricing
        if is_valid:
            print(f"[{datetime.now()}] Valid pricing tier '{tier_name}' for region '{region}'.")
        else:
            print(f"[{datetime.now()}] Invalid pricing tier '{tier_name}' for region '{region}'.")
        return is_valid

    def apply_pricing_lock(self, user_id: str, region: str, tier_name: str) -> bool:
        """
        Lock the user's pricing to a specific region and tier.

        Args:
            user_id (str): The user ID.
            region (str): The region to lock pricing.
            tier_name (str): The pricing tier to lock.

        Returns:
            bool: True if lock is successful, False otherwise.
        """
        if not self.validate_pricing_tier(region, tier_name):
            print(f"[{datetime.now()}] Failed to lock pricing: Invalid tier '{tier_name}' for region '{region}'.")
            return False

        # Simulating database write operation
        print(f"[{datetime.now()}] Pricing locked for user {user_id}: Region='{region}', Tier='{tier_name}'.")
        # Logic to store this information in a database would go here.
        return True


# Example Usage
if __name__ == "__main__":
    # Define default and regional pricing tiers
    default_pricing = {
        "CREATOR": {"weekly": 15.0, "monthly": 59.0},
        "PRO": {"weekly": 40.0, "monthly": 159.0},
        "ENTERPRISE": {"monthly": 399.0},
        "RLG Media Pack": {"monthly": 1500.0}
    }

    regional_pricing = {
        "IL": {
            "CREATOR": {"weekly": 35.0, "monthly": 99.0},
            "PRO": {"weekly": 65.0, "monthly": 199.0},
            "ENTERPRISE": {"monthly": 699.0},
            "RLG Media Pack": {"monthly": 2500.0}
        },
        "US": default_pricing  # Example region inherits default pricing
    }

    # Initialize the pricing service
    pricing_service = PricingService(default_pricing, regional_pricing)

    # Example IPs and usage
    test_ip = "8.8.8.8"  # Replace with a valid test IP address
    pricing = pricing_service.get_pricing_by_region(test_ip)
    print(f"Pricing for IP {test_ip}: {pricing}")

    # Lock pricing for a user
    pricing_service.apply_pricing_lock("user123", "IL", "CREATOR")

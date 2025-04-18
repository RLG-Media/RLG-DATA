import logging
from typing import Dict, List, Optional
import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("geo_targeting_services.log"),
        logging.StreamHandler()
    ]
)

class GeoTargetingService:
    """
    Service class for managing geo-targeting functionality for RLG Data and RLG Fans.
    Includes IP-based location tracking, region-specific targeting, and content personalization.
    """

    def __init__(self):
        self.geolocator = Nominatim(user_agent="rlg_geo_targeting")
        logging.info("GeoTargetingService initialized.")

    def get_location_by_ip(self, ip_address: str) -> Optional[Dict[str, str]]:
        """
        Get geographical location details based on IP address.

        Args:
            ip_address (str): The IP address of the user.

        Returns:
            Optional[Dict[str, str]]: A dictionary containing location details (country, region, city, etc.), or None if failed.
        """
        try:
            response = requests.get(f"https://ipapi.co/{ip_address}/json/")
            if response.status_code == 200:
                data = response.json()
                location = {
                    "ip": ip_address,
                    "country": data.get("country_name"),
                    "country_code": data.get("country"),
                    "region": data.get("region"),
                    "city": data.get("city"),
                    "latitude": data.get("latitude"),
                    "longitude": data.get("longitude")
                }
                logging.info("Location fetched for IP %s: %s", ip_address, location)
                return location
            else:
                logging.error("Failed to fetch location for IP %s: %s", ip_address, response.text)
                return None
        except requests.RequestException as e:
            logging.error("Error fetching location for IP %s: %s", ip_address, e)
            return None

    def get_location_by_coordinates(self, latitude: float, longitude: float) -> Optional[Dict[str, str]]:
        """
        Get location details based on geographical coordinates.

        Args:
            latitude (float): Latitude of the location.
            longitude (float): Longitude of the location.

        Returns:
            Optional[Dict[str, str]]: A dictionary containing location details (country, region, city, etc.), or None if failed.
        """
        try:
            location = self.geolocator.reverse((latitude, longitude), timeout=10)
            if location and location.raw:
                address = location.raw.get("address", {})
                location_details = {
                    "country": address.get("country"),
                    "country_code": address.get("country_code"),
                    "region": address.get("state"),
                    "city": address.get("city", address.get("town"))
                }
                logging.info("Location fetched for coordinates (%f, %f): %s", latitude, longitude, location_details)
                return location_details
            else:
                logging.error("Failed to fetch location for coordinates (%f, %f)", latitude, longitude)
                return None
        except GeocoderTimedOut as e:
            logging.error("Geocoder timed out for coordinates (%f, %f): %s", latitude, longitude, e)
            return None

    def target_content_by_region(self, location_data: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Target content based on the user's geographical region.

        Args:
            location_data (Dict[str, str]): The location details of the user.

        Returns:
            Dict[str, List[str]]: A dictionary of region-specific content suggestions.
        """
        region = location_data.get("region")
        country = location_data.get("country")

        # Example of region-specific content targeting
        content = {
            "South Africa": ["Local News", "Community Events", "Trending Topics in South Africa"],
            "United States": ["Global Trends", "Tech Innovations", "Sports Highlights"],
            "Israel": ["Regional News", "Technology Updates", "Finance Reports"]
        }

        default_content = ["Global News", "International Trends", "Top Stories"]
        targeted_content = content.get(region) or content.get(country) or default_content

        logging.info("Content targeted for region %s, country %s: %s", region, country, targeted_content)
        return {"targeted_content": targeted_content}

    def integrate_social_media_platforms(self, location_data: Dict[str, str]) -> Dict[str, str]:
        """
        Suggest social media platforms based on the user's region.

        Args:
            location_data (Dict[str, str]): The location details of the user.

        Returns:
            Dict[str, str]: Recommended social media platforms for the user's region.
        """
        region = location_data.get("region")
        country = location_data.get("country")

        platform_recommendations = {
            "South Africa": "Twitter, Facebook, Instagram",
            "United States": "TikTok, LinkedIn, Reddit",
            "Israel": "Threads, Snapchat, Pinterest"
        }

        default_platforms = "Global Platforms: Twitter, LinkedIn, Facebook, Instagram"
        recommendations = platform_recommendations.get(region) or platform_recommendations.get(country) or default_platforms

        logging.info("Social media platform recommendations for region %s, country %s: %s", region, country, recommendations)
        return {"recommended_platforms": recommendations}

# Example usage
if __name__ == "__main__":
    geo_service = GeoTargetingService()

    # Fetch location by IP
    location = geo_service.get_location_by_ip("8.8.8.8")
    if location:
        print("Location:", location)

        # Target content by region
        content = geo_service.target_content_by_region(location)
        print("Targeted Content:", content)

        # Recommend social media platforms
        platforms = geo_service.integrate_social_media_platforms(location)
        print("Recommended Platforms:", platforms)

    # Fetch location by coordinates
    location_coords = geo_service.get_location_by_coordinates(-33.9249, 18.4241)  # Cape Town, South Africa
    if location_coords:
        print("Location by Coordinates:", location_coords)

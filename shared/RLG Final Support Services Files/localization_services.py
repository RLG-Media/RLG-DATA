import logging
import requests
from typing import Dict, Optional
from datetime import datetime
from babel.dates import format_date, format_datetime

# Configure logging if not already configured by your application.
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class LocalizationService:
    """
    Service class to manage localization and internationalization.

    Features:
      - Detect location details (region, country, city, town) using an IP geolocation API.
      - Format dates and datetimes according to a given locale using Babel.
      - Retrieve basic translations for common keys (stub implementation).
    """

    def __init__(self, default_locale: str = "en_US") -> None:
        """
        Initialize the LocalizationService with a default locale.

        Args:
            default_locale (str): The default locale (e.g., "en_US").
        """
        self.default_locale = default_locale
        # For production, you can extend this to load translations from files.
        self.translation_dict = {
            "en_US": {"welcome": "Welcome", "goodbye": "Goodbye"},
            "es_ES": {"welcome": "Bienvenido", "goodbye": "Adiós"},
        }
        logger.info("LocalizationService initialized with default locale: %s", self.default_locale)

    def detect_location(self, ip_address: str) -> Dict[str, Optional[str]]:
        """
        Detect location details (region, country, city, town) based on an IP address.

        Uses the ipapi.co service to fetch location information.

        Args:
            ip_address (str): The IP address to geolocate.

        Returns:
            Dict[str, Optional[str]]: A dictionary with keys: 'region', 'country', 'city', 'town'.
        """
        try:
            url = f"https://ipapi.co/{ip_address}/json/"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            location = {
                "region": data.get("region"),
                "country": data.get("country_name"),
                "city": data.get("city"),
                "town": data.get("region")  # Fallback; replace with actual town if available.
            }
            logger.info("Detected location for IP %s: %s", ip_address, location)
            return location
        except Exception as e:
            logger.error("Error detecting location for IP %s: %s", ip_address, e)
            return {"region": None, "country": None, "city": None, "town": None}

    def format_date(self, date_obj: datetime, locale: Optional[str] = None) -> str:
        """
        Format a datetime object into a localized date string.

        Args:
            date_obj (datetime): The date to format.
            locale (Optional[str]): Locale code (e.g., "en_US"); defaults to the service default.

        Returns:
            str: The formatted date string.
        """
        try:
            loc = locale if locale else self.default_locale
            formatted = format_date(date_obj, format="long", locale=loc)
            logger.info("Formatted date %s with locale %s: %s", date_obj, loc, formatted)
            return formatted
        except Exception as e:
            logger.error("Error formatting date %s: %s", date_obj, e)
            return str(date_obj)

    def format_datetime(self, date_obj: datetime, locale: Optional[str] = None) -> str:
        """
        Format a datetime object into a localized datetime string.

        Args:
            date_obj (datetime): The datetime to format.
            locale (Optional[str]): Locale code (e.g., "en_US"); defaults to the service default.

        Returns:
            str: The formatted datetime string.
        """
        try:
            loc = locale if locale else self.default_locale
            formatted = format_datetime(date_obj, format="medium", locale=loc)
            logger.info("Formatted datetime %s with locale %s: %s", date_obj, loc, formatted)
            return formatted
        except Exception as e:
            logger.error("Error formatting datetime %s: %s", date_obj, e)
            return str(date_obj)

    def get_translation(self, key: str, locale: Optional[str] = None) -> str:
        """
        Retrieve a translation for a given key and locale.
        
        This basic implementation uses an internal dictionary; for production,
        integrate with Flask-Babel or load translations from external files.

        Args:
            key (str): The text key to translate.
            locale (Optional[str]): Locale code (e.g., "en_US"); defaults to the service default.

        Returns:
            str: The translated text, or the key itself if not found.
        """
        try:
            loc = locale if locale else self.default_locale
            translation = self.translation_dict.get(loc, {}).get(key, key)
            logger.info("Translation for key '%s' in locale %s: %s", key, loc, translation)
            return translation
        except Exception as e:
            logger.error("Error retrieving translation for key '%s': %s", key, e)
            return key

# -------------------------------
# Example Usage (for testing purposes)
# -------------------------------
if __name__ == "__main__":
    service = LocalizationService(default_locale="en_US")

    # Detect location from an example IP address.
    ip = "8.8.8.8"
    location = service.detect_location(ip)
    print("Detected Location:", location)

    # Format current date and datetime.
    now = datetime.utcnow()
    print("Formatted Date (en_US):", service.format_date(now, locale="en_US"))
    print("Formatted Date (es_ES):", service.format_date(now, locale="es_ES"))
    print("Formatted Datetime (en_US):", service.format_datetime(now, locale="en_US"))

    # Retrieve translations.
    print("Translation for 'welcome' in en_US:", service.get_translation("welcome", locale="en_US"))
    print("Translation for 'welcome' in es_ES:", service.get_translation("welcome", locale="es_ES"))

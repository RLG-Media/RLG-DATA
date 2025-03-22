import json
import os
from typing import Dict, Any, Optional

# File-based storage for simplicity; replace with database in production
SETTINGS_FILE = "brand_settings.json"


class BrandSettingsManager:
    """
    Manages brand-specific settings for RLG Data and RLG Fans.
    """

    def __init__(self):
        """
        Initialize the BrandSettingsManager.
        Loads existing settings from the storage file or initializes an empty structure.
        """
        self.settings = self._load_settings()

    def _load_settings(self) -> Dict[str, Any]:
        """
        Load brand settings from the JSON file.
        :return: A dictionary of brand settings.
        """
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as file:
                return json.load(file)
        return {}

    def _save_settings(self):
        """
        Save brand settings to the JSON file.
        """
        with open(SETTINGS_FILE, "w") as file:
            json.dump(self.settings, file, indent=4)

    def add_brand(self, brand_name: str, settings: Dict[str, Any]):
        """
        Add a new brand with its settings.
        :param brand_name: Name of the brand.
        :param settings: A dictionary of settings for the brand.
        """
        if brand_name in self.settings:
            raise ValueError(f"Brand '{brand_name}' already exists.")
        self.settings[brand_name] = settings
        self._save_settings()
        print(f"Brand '{brand_name}' added successfully.")

    def update_brand(self, brand_name: str, settings: Dict[str, Any]):
        """
        Update settings for an existing brand.
        :param brand_name: Name of the brand.
        :param settings: A dictionary of updated settings.
        """
        if brand_name not in self.settings:
            raise ValueError(f"Brand '{brand_name}' does not exist.")
        self.settings[brand_name].update(settings)
        self._save_settings()
        print(f"Brand '{brand_name}' updated successfully.")

    def delete_brand(self, brand_name: str):
        """
        Delete a brand and its settings.
        :param brand_name: Name of the brand.
        """
        if brand_name not in self.settings:
            raise ValueError(f"Brand '{brand_name}' does not exist.")
        del self.settings[brand_name]
        self._save_settings()
        print(f"Brand '{brand_name}' deleted successfully.")

    def get_brand_settings(self, brand_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve settings for a specific brand.
        :param brand_name: Name of the brand.
        :return: A dictionary of brand settings or None if the brand doesn't exist.
        """
        return self.settings.get(brand_name)

    def list_brands(self) -> Dict[str, Any]:
        """
        List all available brands and their settings.
        :return: A dictionary of all brand settings.
        """
        return self.settings


# Example Usage
if __name__ == "__main__":
    manager = BrandSettingsManager()

    # Add a new brand
    manager.add_brand(
        "BrandA",
        {
            "logo_url": "https://example.com/logo.png",
            "primary_color": "#FF5733",
            "secondary_color": "#C70039",
            "theme": "dark",
            "social_media": {
                "facebook": "https://facebook.com/brandA",
                "twitter": "https://twitter.com/brandA",
                "instagram": "https://instagram.com/brandA",
            },
            "content_guidelines": {
                "tone": "professional",
                "language": "English",
                "avoid": ["controversial topics", "slang"],
            },
            "analytics_preferences": {
                "kpis": ["engagement_rate", "conversion_rate", "brand_mentions"],
            },
        },
    )

    # Update an existing brand
    manager.update_brand(
        "BrandA",
        {
            "primary_color": "#FF4500",
            "analytics_preferences": {
                "kpis": ["audience_growth", "positive_sentiment"],
            },
        },
    )

    # Retrieve brand settings
    settings = manager.get_brand_settings("BrandA")
    print("Brand Settings:", settings)

    # List all brands
    brands = manager.list_brands()
    print("All Brands:", brands)

    # Delete a brand
    manager.delete_brand("BrandA")
    print("All Brands After Deletion:", manager.list_brands())

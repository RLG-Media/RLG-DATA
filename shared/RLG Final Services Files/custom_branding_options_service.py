import os
import logging
from typing import Dict, Optional
from PIL import Image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("custom_branding.log"),
        logging.StreamHandler()
    ]
)

class CustomBrandingOptionsService:
    """
    Service class to manage custom branding options for RLG Data and RLG Fans.
    Includes functionalities for logo uploads, color scheme customization, and font preferences.
    """

    def __init__(self, storage_path: str = "branding_assets"):
        """
        Initialize the CustomBrandingOptionsService.

        Args:
            storage_path (str): Directory to store uploaded branding assets.
        """
        self.storage_path = storage_path
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
        logging.info("CustomBrandingOptionsService initialized with storage path: %s", self.storage_path)

    def upload_logo(self, user_id: str, logo_file: bytes, file_name: str) -> str:
        """
        Upload and save a custom logo for a user.

        Args:
            user_id (str): The ID of the user uploading the logo.
            logo_file (bytes): The file data of the logo.
            file_name (str): The name of the file being uploaded.

        Returns:
            str: The path to the saved logo file.
        """
        user_dir = os.path.join(self.storage_path, user_id)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)

        file_path = os.path.join(user_dir, file_name)
        try:
            with open(file_path, "wb") as f:
                f.write(logo_file)
            logging.info("Logo uploaded successfully for user %s: %s", user_id, file_path)
            return file_path
        except Exception as e:
            logging.error("Failed to upload logo for user %s: %s", user_id, e)
            raise

    def validate_logo(self, file_path: str) -> bool:
        """
        Validate the uploaded logo for size and format.

        Args:
            file_path (str): Path to the uploaded logo file.

        Returns:
            bool: True if the logo is valid, False otherwise.
        """
        try:
            with Image.open(file_path) as img:
                if img.format not in ["PNG", "JPEG"]:
                    logging.error("Invalid logo format: %s", img.format)
                    return False
                if img.size[0] > 1024 or img.size[1] > 1024:
                    logging.error("Logo dimensions exceed 1024x1024 pixels: %s", img.size)
                    return False
            logging.info("Logo validated successfully: %s", file_path)
            return True
        except Exception as e:
            logging.error("Failed to validate logo: %s", e)
            return False

    def set_color_scheme(self, user_id: str, color_scheme: Dict[str, str]) -> None:
        """
        Save the custom color scheme for a user.

        Args:
            user_id (str): The ID of the user setting the color scheme.
            color_scheme (Dict[str, str]): A dictionary of color variables and their values.
        """
        user_dir = os.path.join(self.storage_path, user_id)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)

        file_path = os.path.join(user_dir, "color_scheme.json")
        try:
            with open(file_path, "w") as f:
                import json
                json.dump(color_scheme, f, indent=4)
            logging.info("Color scheme saved for user %s: %s", user_id, file_path)
        except Exception as e:
            logging.error("Failed to save color scheme for user %s: %s", user_id, e)
            raise

    def set_font_preferences(self, user_id: str, font_preferences: Dict[str, str]) -> None:
        """
        Save the custom font preferences for a user.

        Args:
            user_id (str): The ID of the user setting the font preferences.
            font_preferences (Dict[str, str]): A dictionary of font settings (e.g., font family, size).
        """
        user_dir = os.path.join(self.storage_path, user_id)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)

        file_path = os.path.join(user_dir, "font_preferences.json")
        try:
            with open(file_path, "w") as f:
                import json
                json.dump(font_preferences, f, indent=4)
            logging.info("Font preferences saved for user %s: %s", user_id, file_path)
        except Exception as e:
            logging.error("Failed to save font preferences for user %s: %s", user_id, e)
            raise

    def get_branding_settings(self, user_id: str) -> Dict[str, Optional[str]]:
        """
        Retrieve all branding settings for a user.

        Args:
            user_id (str): The ID of the user.

        Returns:
            Dict[str, Optional[str]]: A dictionary containing the user's branding settings.
        """
        user_dir = os.path.join(self.storage_path, user_id)
        if not os.path.exists(user_dir):
            logging.info("No branding settings found for user %s", user_id)
            return {}

        settings = {}

        # Retrieve logo
        logo_path = next((f for f in os.listdir(user_dir) if f.endswith(('.png', '.jpg', '.jpeg'))), None)
        if logo_path:
            settings["logo"] = os.path.join(user_dir, logo_path)

        # Retrieve color scheme
        color_scheme_path = os.path.join(user_dir, "color_scheme.json")
        if os.path.exists(color_scheme_path):
            with open(color_scheme_path, "r") as f:
                import json
                settings["color_scheme"] = json.load(f)

        # Retrieve font preferences
        font_preferences_path = os.path.join(user_dir, "font_preferences.json")
        if os.path.exists(font_preferences_path):
            with open(font_preferences_path, "r") as f:
                import json
                settings["font_preferences"] = json.load(f)

        logging.info("Branding settings retrieved for user %s", user_id)
        return settings

# Example usage
if __name__ == "__main__":
    branding_service = CustomBrandingOptionsService()

    user_id = "user123"

    # Upload logo
    logo_path = branding_service.upload_logo(user_id, b"dummy_logo_data", "logo.png")
    if branding_service.validate_logo(logo_path):
        print(f"Logo uploaded and validated: {logo_path}")

    # Set color scheme
    branding_service.set_color_scheme(user_id, {"primary": "#000000", "secondary": "#FFFFFF"})

    # Set font preferences
    branding_service.set_font_preferences(user_id, {"font_family": "Arial", "font_size": "14px"})

    # Retrieve settings
    settings = branding_service.get_branding_settings(user_id)
    print("Branding settings:", settings)

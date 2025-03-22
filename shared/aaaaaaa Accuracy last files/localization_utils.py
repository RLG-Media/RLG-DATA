"""
localization_utils.py
Provides utilities for handling localization, translations, and formatting.
Supports multilingual content for RLG Data and RLG Fans.
"""

import os
import logging
from typing import Dict, Optional
from babel import Locale, dates, numbers
from babel.support import Translations

# Logger setup
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Constants
DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = ["en", "es", "fr", "de", "zh", "ja", "ar"]
TRANSLATIONS_DIR = "translations"

class LocalizationUtils:
    def __init__(self, default_language: str = DEFAULT_LANGUAGE):
        self.default_language = default_language
        self.current_language = default_language
        self.translations_cache = {}
        self._load_translations()

    def _load_translations(self) -> None:
        """
        Preloads translation files for supported languages.
        """
        for lang in SUPPORTED_LANGUAGES:
            try:
                lang_dir = os.path.join(TRANSLATIONS_DIR, lang, "LC_MESSAGES")
                self.translations_cache[lang] = Translations.load(lang_dir, domain="messages")
                logger.info(f"Loaded translations for language: {lang}")
            except Exception as e:
                logger.warning(f"Could not load translations for {lang}: {str(e)}")

    def set_language(self, language: str) -> None:
        """
        Sets the current language for localization.

        Args:
            language (str): Language code (e.g., 'en', 'es').

        Raises:
            ValueError: If the language is not supported.
        """
        if language not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Language '{language}' is not supported.")
        self.current_language = language
        logger.info(f"Language set to: {language}")

    def translate(self, text: str) -> str:
        """
        Translates a given text to the current language.

        Args:
            text (str): Text to be translated.

        Returns:
            str: Translated text.
        """
        try:
            translation = self.translations_cache[self.current_language].gettext(text)
            return translation
        except KeyError:
            logger.warning(f"No translation found for language: {self.current_language}")
            return text  # Fallback to original text

    def format_date(self, date_obj, format_type: str = "medium") -> str:
        """
        Formats a date object according to the current language.

        Args:
            date_obj (datetime): The date to format.
            format_type (str): The format type ('short', 'medium', 'long', 'full').

        Returns:
            str: Formatted date string.
        """
        try:
            locale = Locale.parse(self.current_language)
            formatted_date = dates.format_date(date_obj, format=format_type, locale=locale)
            return formatted_date
        except Exception as e:
            logger.error(f"Error formatting date: {str(e)}")
            return str(date_obj)  # Fallback to default string representation

    def format_currency(self, value: float, currency_code: str = "USD") -> str:
        """
        Formats a currency value according to the current language.

        Args:
            value (float): The monetary value to format.
            currency_code (str): The ISO 4217 currency code (e.g., 'USD', 'EUR').

        Returns:
            str: Formatted currency string.
        """
        try:
            locale = Locale.parse(self.current_language)
            formatted_currency = numbers.format_currency(value, currency_code, locale=locale)
            return formatted_currency
        except Exception as e:
            logger.error(f"Error formatting currency: {str(e)}")
            return f"{value} {currency_code}"  # Fallback

    def format_number(self, number: float) -> str:
        """
        Formats a number according to the current language.

        Args:
            number (float): The number to format.

        Returns:
            str: Formatted number string.
        """
        try:
            locale = Locale.parse(self.current_language)
            formatted_number = numbers.format_decimal(number, locale=locale)
            return formatted_number
        except Exception as e:
            logger.error(f"Error formatting number: {str(e)}")
            return str(number)  # Fallback to default string representation

    def localize_content(self, content: Dict[str, str]) -> str:
        """
        Retrieves localized content for the current language.

        Args:
            content (Dict[str, str]): A dictionary with language keys and localized content values.

        Returns:
            str: Localized content for the current language.
        """
        return content.get(self.current_language, content.get(DEFAULT_LANGUAGE, ""))

# Example Usage
if __name__ == "__main__":
    # Initialize localization utility
    localization = LocalizationUtils()

    # Set language
    localization.set_language("es")

    # Translate text
    print(localization.translate("Welcome to RLG Data!"))

    # Format date
    from datetime import datetime
    current_date = datetime.now()
    print(localization.format_date(current_date, format_type="full"))

    # Format currency
    print(localization.format_currency(12345.67, "EUR"))

    # Format number
    print(localization.format_number(1234567.89))

    # Localize content example
    content = {
        "en": "Hello!",
        "es": "¡Hola!",
        "fr": "Bonjour!"
    }
    print(localization.localize_content(content))

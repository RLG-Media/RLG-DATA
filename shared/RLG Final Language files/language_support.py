"""
language_support.py

Multi-language and Regional Localization Support for RLG Data & RLG Fans

This module provides support for:
- Internationalization (i18n) of UI strings, error messages, and tool features.
- Region and pricing-based dynamic content switching.
- Localization of reports, chatbot, newsletter, monetization, AI tools, etc.
- Locked pricing display for special regions like Israel.
"""

import os
from typing import Dict

# Default supported languages
SUPPORTED_LANGUAGES = {
    "en": "English",
    "fr": "French",
    "es": "Spanish",
    "pt": "Portuguese",
    "sw": "Swahili",
    "he": "Hebrew",
    "de": "German",
    "zh": "Chinese",
}

# Define region-based default language settings
REGION_LANGUAGE_MAP = {
    "SADC": "en",
    "Israel": "he",
    "Europe": "fr",
    "LatinAmerica": "es",
    "Asia": "zh",
    "EastAfrica": "sw",
    "Global": "en"
}

# Region-specific locked pricing logic
SPECIAL_REGIONS = {
    "Israel": {
        "locked": True,
        "currency": "ILS",
        "pricing": {
            "monthly": 99,
            "weekly": 25
        },
        "label": "Special Region - Israel (Pricing locked after registration)"
    },
    "SADC": {
        "locked": False,
        "currency": "USD",
        "pricing": {
            "monthly": 59,
            "weekly": 15
        },
        "label": "SADC Region"
    },
    "Global": {
        "locked": False,
        "currency": "USD",
        "pricing": {
            "monthly": 59,
            "weekly": 15
        },
        "label": "Global Pricing"
    }
}

# Default fallback language
DEFAULT_LANGUAGE = "en"

# Localization dictionary (sample, should expand per UI component or externalize to JSON/YAML later)
LOCALIZED_STRINGS = {
    "en": {
        "welcome": "Welcome to RLG Data & RLG Fans!",
        "pricing_note": "Pricing will be shown after registration based on your region.",
        "locked_pricing_notice": "You cannot change your region after registration.",
        "super_tool": "Access the RLG Super Tool",
        "ai_insights": "View AI-Powered Insights"
    },
    "he": {
        "welcome": "ברוכים הבאים ל-RLG Data ו-RLG Fans!",
        "pricing_note": "המחירים יוצגו לאחר ההרשמה בהתאם למיקומך.",
        "locked_pricing_notice": "לא תוכל לשנות את מיקומך לאחר ההרשמה.",
        "super_tool": "גישה לכלי העל של RLG",
        "ai_insights": "הצג תובנות מונחות AI"
    },
    "sw": {
        "welcome": "Karibu RLG Data na RLG Fans!",
        "pricing_note": "Bei itaonyeshwa baada ya usajili kulingana na eneo lako.",
        "locked_pricing_notice": "Huwezi kubadilisha eneo lako baada ya usajili.",
        "super_tool": "Fikia Zana Kuu ya RLG",
        "ai_insights": "Angalia Maarifa Yanayoendeshwa na AI"
    },
    # Add more localized content as needed
}


def get_default_language(region: str) -> str:
    """Return the default language for a given region."""
    return REGION_LANGUAGE_MAP.get(region, DEFAULT_LANGUAGE)


def get_localized_string(lang: str, key: str) -> str:
    """Return a localized string based on language and key."""
    return LOCALIZED_STRINGS.get(lang, LOCALIZED_STRINGS[DEFAULT_LANGUAGE]).get(key, key)


def get_pricing_by_region(region: str) -> Dict:
    """Return pricing and display metadata based on user region."""
    return SPECIAL_REGIONS.get(region, SPECIAL_REGIONS["Global"])


def is_region_locked(region: str) -> bool:
    """Check if the region has locked pricing and location settings."""
    return SPECIAL_REGIONS.get(region, {}).get("locked", False)


def get_supported_languages() -> Dict[str, str]:
    """Return the list of supported languages."""
    return SUPPORTED_LANGUAGES


# Example utility function: personalize greeting and pricing message
def generate_user_onboarding_content(region: str) -> Dict[str, str]:
    lang = get_default_language(region)
    strings = {
        "welcome": get_localized_string(lang, "welcome"),
        "pricing_note": get_localized_string(lang, "pricing_note"),
        "locked_pricing_notice": get_localized_string(lang, "locked_pricing_notice"),
        "super_tool_access": get_localized_string(lang, "super_tool"),
        "ai_insights_access": get_localized_string(lang, "ai_insights")
    }
    pricing_info = get_pricing_by_region(region)
    strings.update({
        "pricing_tier": pricing_info.get("label"),
        "pricing_values": pricing_info.get("pricing")
    })
    return strings

import json
import os
import logging
from deep_translator import GoogleTranslator
from langdetect import detect
from config import LANGUAGE_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class MultiLanguageSupport:
    """Handles multi-language support for RLG Data and RLG Fans, ensuring a globally optimized user experience."""

    def __init__(self):
        self.supported_languages = LANGUAGE_CONFIG.get("supported_languages", self.load_supported_languages())
        self.default_language = LANGUAGE_CONFIG.get("default_language", "en")
        self.translator = GoogleTranslator(source="auto", target=self.default_language)
        self.translations_cache = {}

    def load_supported_languages(self):
        """Loads all supported languages including African languages."""
        return [
            "en", "fr", "es", "de", "zh", "ar",  # Major global languages
            "sw", "am", "ha", "ig", "yo", "zu", "xh", "rw", "lg", "so", "ny", "tn",  # African languages
            "af", "st", "ts", "ve", "nr", "ss", "sn", "mg"  # More African languages
        ]

    def detect_language(self, text):
        """Detects the language of the given text and ensures regional accuracy."""
        try:
            detected_lang = detect(text)
            if detected_lang in self.supported_languages:
                logging.info(f"Detected language: {detected_lang}")
                return detected_lang
            return self.default_language
        except Exception as e:
            logging.error(f"Language detection failed: {e}")
            return self.default_language

    def translate_text(self, text, target_language):
        """Translates text into the specified target language with caching and optimizations."""
        if target_language not in self.supported_languages:
            logging.warning(f"Language {target_language} not supported, defaulting to {self.default_language}")
            target_language = self.default_language

        cache_key = (text, target_language)
        if cache_key in self.translations_cache:
            return self.translations_cache[cache_key]

        try:
            translated_text = GoogleTranslator(source="auto", target=target_language).translate(text)
            self.translations_cache[cache_key] = translated_text
            return translated_text
        except Exception as e:
            logging.error(f"Translation failed: {e}")
            return text

    def load_language_pack(self, language):
        """Loads predefined language packs for UI elements and messages, ensuring regional accuracy."""
        lang_file = f"language_packs/{language}.json"
        if os.path.exists(lang_file):
            with open(lang_file, "r", encoding="utf-8") as file:
                return json.load(file)
        return {}

    def localize_content(self, content, target_language):
        """Translates and formats content according to the target language and regional preferences."""
        language_pack = self.load_language_pack(target_language)
        localized_content = {
            key: language_pack.get(key, self.translate_text(value, target_language))
            for key, value in content.items()
        }
        return localized_content

    def optimize_for_seo(self, translated_text, target_language):
        """Ensures regional SEO optimization by adapting translations to regional search patterns."""
        seo_keywords = {
            "en": ["social media analytics", "brand monitoring", "AI marketing"],
            "fr": ["analyse des médias sociaux", "suivi de marque", "marketing IA"],
            "sw": ["uchambuzi wa mitandao", "ufuatiliaji wa chapa", "masoko ya AI"],
            "ar": ["تحليلات وسائل التواصل الاجتماعي", "مراقبة العلامة التجارية", "تسويق الذكاء الاصطناعي"],
            "yo": ["Itupalẹ media awujọ", "Idaniloju ami", "Titaja AI"]
        }
        if target_language in seo_keywords:
            translated_text += f" | {' '.join(seo_keywords[target_language])}"
        return translated_text

# Example Usage
if __name__ == "__main__":
    multi_lang = MultiLanguageSupport()

    sample_text = "Welcome to RLG Data and RLG Fans, your all-in-one AI-powered marketing and compliance tool!"
    detected_lang = multi_lang.detect_language(sample_text)
    translated_text = multi_lang.translate_text(sample_text, "sw")  # Translating to Swahili

    logging.info(f"Detected Language: {detected_lang}")
    logging.info(f"Translated to Swahili: {translated_text}")

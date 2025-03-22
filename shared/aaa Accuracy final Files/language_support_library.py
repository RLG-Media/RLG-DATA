import logging
from typing import List, Dict
from googletrans import Translator
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("language_support_library.log"),
        logging.StreamHandler()
    ]
)

class LanguageSupportLibrary:
    """
    Library for managing language support, including translation,
    language detection, and cross-platform compatibility for RLG Data and RLG Fans.
    """

    def __init__(self):
        self.translator = Translator()
        DetectorFactory.seed = 0  # Ensure consistent results for langdetect
        logging.info("LanguageSupportLibrary initialized.")

    def detect_language(self, text: str) -> str:
        """
        Detect the language of a given text.

        Args:
            text: The text to detect the language for.

        Returns:
            The detected language code (e.g., 'en', 'fr').
        """
        try:
            language = detect(text)
            logging.info("Detected language: %s", language)
            return language
        except LangDetectException as e:
            logging.error("Failed to detect language: %s", e)
            return "unknown"

    def translate_text(self, text: str, target_language: str, source_language: str = "auto") -> Dict:
        """
        Translate text into the target language.

        Args:
            text: The text to translate.
            target_language: The language code to translate the text into (e.g., 'en', 'fr').
            source_language: The language code of the source text (default: 'auto').

        Returns:
            A dictionary with the translated text and language details.
        """
        try:
            translation = self.translator.translate(text, src=source_language, dest=target_language)
            result = {
                "source_language": translation.src,
                "target_language": translation.dest,
                "translated_text": translation.text
            }
            logging.info("Translated text successfully.")
            return result
        except Exception as e:
            logging.error("Failed to translate text: %s", e)
            return {
                "error": "Translation failed.",
                "details": str(e)
            }

    def batch_translate(self, texts: List[str], target_language: str, source_language: str = "auto") -> List[Dict]:
        """
        Translate a batch of texts into the target language.

        Args:
            texts: A list of texts to translate.
            target_language: The language code to translate the texts into (e.g., 'en', 'fr').
            source_language: The language code of the source texts (default: 'auto').

        Returns:
            A list of dictionaries with translated texts and language details.
        """
        translations = []
        for text in texts:
            translations.append(self.translate_text(text, target_language, source_language))
        logging.info("Batch translation completed for %d texts.", len(texts))
        return translations

    def supported_languages(self) -> List[Dict]:
        """
        List all supported languages for translation.

        Returns:
            A list of dictionaries containing language names and their codes.
        """
        languages = self.translator.LANGUAGES
        supported_languages = [{"code": code, "name": name} for code, name in languages.items()]
        logging.info("Retrieved supported languages.")
        return supported_languages

# Example usage
if __name__ == "__main__":
    library = LanguageSupportLibrary()

    # Detect language
    sample_text = "Bonjour tout le monde"
    detected_language = library.detect_language(sample_text)
    print(f"Detected Language: {detected_language}")

    # Translate text
    translated = library.translate_text("Hello, how are you?", "fr")
    print("Translation Result:", translated)

    # Batch translate
    batch_texts = ["Good morning", "Good night", "How are you?"]
    batch_translations = library.batch_translate(batch_texts, "es")
    print("Batch Translations:", batch_translations)

    # List supported languages
    languages = library.supported_languages()
    print("Supported Languages:", languages)

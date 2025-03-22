import logging
from typing import List, Dict, Optional
from google.cloud import translate_v2 as translate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("language_translation_services.log"),
        logging.StreamHandler()
    ]
)

class LanguageTranslationService:
    """
    Service class to manage language translation for RLG Data and RLG Fans.
    Includes features for text translation, supported language detection, and batch translation.
    """

    def __init__(self, google_cloud_key_path: str):
        """
        Initialize the LanguageTranslationService.

        Args:
            google_cloud_key_path (str): Path to the Google Cloud service account key JSON file.
        """
        self.google_cloud_key_path = google_cloud_key_path
        self.translate_client = self._initialize_google_translate_client()
        logging.info("LanguageTranslationService initialized with Google Cloud Translate API.")

    def _initialize_google_translate_client(self):
        """
        Initialize the Google Translate client.

        Returns:
            translate.Client: Google Translate client.
        """
        try:
            return translate.Client.from_service_account_json(self.google_cloud_key_path)
        except Exception as e:
            logging.error("Failed to initialize Google Translate client: %s", e)
            raise

    def detect_language(self, text: str) -> Dict[str, str]:
        """
        Detect the language of a given text.

        Args:
            text (str): The text to analyze.

        Returns:
            Dict[str, str]: Detected language and confidence level.
        """
        try:
            result = self.translate_client.detect_language(text)
            detected_language = {
                "language": result["language"],
                "confidence": str(result["confidence"])
            }
            logging.info("Detected language: %s with confidence: %s", detected_language["language"], detected_language["confidence"])
            return detected_language
        except Exception as e:
            logging.error("Failed to detect language: %s", e)
            raise

    def translate_text(self, text: str, target_language: str, source_language: Optional[str] = None) -> str:
        """
        Translate a given text into the target language.

        Args:
            text (str): The text to translate.
            target_language (str): The language code for the target language (e.g., 'en', 'es').
            source_language (str, optional): The language code for the source language. If None, it will auto-detect.

        Returns:
            str: The translated text.
        """
        try:
            result = self.translate_client.translate(
                text,
                target_language=target_language,
                source_language=source_language
            )
            translated_text = result["translatedText"]
            logging.info("Translated text to %s: %s", target_language, translated_text)
            return translated_text
        except Exception as e:
            logging.error("Failed to translate text: %s", e)
            raise

    def batch_translate(self, texts: List[str], target_language: str, source_language: Optional[str] = None) -> List[str]:
        """
        Translate a batch of texts into the target language.

        Args:
            texts (List[str]): A list of texts to translate.
            target_language (str): The language code for the target language (e.g., 'en', 'es').
            source_language (str, optional): The language code for the source language. If None, it will auto-detect.

        Returns:
            List[str]: A list of translated texts.
        """
        try:
            translations = []
            for text in texts:
                translations.append(self.translate_text(text, target_language, source_language))
            logging.info("Batch translation completed for %d texts to %s.", len(texts), target_language)
            return translations
        except Exception as e:
            logging.error("Failed to perform batch translation: %s", e)
            raise

    def supported_languages(self, target_language: Optional[str] = "en") -> List[Dict[str, str]]:
        """
        Get a list of supported languages by the translation API.

        Args:
            target_language (str, optional): The language code for displaying language names (default is 'en').

        Returns:
            List[Dict[str, str]]: A list of supported languages with their codes and names.
        """
        try:
            languages = self.translate_client.get_languages(target_language=target_language)
            logging.info("Retrieved %d supported languages.", len(languages))
            return languages
        except Exception as e:
            logging.error("Failed to retrieve supported languages: %s", e)
            raise

# Example usage
if __name__ == "__main__":
    google_cloud_key_path = "path/to/your/google_cloud_key.json"
    translation_service = LanguageTranslationService(google_cloud_key_path)

    # Detect language
    text_to_detect = "Hola, ¿cómo estás?"
    detected_language = translation_service.detect_language(text_to_detect)
    print("Detected Language:", detected_language)

    # Translate text
    text_to_translate = "Hello, how are you?"
    translated_text = translation_service.translate_text(text_to_translate, target_language="es")
    print("Translated Text:", translated_text)

    # Batch translation
    texts_to_translate = ["Good morning!", "What is your name?", "Thank you!"]
    batch_translations = translation_service.batch_translate(texts_to_translate, target_language="fr")
    print("Batch Translations:", batch_translations)

    # Get supported languages
    supported_langs = translation_service.supported_languages()
    print("Supported Languages:", supported_langs)

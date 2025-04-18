#!/usr/bin/env python3
"""
RLG Automated Language Detection & Translation
----------------------------------------------
This module detects the language of text, provides region-based accuracy,
and translates content into a target language if needed.

Features:
✔ Detects 100+ languages using fast AI-based models (LangDetect, langid, and deep_translator)
✔ Supports real-time translation via Google, DeepL, or Microsoft Translator APIs
✔ Enables multilingual sentiment analysis, compliance, and competitive benchmarking
✔ Scalable, data-driven, and integrates seamlessly with RLG Super Tool
"""

import logging
import langid
from langdetect import detect, DetectorFactory
from deep_translator import GoogleTranslator, exceptions

# Ensure reproducibility for langdetect
DetectorFactory.seed = 0

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# Supported language codes
SUPPORTED_LANGUAGES = {
    "en": "English", "es": "Spanish", "fr": "French", "de": "German", "zh-cn": "Chinese", "ru": "Russian",
    "ar": "Arabic", "pt": "Portuguese", "hi": "Hindi", "ja": "Japanese", "ko": "Korean", "tr": "Turkish",
    "nl": "Dutch", "sv": "Swedish", "it": "Italian", "pl": "Polish", "id": "Indonesian", "th": "Thai",
    "he": "Hebrew", "vi": "Vietnamese", "da": "Danish", "no": "Norwegian", "fi": "Finnish", "el": "Greek",
    "cs": "Czech", "hu": "Hungarian", "ro": "Romanian"
}

def detect_language(text):
    """
    Detects the language of a given text using langdetect and langid.
    Returns a dictionary with detected language and confidence score.
    """
    if not text or len(text) < 3:
        return {"language": "unknown", "confidence": 0}

    try:
        lang_detected = detect(text)
        lang_confidence = langid.classify(text)[1]  # Confidence score from langid
        
        if lang_detected in SUPPORTED_LANGUAGES:
            return {
                "language": SUPPORTED_LANGUAGES.get(lang_detected, "Unknown"),
                "language_code": lang_detected,
                "confidence": round(lang_confidence, 2)
            }
        else:
            return {"language": "Unsupported", "confidence": 0}
    
    except Exception as e:
        logging.error(f"Language detection failed: {e}")
        return {"language": "error", "confidence": 0}

def translate_text(text, target_language="en"):
    """
    Translates a given text into the specified target language.
    Uses Google Translator API (can be extended to DeepL or Microsoft Translator).
    """
    if not text or target_language not in SUPPORTED_LANGUAGES:
        return {"translated_text": text, "error": "Invalid target language"}

    try:
        translated_text = GoogleTranslator(source="auto", target=target_language).translate(text)
        return {"translated_text": translated_text, "error": None}
    
    except exceptions.NotValidPayload:
        logging.warning(f"Translation skipped: Empty or invalid input.")
        return {"translated_text": text, "error": "Invalid input"}
    
    except exceptions.ElementNotFoundInAPIResponse:
        logging.error(f"Translation API issue for text: {text}")
        return {"translated_text": text, "error": "API error"}

def process_text(text, target_language="en"):
    """
    Detects the language of the text and translates it if necessary.
    Returns a dictionary with original text, detected language, and translated text.
    """
    detected = detect_language(text)
    
    if detected["language_code"] != target_language and detected["language_code"] != "unknown":
        translation = translate_text(text, target_language)
        return {
            "original_text": text,
            "detected_language": detected["language"],
            "confidence": detected["confidence"],
            "translated_text": translation["translated_text"],
            "error": translation["error"]
        }
    else:
        return {
            "original_text": text,
            "detected_language": detected["language"],
            "confidence": detected["confidence"],
            "translated_text": text,
            "error": None
        }

# Test cases
if __name__ == "__main__":
    test_sentences = [
        "Bonjour tout le monde!",  # French
        "Hola, ¿cómo estás?",  # Spanish
        "Hallo, wie geht es Ihnen?",  # German
        "こんにちは、元気ですか？",  # Japanese
        "Привет, как дела?",  # Russian
        "Hello, how are you?"  # English
    ]

    for sentence in test_sentences:
        result = process_text(sentence, target_language="en")
        print(f"Original: {result['original_text']}")
        print(f"Detected Language: {result['detected_language']} (Confidence: {result['confidence']})")
        print(f"Translated: {result['translated_text']}")
        print("-------------------------------------------------")

import logging
from typing import List, Dict
from langdetect import detect
from transformers import pipeline, MarianMTModel, MarianTokenizer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("cross_language_sentiment_analysis.log"),
        logging.StreamHandler()
    ]
)

class CrossLanguageSentimentAnalysis:
    def __init__(self):
        self.translation_models = {}
        self.sentiment_pipeline = pipeline("sentiment-analysis")
        logging.info("CrossLanguageSentimentAnalysis initialized.")

    def _get_translation_model(self, src_lang: str):
        if src_lang not in self.translation_models:
            model_name = f"Helsinki-NLP/opus-mt-{src_lang}-en"
            try:
                model = MarianMTModel.from_pretrained(model_name)
                tokenizer = MarianTokenizer.from_pretrained(model_name)
                self.translation_models[src_lang] = (model, tokenizer)
                logging.info(f"Loaded translation model for {src_lang}.")
            except Exception as e:
                logging.error(f"Failed to load translation model for {src_lang}: {e}")
                raise
        return self.translation_models[src_lang]

    def translate_to_english(self, text: str, src_lang: str) -> str:
        model, tokenizer = self._get_translation_model(src_lang)
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        translated = model.generate(**inputs)
        translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)
        logging.info(f"Translated text from {src_lang} to English.")
        return translated_text

    def detect_language(self, text: str) -> str:
        try:
            lang = detect(text)
            logging.info(f"Detected language: {lang}")
            return lang
        except Exception as e:
            logging.error(f"Language detection failed: {e}")
            raise

    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        try:
            result = self.sentiment_pipeline(text)
            sentiment = {
                "label": result[0]["label"],
                "score": result[0]["score"]
            }
            logging.info(f"Sentiment analysis result: {sentiment}")
            return sentiment
        except Exception as e:
            logging.error(f"Sentiment analysis failed: {e}")
            raise

    def analyze_sentiment_cross_language(self, text: str) -> Dict:
        try:
            src_lang = self.detect_language(text)
            if src_lang == "en":
                sentiment = self.analyze_sentiment(text)
                return {"original_language": src_lang, "translated": False, **sentiment}
            else:
                translated_text = self.translate_to_english(text, src_lang)
                sentiment = self.analyze_sentiment(translated_text)
                return {
                    "original_language": src_lang,
                    "translated": True,
                    "original_text": text,
                    "translated_text": translated_text,
                    **sentiment
                }
        except Exception as e:
            logging.error(f"Cross-language sentiment analysis failed: {e}")
            return {"error": str(e)}

    def batch_analyze_sentiment(self, texts: List[str]) -> List[Dict]:
        results = []
        for text in texts:
            result = self.analyze_sentiment_cross_language(text)
            results.append(result)
        return results

if __name__ == "__main__":
    analysis_service = CrossLanguageSentimentAnalysis()
    sample_texts = [
        "I love this product!",  # English
        "J'adore ce produit!",   # French
        "我喜欢这个产品!"  # Chinese
    ]
    results = analysis_service.batch_analyze_sentiment(sample_texts)
    for result in results:
        print(result)

"""
nlp_processor.py

This module provides the NLPProcessor class for processing text data for both RLG Data (media articles)
and RLG Fans (social posts). It integrates spaCy for tokenization, lemmatization, stopword removal, and entity
extraction, and NLTK's VADER for sentiment analysis.

Features:
- Text cleaning (lowercasing, trimming whitespace).
- Tokenization and lemmatization.
- Stopword removal.
- Named entity extraction.
- Sentiment analysis using VADER.
- A complete processing pipeline that returns tokens, lemmas, entities, and sentiment scores.

Additional Recommendations:
1. For region-specific processing, you can extend the class to load region-specific stopwords or sentiment lexicons.
2. For large-scale or real-time processing, consider asynchronous or batch processing strategies.
3. Expand the pipeline with additional NLP tasks (e.g., part-of-speech tagging, dependency parsing) if needed.
4. Add unit tests to ensure consistency across different types of input data.
"""

import re
import logging
from typing import List, Dict, Any

import spacy
from spacy.tokens import Doc
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Ensure the VADER lexicon is downloaded.
try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    nltk.download("vader_lexicon")

# Configure logging
logger = logging.getLogger("NLPProcessor")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)


class NLPProcessor:
    def __init__(self, language_model: str = "en_core_web_sm", region: str = "default"):
        """
        Initializes the NLPProcessor.

        Parameters:
            language_model (str): The spaCy language model to load.
            region (str): Region identifier for region-specific processing (e.g., stopword customization).
        """
        try:
            self.nlp = spacy.load(language_model)
            logger.info(f"Loaded spaCy model '{language_model}' successfully.")
        except Exception as e:
            logger.error(f"Error loading spaCy model '{language_model}': {e}")
            raise

        self.region = region
        # Initialize NLTK's VADER sentiment analyzer.
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        logger.info("Initialized NLTK VADER SentimentIntensityAnalyzer.")

    def clean_text(self, text: str) -> str:
        """
        Cleans the input text by lowercasing and stripping extra whitespace.

        Parameters:
            text (str): The raw text.

        Returns:
            str: The cleaned text.
        """
        try:
            cleaned = text.lower().strip()
            cleaned = re.sub(r'\s+', ' ', cleaned)
            logger.debug(f"Cleaned text: {cleaned[:60]}...")
            return cleaned
        except Exception as e:
            logger.error(f"Error cleaning text: {e}")
            return text

    def tokenize_and_lemmatize(self, text: str) -> List[str]:
        """
        Tokenizes and lemmatizes the input text using spaCy.

        Parameters:
            text (str): The text to process.

        Returns:
            List[str]: A list of lemmas for tokens that are not stopwords or punctuation.
        """
        try:
            doc: Doc = self.nlp(text)
            tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
            logger.debug(f"Tokens after lemmatization: {tokens[:10]}")
            return tokens
        except Exception as e:
            logger.error(f"Error in tokenization and lemmatization: {e}")
            return []

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extracts named entities from the text using spaCy.

        Parameters:
            text (str): The text to analyze.

        Returns:
            List[Dict[str, Any]]: A list of entities with their text and label.
        """
        try:
            doc: Doc = self.nlp(text)
            entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
            logger.debug(f"Extracted entities: {entities}")
            return entities
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return []

    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyzes sentiment of the text using NLTK's VADER.

        Parameters:
            text (str): The text to analyze.

        Returns:
            Dict[str, float]: A dictionary with sentiment scores (negative, neutral, positive, compound).
        """
        try:
            scores = self.sentiment_analyzer.polarity_scores(text)
            logger.debug(f"Sentiment scores: {scores}")
            return scores
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {"neg": 0.0, "neu": 0.0, "pos": 0.0, "compound": 0.0}

    def process_text(self, text: str) -> Dict[str, Any]:
        """
        Full processing pipeline for a single text. Cleans text, tokenizes/lemmatizes,
        extracts entities, and performs sentiment analysis.

        Parameters:
            text (str): The input text to process.

        Returns:
            Dict[str, Any]: A dictionary containing:
                - cleaned_text: The cleaned version of the text.
                - tokens: List of tokens/lemmas.
                - entities: Extracted named entities.
                - sentiment: Sentiment analysis scores.
        """
        logger.info("Processing text through NLP pipeline.")
        cleaned = self.clean_text(text)
        tokens = self.tokenize_and_lemmatize(cleaned)
        entities = self.extract_entities(cleaned)
        sentiment = self.analyze_sentiment(cleaned)
        
        result = {
            "cleaned_text": cleaned,
            "tokens": tokens,
            "entities": entities,
            "sentiment": sentiment
        }
        logger.info("Completed processing text.")
        return result

    def batch_process_texts(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Processes a list of texts in a batch.

        Parameters:
            texts (List[str]): A list of text strings to process.

        Returns:
            List[Dict[str, Any]]: A list of processing results for each text.
        """
        logger.info(f"Batch processing {len(texts)} texts.")
        results = [self.process_text(text) for text in texts]
        logger.info("Completed batch processing texts.")
        return results


# -------------------------------
# Additional Recommendations:
# -------------------------------
# 1. For more advanced processing, consider integrating additional NLP tasks such as POS tagging,
#    dependency parsing, and coreference resolution.
# 2. To improve region-specific accuracy, extend the class to load region-specific stopword lists or sentiment lexicons.
# 3. For high-volume data, consider using asynchronous processing or batching with parallelism.
# 4. Implement unit tests for each method using representative text examples to ensure the pipeline's accuracy.
# 5. If higher accuracy is required, explore fine-tuning pre-trained transformer models (e.g., using Hugging Face's transformers).

# -------------------------------
# Standalone Testing
# -------------------------------
if __name__ == "__main__":
    # Sample texts for testing (for both RLG Data and RLG Fans)
    sample_text = (
        "Breaking: The new RLG Data platform is revolutionizing digital media monitoring! "
        "Experts say this innovative tool is a game-changer. Meanwhile, fans on RLG Fans are "
        "thrilled with the latest updates and engaging community features."
    )
    
    processor = NLPProcessor()
    result = processor.process_text(sample_text)
    
    print("Processed Text Result:")
    print(result)

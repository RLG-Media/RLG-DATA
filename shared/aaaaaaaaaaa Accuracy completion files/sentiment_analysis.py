"""
sentiment_analysis.py

This module provides sentiment analysis functionality for both RLG Data (media articles)
and RLG Fans (social posts). It leverages NLTK's VADER sentiment analyzer to compute sentiment
scores, and supports both single-text and batch processing. The module is designed to be robust,
scalable, and ready for integration into automated and region-specific workflows.
"""

import logging
from typing import List, Dict, Any

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Ensure the VADER lexicon is downloaded.
try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    nltk.download("vader_lexicon")

# Configure logging
logger = logging.getLogger("SentimentAnalysis")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)


class SentimentAnalyzer:
    def __init__(self, region: str = "default", custom_lexicon: Dict[str, float] = None):
        """
        Initializes the SentimentAnalyzer.

        Parameters:
            region (str): A region identifier for potential region-specific adjustments.
            custom_lexicon (Dict[str, float], optional): Custom lexicon to override or extend VADER's defaults.
                This can be used for region-specific sentiment calibration.
        """
        try:
            self.analyzer = SentimentIntensityAnalyzer()
            logger.info("Initialized VADER SentimentIntensityAnalyzer.")
            if custom_lexicon:
                # Update the lexicon with custom values if provided.
                self.analyzer.lexicon.update(custom_lexicon)
                logger.info("Custom lexicon applied for region '%s'.", region)
        except Exception as e:
            logger.error(f"Error initializing sentiment analyzer: {e}")
            raise

        self.region = region

    def analyze_text(self, text: str) -> Dict[str, float]:
        """
        Analyzes the sentiment of a single text string.

        Parameters:
            text (str): The text to analyze.

        Returns:
            Dict[str, float]: A dictionary containing sentiment scores:
                - 'neg': Negative score.
                - 'neu': Neutral score.
                - 'pos': Positive score.
                - 'compound': Compound score (overall sentiment).
        """
        try:
            if not text:
                logger.warning("Empty text provided to sentiment analyzer.")
                return {"neg": 0.0, "neu": 0.0, "pos": 0.0, "compound": 0.0}
            scores = self.analyzer.polarity_scores(text)
            logger.debug(f"Sentiment scores for text: {scores}")
            return scores
        except Exception as e:
            logger.error(f"Error analyzing text sentiment: {e}")
            return {"neg": 0.0, "neu": 0.0, "pos": 0.0, "compound": 0.0}

    def batch_analyze(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Processes a list of texts to compute sentiment scores for each.

        Parameters:
            texts (List[str]): A list of text strings.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each containing:
                - 'text': The original text.
                - 'sentiment': The sentiment scores dictionary.
        """
        results = []
        for idx, text in enumerate(texts):
            try:
                scores = self.analyze_text(text)
                results.append({"text": text, "sentiment": scores})
                logger.debug(f"Processed text index {idx} with sentiment: {scores}")
            except Exception as e:
                logger.error(f"Error processing text at index {idx}: {e}")
                results.append({"text": text, "sentiment": {"neg": 0.0, "neu": 0.0, "pos": 0.0, "compound": 0.0}})
        logger.info("Completed batch sentiment analysis.")
        return results


# -------------------------------
# Additional Recommendations:
# -------------------------------
# 1. **Enhanced Models:** For more nuanced sentiment analysis, consider combining VADER with other models
#    (e.g., TextBlob or transformer-based models from Hugging Face) and comparing results.
# 2. **Region Customization:** Extend this class to load region-specific sentiment adjustments, such as custom lexicons.
# 3. **Asynchronous Processing:** For high-volume analysis, consider using asynchronous processing techniques.
# 4. **Integration:** Expose these methods via an API endpoint or integrate with your reporting/dashboard modules.
# 5. **Testing:** Develop unit tests with diverse text samples to ensure consistent and accurate sentiment analysis.

# -------------------------------
# Standalone Testing
# -------------------------------
if __name__ == "__main__":
    # Create an instance of the SentimentAnalyzer.
    analyzer = SentimentAnalyzer(region="default")
    
    # Test with a sample text from RLG Data.
    sample_text_data = (
        "Breaking: The innovative RLG Data platform is transforming digital media monitoring. "
        "This breakthrough technology has received rave reviews and positive sentiment from experts."
    )
    data_scores = analyzer.analyze_text(sample_text_data)
    print("Sentiment analysis for RLG Data sample text:")
    print(data_scores)
    
    # Test with a sample text from RLG Fans.
    sample_text_fans = (
        "I absolutely love the new features on the RLG Fans platform! The update is fantastic and has improved my experience dramatically."
    )
    fans_scores = analyzer.analyze_text(sample_text_fans)
    print("\nSentiment analysis for RLG Fans sample text:")
    print(fans_scores)
    
    # Batch processing example.
    texts = [sample_text_data, sample_text_fans, ""]
    batch_results = analyzer.batch_analyze(texts)
    print("\nBatch sentiment analysis results:")
    for result in batch_results:
        print(result)

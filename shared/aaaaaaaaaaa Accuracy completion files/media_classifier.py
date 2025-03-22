"""
media_classifiers.py

This module provides functionality to classify media content for both RLG Data (media articles)
and RLG Fans (social posts) using rule-based heuristics. The classification is designed to be robust,
scalable, and region-aware, with support for custom rules.

Features:
- Rule-based classification for media articles.
- Rule-based sentiment classification for fan posts.
- Batch processing support.
- Region-specific (or custom) classification rules.
- Detailed logging and error handling.
"""

import logging
import re
from typing import Dict, Optional

# Configure logging
logger = logging.getLogger("MediaClassifier")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

class MediaClassifier:
    def __init__(self, region: str = "default", custom_rules: Optional[Dict[str, Dict]] = None):
        """
        Initializes the MediaClassifier with region-specific rules.

        Parameters:
            region (str): The region identifier to use for classification rules.
            custom_rules (Optional[Dict[str, Dict]]): Custom classification rules that override defaults.
                Expected structure:
                {
                    "rlg_data": {
                        "Breaking News": ["breaking", "exclusive", "alert", "urgent"],
                        "Opinion": ["analysis", "opinion", "editorial", "commentary"],
                        "General": []  # fallback category
                    },
                    "rlg_fans": {
                        "Positive": ["love", "awesome", "great", "fantastic", "amazing"],
                        "Negative": ["hate", "terrible", "dislike", "awful", "bad"],
                        "Neutral": []  # fallback category
                    }
                }
        """
        self.region = region
        # Default rules for RLG Data classification (articles)
        self.default_data_rules = {
            "Breaking News": ["breaking", "exclusive", "alert", "urgent"],
            "Opinion": ["analysis", "opinion", "editorial", "commentary"],
            "General": []  # Fallback category if no keywords match
        }
        # Default rules for RLG Fans classification (sentiment)
        self.default_fans_rules = {
            "Positive": ["love", "awesome", "great", "fantastic", "amazing"],
            "Negative": ["hate", "terrible", "dislike", "awful", "bad"],
            "Neutral": []  # Fallback category if counts are equal or no keywords match
        }
        # Override defaults if custom rules are provided
        if custom_rules:
            self.data_rules = custom_rules.get("rlg_data", self.default_data_rules)
            self.fans_rules = custom_rules.get("rlg_fans", self.default_fans_rules)
        else:
            self.data_rules = self.default_data_rules
            self.fans_rules = self.default_fans_rules
        
        logger.info("MediaClassifier initialized for region: %s", self.region)
        logger.debug("Data rules: %s", self.data_rules)
        logger.debug("Fans rules: %s", self.fans_rules)
    
    def classify_rlg_data(self, text: str) -> Dict[str, str]:
        """
        Classifies a media article (RLG Data) into a category based on its text.

        Parameters:
            text (str): The text content of the media article.

        Returns:
            Dict[str, str]: Dictionary with keys "category" and "confidence" (a simple heuristic).
        """
        try:
            lower_text = text.lower()
            # Check each category's keywords in order
            for category, keywords in self.data_rules.items():
                for kw in keywords:
                    # Use regex for whole-word matching
                    if re.search(r'\b' + re.escape(kw) + r'\b', lower_text):
                        logger.debug("Article classified as '%s' based on keyword '%s'.", category, kw)
                        return {"category": category, "confidence": "high"}
            # Fallback category if no keywords match
            logger.debug("No specific keywords found. Defaulting to 'General'.")
            return {"category": "General", "confidence": "low"}
        except Exception as e:
            logger.error("Error classifying RLG Data: %s", e)
            return {"category": "Unknown", "confidence": "error"}
    
    def classify_rlg_fans(self, text: str) -> Dict[str, str]:
        """
        Classifies a fan post (RLG Fans) for sentiment based on its text.

        Parameters:
            text (str): The text content of the fan post.

        Returns:
            Dict[str, str]: Dictionary with keys "sentiment" and "confidence" (a simple heuristic).
        """
        try:
            lower_text = text.lower()
            # Count the occurrences of positive and negative keywords
            positive_count = sum(len(re.findall(r'\b' + re.escape(kw) + r'\b', lower_text))
                                 for kw in self.fans_rules.get("Positive", []))
            negative_count = sum(len(re.findall(r'\b' + re.escape(kw) + r'\b', lower_text))
                                 for kw in self.fans_rules.get("Negative", []))
            logger.debug("Positive count: %s, Negative count: %s", positive_count, negative_count)
            if positive_count > negative_count:
                sentiment = "Positive"
                confidence = "high" if positive_count - negative_count >= 2 else "medium"
            elif negative_count > positive_count:
                sentiment = "Negative"
                confidence = "high" if negative_count - positive_count >= 2 else "medium"
            else:
                sentiment = "Neutral"
                confidence = "low"
            return {"sentiment": sentiment, "confidence": confidence}
        except Exception as e:
            logger.error("Error classifying RLG Fans: %s", e)
            return {"sentiment": "Unknown", "confidence": "error"}
    
    def batch_classify_rlg_data(self, texts: list) -> list:
        """
        Batch classifies a list of media article texts.

        Parameters:
            texts (list): List of article text strings.

        Returns:
            list: List of classification results.
        """
        results = []
        for text in texts:
            classification = self.classify_rlg_data(text)
            results.append(classification)
        return results
    
    def batch_classify_rlg_fans(self, texts: list) -> list:
        """
        Batch classifies a list of fan post texts.

        Parameters:
            texts (list): List of fan post text strings.

        Returns:
            list: List of classification results.
        """
        results = []
        for text in texts:
            classification = self.classify_rlg_fans(text)
            results.append(classification)
        return results

# -------------------------------
# Additional Recommendations:
# -------------------------------
# 1. For more advanced classification, consider integrating NLP libraries (e.g., spaCy, NLTK) to perform tokenization,
#    lemmatization, and context-aware analysis.
# 2. Train a machine learning classifier (e.g., with scikit-learn) using labeled data for more nuanced categorization.
# 3. Store and manage region-specific rules externally (e.g., configuration files or databases) for easier maintenance.
# 4. Implement comprehensive unit tests covering a variety of sample texts to ensure consistent classification performance.
# 5. For high throughput, consider using asynchronous processing or a parallel classification pipeline.

if __name__ == "__main__":
    # Standalone testing for RLG Data classification
    classifier = MediaClassifier(region="default")
    
    sample_article = "Breaking: Exclusive report on the latest developments in the tech industry."
    result_data = classifier.classify_rlg_data(sample_article)
    print("RLG Data classification result:", result_data)
    
    sample_fan_post = "I absolutely love the new features! They are awesome and fantastic."
    result_fans = classifier.classify_rlg_fans(sample_fan_post)
    print("RLG Fans classification result:", result_fans)
    
    # Batch testing for articles
    sample_articles = [
        "Breaking news: Major breakthrough in renewable energy.",
        "In-depth analysis and opinion on the current political landscape.",
        "A casual update on everyday events."
    ]
    batch_results = classifier.batch_classify_rlg_data(sample_articles)
    print("Batch classification for RLG Data:", batch_results)
    
    # Batch testing for fan posts
    sample_fan_posts = [
        "I love this platform! It's amazing.",
        "I hate the recent update, it's terrible.",
        "The service is okay, nothing special."
    ]
    batch_fan_results = classifier.batch_classify_rlg_fans(sample_fan_posts)
    print("Batch classification for RLG Fans:", batch_fan_results)

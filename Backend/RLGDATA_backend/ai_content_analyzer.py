import re
import string
import logging
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any

# Configure logging: adjust level and handlers as necessary.
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class AIContentAnalyzer:
    """
    AI-based Content Analyzer for extracting insights from text content.
    This analyzer provides:
      - Text preprocessing (cleaning, lowercasing, punctuation removal).
      - Sentiment analysis using TextBlob.
      - Keyword extraction using TF-IDF.
      - Topic modeling using NMF.
      - Content similarity measurement using cosine similarity.
    """

    def __init__(self) -> None:
        """
        Initializes the content analyzer with a TF-IDF vectorizer configured
        to remove English stop words and limit the number of features.
        """
        try:
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000, 
                stop_words='english'
            )
            self.nmf_model = None  # Will be trained during topic modeling
            logger.info("AIContentAnalyzer initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing AIContentAnalyzer: {e}")
            raise

    @staticmethod
    def preprocess_text(text: str) -> str:
        """
        Cleans and preprocesses input text.
        
        Converts text to lowercase, removes punctuation, and extra whitespace.
        
        Args:
            text (str): The raw text to preprocess.
        
        Returns:
            str: Cleaned and preprocessed text.
        """
        try:
            logger.info("Preprocessing text...")
            # Convert text to lowercase
            text = text.lower()
            # Remove punctuation
            text = re.sub(f"[{re.escape(string.punctuation)}]", "", text)
            # Remove extra spaces and strip leading/trailing whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            return text
        except Exception as e:
            logger.error(f"Error preprocessing text: {e}")
            raise

    def sentiment_analysis(self, text: str) -> Dict[str, float]:
        """
        Performs sentiment analysis on the given text using TextBlob.
        
        Args:
            text (str): The text to analyze.
        
        Returns:
            Dict[str, float]: A dictionary with polarity and subjectivity scores.
        """
        try:
            logger.info("Performing sentiment analysis...")
            analysis = TextBlob(text)
            sentiment_scores = {
                "polarity": analysis.sentiment.polarity,
                "subjectivity": analysis.sentiment.subjectivity
            }
            logger.info(f"Sentiment analysis result: {sentiment_scores}")
            return sentiment_scores
        except Exception as e:
            logger.error(f"Error during sentiment analysis: {e}")
            raise

    def keyword_extraction(self, texts: List[str]) -> Dict[int, List[str]]:
        """
        Extracts key phrases from a collection of texts using TF-IDF.
        
        For each document, the top 10 keywords with the highest TF-IDF scores are extracted.
        
        Args:
            texts (List[str]): List of text documents.
        
        Returns:
            Dict[int, List[str]]: A dictionary mapping each document's index to a list of extracted keywords.
        """
        try:
            logger.info("Extracting keywords using TF-IDF...")
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            extracted_keywords = {}
            # Process each document
            for idx, row in enumerate(tfidf_matrix):
                # Convert row to array and get indices of top 10 scores
                row_array = row.toarray().flatten()
                top_indices = row_array.argsort()[-10:][::-1]
                keywords = [feature_names[i] for i in top_indices if row_array[i] > 0]
                extracted_keywords[idx] = keywords
            logger.info(f"Extracted keywords for {len(texts)} documents.")
            return extracted_keywords
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            raise

    def topic_modeling(self, texts: List[str], n_topics: int = 5) -> Dict[str, List[str]]:
        """
        Performs topic modeling on a collection of texts using Non-Negative Matrix Factorization (NMF).
        
        Args:
            texts (List[str]): List of text documents.
            n_topics (int): Number of topics to identify (default: 5).
        
        Returns:
            Dict[str, List[str]]: A dictionary mapping topic names (e.g., 'Topic 1') to a list of top keywords.
        """
        try:
            logger.info("Performing topic modeling using NMF...")
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
            self.nmf_model = NMF(n_components=n_topics, random_state=42)
            W = self.nmf_model.fit_transform(tfidf_matrix)
            H = self.nmf_model.components_
            feature_names = self.tfidf_vectorizer.get_feature_names_out()

            topics = {}
            for topic_idx, topic in enumerate(H):
                # Get indices for the top 10 keywords in the topic
                top_indices = topic.argsort()[-10:][::-1]
                top_keywords = [feature_names[i] for i in top_indices]
                topics[f"Topic {topic_idx + 1}"] = top_keywords

            logger.info(f"Identified topics: {topics}")
            return topics
        except Exception as e:
            logger.error(f"Error during topic modeling: {e}")
            raise

    def content_similarity(self, text1: str, text2: str) -> float:
        """
        Measures similarity between two pieces of text using cosine similarity on TF-IDF vectors.
        
        Args:
            text1 (str): The first text.
            text2 (str): The second text.
        
        Returns:
            float: Cosine similarity score between the two texts.
        """
        try:
            logger.info("Calculating content similarity...")
            texts = [text1, text2]
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
            similarity_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            logger.info(f"Calculated similarity score: {similarity_score}")
            return similarity_score
        except Exception as e:
            logger.error(f"Error calculating content similarity: {e}")
            raise

# -------------------------------
# Example Usage
# -------------------------------
if __name__ == "__main__":
    analyzer = AIContentAnalyzer()

    # Sample texts to analyze
    sample_texts = [
        "Learn how to monetize your content with the latest tips and tricks!",
        "Grow your audience with AI-driven insights and tools.",
        "Discover the power of data-driven decisions for your brand's success."
    ]

    # Preprocess texts
    cleaned_texts = [analyzer.preprocess_text(text) for text in sample_texts]
    print("Cleaned Texts:")
    for text in cleaned_texts:
        print(text)
    print()

    # Perform sentiment analysis for each text
    for text in cleaned_texts:
        sentiment = analyzer.sentiment_analysis(text)
        print(f"Text: {text}\nSentiment: {sentiment}\n")

    # Extract keywords from the texts
    keywords = analyzer.keyword_extraction(cleaned_texts)
    print("Extracted Keywords:")
    print(keywords)
    print()

    # Perform topic modeling on the texts
    topics = analyzer.topic_modeling(cleaned_texts, n_topics=3)
    print("Topic Modeling Results:")
    print(topics)
    print()

    # Calculate content similarity between first two texts
    similarity = analyzer.content_similarity(cleaned_texts[0], cleaned_texts[1])
    print(f"Content similarity between text 1 and text 2: {similarity}")

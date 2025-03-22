import logging
from typing import List, Dict, Any
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk

# Ensure required NLTK resources are downloaded
nltk.download("punkt")
nltk.download("stopwords")
nltk.download("vader_lexicon")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("nlp_analysis_services.log"),
        logging.StreamHandler()
    ]
)

class NLPAnalysisService:
    """
    Service for performing Natural Language Processing (NLP) analysis on text data for RLG Data and RLG Fans.
    """

    def __init__(self):
        self.stop_words = set(stopwords.words("english"))
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        logging.info("NLPAnalysisService initialized.")

    def tokenize_text(self, text: str) -> Dict[str, List[str]]:
        """
        Tokenize text into words and sentences.

        Args:
            text: The input text to tokenize.

        Returns:
            A dictionary containing word and sentence tokens.
        """
        logging.info("Tokenizing text.")
        words = word_tokenize(text)
        sentences = sent_tokenize(text)
        return {"words": words, "sentences": sentences}

    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """
        Remove stopwords from a list of tokens.

        Args:
            tokens: List of word tokens.

        Returns:
            List of tokens with stopwords removed.
        """
        logging.info("Removing stopwords.")
        filtered_tokens = [word for word in tokens if word.lower() not in self.stop_words]
        return filtered_tokens

    def compute_word_frequencies(self, tokens: List[str]) -> Dict[str, int]:
        """
        Compute word frequencies from a list of tokens.

        Args:
            tokens: List of word tokens.

        Returns:
            A dictionary of word frequencies.
        """
        logging.info("Computing word frequencies.")
        freq_dist = FreqDist(tokens)
        return dict(freq_dist)

    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Perform sentiment analysis on a given text.

        Args:
            text: The input text to analyze.

        Returns:
            A dictionary containing sentiment scores (positive, neutral, negative, compound).
        """
        logging.info("Analyzing sentiment.")
        sentiment_scores = self.sentiment_analyzer.polarity_scores(text)
        return sentiment_scores

    def extract_keywords(self, corpus: List[str], top_n: int = 10) -> List[str]:
        """
        Extract top keywords from a corpus using TF-IDF.

        Args:
            corpus: A list of documents.
            top_n: Number of top keywords to extract.

        Returns:
            A list of top keywords.
        """
        logging.info("Extracting keywords using TF-IDF.")
        vectorizer = TfidfVectorizer(max_features=top_n, stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(corpus)
        return vectorizer.get_feature_names_out()

    def summarize_text(self, text: str, sentence_count: int = 3) -> str:
        """
        Summarize text by selecting the most important sentences.

        Args:
            text: The input text to summarize.
            sentence_count: Number of sentences to include in the summary.

        Returns:
            A summarized version of the text.
        """
        logging.info("Summarizing text.")
        sentences = sent_tokenize(text)
        word_frequencies = self.compute_word_frequencies(word_tokenize(text))

        # Score sentences based on word frequencies
        sentence_scores = {}
        for sentence in sentences:
            for word in word_tokenize(sentence.lower()):
                if word in word_frequencies:
                    if sentence not in sentence_scores:
                        sentence_scores[sentence] = 0
                    sentence_scores[sentence] += word_frequencies[word]

        # Sort sentences by score and select the top ones
        sorted_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)
        return " ".join(sorted_sentences[:sentence_count])

# Example usage
if __name__ == "__main__":
    service = NLPAnalysisService()

    text = """
    Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals.
    Leading AI textbooks define the field as the study of "intelligent agents": any device that perceives its environment and takes actions that maximize its chance of successfully achieving its goals.
    """

    # Tokenize text
    tokens = service.tokenize_text(text)
    print("Tokens:", tokens)

    # Remove stopwords
    filtered_words = service.remove_stopwords(tokens["words"])
    print("Filtered Words:", filtered_words)

    # Compute word frequencies
    word_freqs = service.compute_word_frequencies(filtered_words)
    print("Word Frequencies:", word_freqs)

    # Perform sentiment analysis
    sentiment = service.analyze_sentiment(text)
    print("Sentiment Analysis:", sentiment)

    # Extract keywords
    corpus = [text]
    keywords = service.extract_keywords(corpus, top_n=5)
    print("Keywords:", keywords)

    # Summarize text
    summary = service.summarize_text(text, sentence_count=2)
    print("Summary:", summary)

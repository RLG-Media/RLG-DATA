# ai_content_analyzer.py

from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIContentAnalyzer:
    def __init__(self):
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        self.engagement_predictor_model = AutoModelForSequenceClassification.from_pretrained("facebook/bart-large-mnli")
        self.tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-mnli")
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        self.lda_model = LatentDirichletAllocation(n_components=5, random_state=42)

    def analyze_sentiment(self, content):
        """
        Analyze the sentiment of the given content and return structured results.
        """
        logger.info("Analyzing sentiment...")
        sentiment_result = self.sentiment_analyzer(content)
        sentiment_summary = {
            "label": sentiment_result[0]["label"],
            "score": sentiment_result[0]["score"]
        }
        logger.info(f"Sentiment analysis complete: {sentiment_summary}")
        return sentiment_summary

    def predict_engagement(self, content):
        """
        Predict engagement level based on content. Uses a sequence classification model to estimate.
        """
        logger.info("Predicting engagement level...")
        inputs = self.tokenizer(content, return_tensors="pt", truncation=True, max_length=512)
        outputs = self.engagement_predictor_model(**inputs)
        probabilities = outputs.logits.softmax(dim=1).detach().numpy()
        engagement_score = {
            "low": float(probabilities[0][0]),
            "medium": float(probabilities[0][1]),
            "high": float(probabilities[0][2])
        }
        logger.info(f"Engagement prediction complete: {engagement_score}")
        return engagement_score

    def extract_topics(self, contents):
        """
        Perform topic modeling on a list of content to identify major topics.
        """
        logger.info("Extracting topics using LDA...")
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(contents)
        self.lda_model.fit(tfidf_matrix)
        topics = {}
        for idx, topic in enumerate(self.lda_model.components_):
            topic_terms = [self.tfidf_vectorizer.get_feature_names_out()[i] for i in topic.argsort()[-10:]]
            topics[f"Topic {idx + 1}"] = topic_terms
        logger.info(f"Topic extraction complete: {topics}")
        return topics

    def content_optimization_suggestions(self, content, engagement_score, sentiment_summary):
        """
        Provide suggestions to optimize content based on sentiment and engagement predictions.
        """
        logger.info("Generating content optimization suggestions...")
        suggestions = []
        if sentiment_summary["label"] == "NEGATIVE" and sentiment_summary["score"] > 0.7:
            suggestions.append("Consider rephrasing to be more positive.")

        if engagement_score["high"] < 0.3:
            suggestions.append("Incorporate trending keywords or hashtags to improve engagement.")

        if "call to action" not in content.lower():
            suggestions.append("Add a call to action to encourage interaction.")

        logger.info(f"Optimization suggestions: {suggestions}")
        return suggestions

    def analyze_and_suggest(self, content):
        """
        Comprehensive analysis that combines sentiment analysis, engagement prediction, topic extraction,
        and optimization suggestions.
        """
        sentiment = self.analyze_sentiment(content)
        engagement = self.predict_engagement(content)
        suggestions = self.content_optimization_suggestions(content, engagement, sentiment)

        analysis_summary = {
            "sentiment": sentiment,
            "predicted_engagement": engagement,
            "optimization_suggestions": suggestions
        }

        logger.info(f"Full analysis summary: {json.dumps(analysis_summary, indent=2)}")
        return analysis_summary

# Example usage:
# analyzer = AIContentAnalyzer()
# content = "Check out my latest video, and don't forget to like and subscribe for more!"
# analysis_result = analyzer.analyze_and_suggest(content)

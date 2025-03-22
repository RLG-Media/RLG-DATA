# ai_content_analyzer.py

import logging
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter

# Setup logging
logger = logging.getLogger("ai_content_analyzer")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class AIContentAnalyzer:
    """Class for AI-based analysis of content to improve engagement and monetization."""
    
    def __init__(self):
        # Initialize AI model pipelines for sentiment analysis and summarization
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        self.summarizer = pipeline("summarization")
        self.vectorizer = TfidfVectorizer(max_features=100)

    def analyze_sentiment(self, content_text):
        """Analyze sentiment of content text to understand audience reaction."""
        logger.info("Performing sentiment analysis on content...")
        
        sentiments = self.sentiment_analyzer(content_text)
        sentiment_summary = Counter([sent['label'] for sent in sentiments])
        
        result = {
            "positive": sentiment_summary.get("POSITIVE", 0),
            "neutral": sentiment_summary.get("NEUTRAL", 0),
            "negative": sentiment_summary.get("NEGATIVE", 0),
            "total": len(sentiments)
        }
        
        logger.info(f"Sentiment analysis completed: {result}")
        return result

    def summarize_content(self, content_text):
        """Generate a concise summary for longer content."""
        logger.info("Generating content summary...")
        
        try:
            summary = self.summarizer(content_text, max_length=100, min_length=30, do_sample=False)
            summary_text = summary[0]['summary_text']
            logger.info("Content summarization completed successfully.")
            return summary_text
        except Exception as e:
            logger.error(f"Error in summarizing content: {e}")
            return "Summary unavailable"

    def analyze_keywords(self, content_list):
        """Extract top keywords from a list of content to identify trending topics."""
        logger.info("Extracting keywords from content for trend analysis...")
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform(content_list)
            feature_array = self.vectorizer.get_feature_names_out()
            keywords = feature_array[tfidf_matrix.sum(axis=0).A1.argsort()[-10:][::-1]]
            logger.info(f"Top keywords identified: {keywords}")
            return keywords.tolist()
        except Exception as e:
            logger.error(f"Error in keyword extraction: {e}")
            return []

    def content_optimization_recommendations(self, content_text):
        """Provide AI-driven recommendations to improve content engagement."""
        logger.info("Generating content optimization recommendations...")
        
        sentiment = self.analyze_sentiment(content_text)
        summary = self.summarize_content(content_text)
        recommendations = []

        if sentiment["negative"] > sentiment["positive"]:
            recommendations.append("Consider a more positive tone to increase engagement.")
        
        if len(content_text.split()) > 300:
            recommendations.append("Content is lengthy; consider a shorter format or dividing it into parts.")
        
        if summary:
            recommendations.append(f"Suggested content focus: {summary}")
        
        logger.info("Optimization recommendations generated.")
        return recommendations

    def generate_analysis_report(self, content_list, platforms_data):
        """Generate a comprehensive analysis report on content for RLG Data and RLG Fans."""
        logger.info("Generating full analysis report...")

        # Aggregate content from all supported platforms
        aggregated_content = " ".join(content_list + platforms_data)

        analysis_report = {
            "sentiment_summary": self.analyze_sentiment(aggregated_content),
            "keywords": self.analyze_keywords(content_list + platforms_data),
            "optimization_recommendations": []
        }
        
        for content in content_list + platforms_data:
            recommendations = self.content_optimization_recommendations(content)
            analysis_report["optimization_recommendations"].append({
                "content": content,
                "recommendations": recommendations
            })
        
        logger.info("Analysis report generated successfully.")
        return analysis_report

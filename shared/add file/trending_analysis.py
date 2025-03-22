# trending_analysis.py - Module for performing trending analysis on RLG Data and RLG Fans content

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class TrendingAnalysis:
    """
    Class for performing trending analysis on RLG Data and RLG Fans content.
    This includes keyword extraction, content analysis, and trend forecasting.
    """
    
    def __init__(self, data):
        self.data = data  # Assumed to be a DataFrame containing the content data
        self.keywords_col = 'content'  # Column containing the textual content
        
        # Ensure data is in the correct format
        if 'date' not in self.data.columns:
            self.data['date'] = pd.to_datetime('today')  # Default to today's date if not provided
    
    def preprocess_data(self):
        """
        Preprocess the content data to clean, tokenize, and remove stopwords.
        """
        logger.debug("Preprocessing the data")
        
        # Lowercasing, removing punctuations, and tokenization
        self.data['clean_content'] = self.data[self.keywords_col].str.lower().str.replace('[^\w\s]', '')
        return self.data
    
    def extract_keywords(self):
        """
        Extract keywords using TF-IDF (Term Frequency-Inverse Document Frequency).
        """
        logger.debug("Extracting keywords using TF-IDF")
        
        # Vectorize the content
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(self.data['clean_content'])
        
        # Calculate the average TF-IDF scores per document
        avg_tfidf = np.mean(tfidf_matrix.toarray(), axis=1)
        
        # Assign keywords to each content
        self.data['keywords'] = [vectorizer.get_feature_names_out()[i] for i in np.argmax(tfidf_matrix.toarray(), axis=1)]
        
        return self.data
    
    def calculate_trending_score(self):
        """
        Calculate trending scores based on engagement and recency.
        """
        logger.debug("Calculating trending scores")
        
        # Example: using engagement (likes/comments) and recency (time since creation)
        self.data['engagement_score'] = self.data['likes'] * 0.6 + self.data['comments'] * 0.4
        
        # Normalize recency
        current_time = pd.to_datetime('today')
        self.data['days_since'] = (current_time - self.data['date']).dt.days
        
        # Define weightings for engagement and recency (could be tuned)
        weight_engagement = 0.7
        weight_recency = 0.3
        
        # Trend score = weighted engagement + weighted recency
        self.data['trend_score'] = (self.data['engagement_score'] / self.data['engagement_score'].max()) * weight_engagement + \
                                   (1 - (self.data['days_since'] / self.data['days_since'].max())) * weight_recency
        
        return self.data

    def analyze_trends(self):
        """
        Main method to analyze trending content by performing all necessary steps.
        """
        logger.info("Analyzing content trends")
        
        self.preprocess_data()
        self.extract_keywords()
        self.calculate_trending_score()
        
        # Sort by trend score in descending order
        trending_content = self.data.sort_values(by='trend_score', ascending=False)
        
        logger.info(f"Trending content analysis completed, {len(trending_content)} items found.")
        return trending_content
    
    def get_trend_summary(self, top_n=10):
        """
        Provides a summarized view of top trending content.
        """
        logger.info(f"Generating top {top_n} trending content summary")
        
        trending_content = self.analyze_trends()
        top_trending = trending_content.head(top_n)
        
        summary = top_trending[['title', 'keywords', 'trend_score', 'likes', 'comments', 'date']]
        return summary
    
    def forecast_trends(self, forecast_days=7):
        """
        Forecast future trends based on past trending analysis.
        """
        logger.info("Forecasting future trends")
        
        # Get last week’s trend scores as base
        recent_trends = self.data[self.data['date'] >= (pd.to_datetime('today') - timedelta(days=forecast_days))]
        avg_trend_score = recent_trends['trend_score'].mean()
        
        # Simple forecast logic (could be refined)
        forecasted_trend_scores = avg_trend_score * np.random.uniform(0.9, 1.1, forecast_days)
        
        forecast_dates = [pd.to_datetime('today') + timedelta(days=i) for i in range(1, forecast_days+1)]
        
        forecast_results = pd.DataFrame({
            'date': forecast_dates,
            'forecast_trend_score': forecasted_trend_scores
        })
        
        logger.info("Trend forecasting completed")
        return forecast_results

# Example usage:
# data = pd.read_csv('content_data.csv')  # Example data source
# analysis = TrendingAnalysis(data)
# top_trending = analysis.get_trend_summary(top_n=10)
# forecast = analysis.forecast_trends(forecast_days=7)

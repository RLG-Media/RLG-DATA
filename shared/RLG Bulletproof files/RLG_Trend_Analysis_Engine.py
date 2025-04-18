#!/usr/bin/env python3
"""
RLG Trend Analysis Engine
----------------------------------------
This module automates trend analysis for RLG Data and RLG Fans. It is:
- Robust, data-driven, and scalable
- Integrates with RLG's scraping, sentiment analysis, and compliance engine
- Identifies emerging media trends using AI and machine learning
- Provides real-time insights based on historical patterns and forecasts
"""

import re
import numpy as np
import pandas as pd
import nltk
import matplotlib.pyplot as plt
import seaborn as sns
from langdetect import detect
from textblob import TextBlob
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from prophet import Prophet
from transformers import pipeline

# Download necessary NLP resources
nltk.download('stopwords')
nltk.download('punkt')

# Initialize sentiment analysis model
sentiment_pipeline = pipeline("sentiment-analysis")

# Stopwords list
STOPWORDS = set(nltk.corpus.stopwords.words('english'))

# Function to clean text
def clean_text(text):
    """Removes special characters, stopwords, and excess spaces."""
    text = text.lower()
    text = re.sub(r'\W', ' ', text)  # Remove non-word characters
    text = ' '.join([word for word in text.split() if word not in STOPWORDS])
    return text.strip()

# Topic Modeling with LDA
def extract_trending_topics(texts, num_topics=5):
    """
    Identifies top emerging topics using Latent Dirichlet Allocation (LDA).
    """
    vectorizer = CountVectorizer(stop_words='english')
    text_matrix = vectorizer.fit_transform(texts)
    
    lda = LatentDirichletAllocation(n_components=num_topics, random_state=42)
    lda.fit(text_matrix)
    
    terms = vectorizer.get_feature_names_out()
    topics = []
    
    for topic_idx, topic in enumerate(lda.components_):
        top_words = [terms[i] for i in topic.argsort()[:-6:-1]]
        topics.append(f"Topic {topic_idx+1}: {', '.join(top_words)}")
    
    return topics

# Sentiment-Based Trend Analysis
def analyze_sentiment_trends(texts, dates):
    """
    Analyzes sentiment trends over time using Prophet.
    """
    sentiment_scores = []
    
    for text in texts:
        sentiment_result = sentiment_pipeline(text)[0]
        label = sentiment_result['label']
        score = sentiment_result['score']
        
        if "1 star" in label or "2 stars" in label:
            sentiment_scores.append(-score)
        elif "3 stars" in label:
            sentiment_scores.append(0)
        else:
            sentiment_scores.append(score)
    
    df = pd.DataFrame({"ds": dates, "y": sentiment_scores})
    
    # Train a forecasting model
    model = Prophet()
    model.fit(df)
    
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)
    
    return df, forecast

# Full Trend Analysis Function
def trend_analysis(texts, dates, region="global"):
    """
    Performs complete trend analysis: topic modeling, sentiment trends, and forecasting.
    """
    texts = [clean_text(text) for text in texts if text.strip()]
    
    # Extract trending topics
    topics = extract_trending_topics(texts)
    
    # Analyze sentiment trends
    df, forecast = analyze_sentiment_trends(texts, dates)
    
    # Generate a visualization
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x="ds", y="y", label="Actual Sentiment Trend")
    sns.lineplot(data=forecast, x="ds", y="yhat", label="Predicted Trend", linestyle="dashed")
    plt.title(f"Sentiment Trend Analysis for {region}")
    plt.xlabel("Date")
    plt.ylabel("Sentiment Score")
    plt.legend()
    plt.show()
    
    return {
        "region": region,
        "trending_topics": topics,
        "forecast_data": forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]
    }

# Example Usage
if __name__ == "__main__":
    sample_texts = [
        "AI is transforming the media industry!", "Privacy laws are affecting data scraping.",
        "Social media trends change every week.", "Brandwatch released a new feature.",
        "Compliance with GDPR is a growing concern."
    ]
    sample_dates = pd.date_range(start="2025-01-01", periods=len(sample_texts), freq="D")
    
    results = trend_analysis(sample_texts, sample_dates, region="USA")
    
    print("\nTrending Topics:")
    for topic in results["trending_topics"]:
        print(topic)

    print("\nForecast Data:")
    print(results["forecast_data"].head())

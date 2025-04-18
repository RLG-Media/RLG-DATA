#!/usr/bin/env python3
"""
RLG Automated Sentiment Analysis Module
----------------------------------------
This module automates sentiment analysis for RLG Data and RLG Fans. It is:
- Robust, data-driven, and scalable
- Integrates with RLG's scraping, compliance, and Super Tool
- Provides real-time sentiment classification (positive, neutral, negative)
- Supports multiple languages and regional dialects
- Includes both a Transformer (BERT) model and a backup Naïve Bayes model
"""

import re
import torch
import numpy as np
import pandas as pd
import nltk
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from langdetect import detect
from textblob import TextBlob
from nltk.corpus import stopwords

# Download NLTK resources
nltk.download('stopwords')

# Load English stopwords
STOPWORDS = set(stopwords.words('english'))

# Load the pre-trained Transformer sentiment model
transformer_model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
tokenizer = AutoTokenizer.from_pretrained(transformer_model_name)
transformer_model = AutoModelForSequenceClassification.from_pretrained(transformer_model_name)
sentiment_pipeline = pipeline("sentiment-analysis", model=transformer_model, tokenizer=tokenizer)

# Naïve Bayes Backup Model
class SentimentClassifierNB:
    """Backup sentiment classifier using Naïve Bayes (for fallback if Transformer fails)."""
    def __init__(self):
        self.vectorizer = CountVectorizer(stop_words='english')
        self.tfidf_transformer = TfidfTransformer()
        self.model = MultinomialNB()
    
    def train(self, texts, labels):
        X_counts = self.vectorizer.fit_transform(texts)
        X_tfidf = self.tfidf_transformer.fit_transform(X_counts)
        self.model.fit(X_tfidf, labels)
    
    def predict(self, text):
        X_counts = self.vectorizer.transform([text])
        X_tfidf = self.tfidf_transformer.transform(X_counts)
        return self.model.predict(X_tfidf)[0]

# Instantiate the Naïve Bayes classifier
nb_classifier = SentimentClassifierNB()

# Train the Naïve Bayes Model (Dummy Data for Now - Replace with Real Data)
train_texts = [
    "I love this tool, it's amazing!", "Worst experience ever.", "Not bad, could be better.",
    "Fantastic service!", "Terrible platform, do not recommend.", "I am neutral about this."
]
train_labels = ["positive", "negative", "neutral", "positive", "negative", "neutral"]
nb_classifier.train(train_texts, train_labels)

# Preprocessing Function
def clean_text(text):
    """Cleans input text by removing special characters, stopwords, and excessive spaces."""
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'\W', ' ', text)  # Remove non-word characters
    text = ' '.join([word for word in text.split() if word not in STOPWORDS])  # Remove stopwords
    return text.strip()

# Sentiment Analysis Function
def analyze_sentiment(text):
    """
    Analyzes sentiment of a given text using Transformer (BERT) model.
    Falls back to Naïve Bayes if Transformer fails.
    """
    text = clean_text(text)
    
    if not text:
        return "neutral"

    try:
        # Try Transformer Model First
        sentiment_result = sentiment_pipeline(text)[0]
        label = sentiment_result['label']
        score = sentiment_result['score']

        if "1 star" in label or "2 stars" in label:
            return "negative"
        elif "3 stars" in label:
            return "neutral"
        else:
            return "positive"

    except Exception as e:
        print(f"Transformer Model Failed. Using Naïve Bayes. Error: {e}")
        return nb_classifier.predict(text)

# Regional Analysis Function
def analyze_sentiment_with_region(text, region="global"):
    """
    Enhances sentiment analysis by considering regional variations.
    Uses TextBlob for basic polarity analysis as a supplement.
    """
    try:
        language = detect(text)
    except:
        language = "unknown"

    sentiment = analyze_sentiment(text)

    # Adjust based on region (if needed)
    if region.lower() in ["usa", "canada", "uk"]:
        if TextBlob(text).sentiment.polarity > 0.3:
            sentiment = "positive"
        elif TextBlob(text).sentiment.polarity < -0.3:
            sentiment = "negative"

    return {
        "text": text,
        "region": region,
        "language": language,
        "sentiment": sentiment
    }

# Bulk Sentiment Analysis Function
def bulk_analyze_sentiment(text_list, region="global"):
    """Analyzes sentiment for a list of texts and returns a structured dataframe."""
    results = [analyze_sentiment_with_region(text, region) for text in text_list]
    return pd.DataFrame(results)

# Example Usage
if __name__ == "__main__":
    sample_texts = [
        "I love the RLG Super Tool, it makes my job so much easier!",
        "The compliance system is terrible and slow.",
        "Not sure how I feel about this platform.",
        "This is the best media monitoring service I have used!",
        "Why is the scraping tool not working as expected?"
    ]
    
    df_results = bulk_analyze_sentiment(sample_texts, region="USA")
    print(df_results)

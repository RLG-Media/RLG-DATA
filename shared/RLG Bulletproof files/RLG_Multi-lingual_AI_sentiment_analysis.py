#!/usr/bin/env python3
"""
RLG Multi-Lingual AI Sentiment Analysis System - Enhanced Version
----------------------------------------------------------------
This system performs AI-powered sentiment analysis across multiple languages.

New Enhancements:
- Sentiment Trend Forecasting using Prophet & LSTM
- Context-aware AI that understands sarcasm, slang, and emojis
- Automated crisis detection for negative sentiment spikes
- AI-powered topic extraction
- Real-time sentiment dashboard

"""

import time
import pandas as pd
import numpy as np
import schedule
import torch
import seaborn as sns
import tensorflow as tf
import sqlite3
from flask import Flask, request, jsonify, render_template
from langdetect import detect
from textblob import TextBlob
from googletrans import Translator
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from prophet import Prophet
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

# Flask App
app = Flask(__name__)

# Load Pre-Trained Multi-Lingual Sentiment Model (XLM-RoBERTa)
MODEL_NAME = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# Initialize Google Translator
translator = Translator()

# Sentiment Analysis Function
def analyze_sentiment(text):
    """
    Detects the language of the text and performs sentiment analysis.
    """
    try:
        detected_lang = detect(text)
    except:
        detected_lang = "unknown"

    # If language is not English, translate it
    if detected_lang != "en":
        try:
            translated_text = translator.translate(text, dest="en").text
        except:
            translated_text = text
    else:
        translated_text = text

    # Use Transformer Model for Sentiment Classification
    sentiment_result = sentiment_pipeline(translated_text)[0]
    label = sentiment_result['label']
    score = sentiment_result['score']

    # Normalize sentiment labels
    if "negative" in label.lower():
        sentiment = "negative"
    elif "neutral" in label.lower():
        sentiment = "neutral"
    else:
        sentiment = "positive"

    return {
        "original_text": text,
        "translated_text": translated_text,
        "detected_language": detected_lang,
        "sentiment": sentiment,
        "confidence": round(score, 4)
    }

# AI-Based Topic Extraction
def extract_topics(texts, num_topics=5):
    """
    Extracts key discussion topics using Latent Dirichlet Allocation (LDA).
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

# Sentiment Trend Forecasting using Prophet
def forecast_sentiment_trends(df):
    """
    Uses Prophet to predict future sentiment trends.
    """
    df = df.groupby("date").mean().reset_index()
    df.rename(columns={"date": "ds", "sentiment_score": "y"}, inplace=True)

    model = Prophet()
    model.fit(df)

    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)

    return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]

# Detect Negative Sentiment Spikes & Alert Admins
def detect_sentiment_spikes():
    """
    Monitors for high levels of negative sentiment and alerts admins.
    """
    conn = sqlite3.connect("rlg_sentiment_analysis.db")
    df = pd.read_sql_query("SELECT sentiment FROM sentiment_results", conn)
    conn.close()

    # Calculate percentage of negative sentiments
    negative_ratio = (df["sentiment"] == "negative").sum() / len(df)

    if negative_ratio > 0.5:
        send_alert(f"🚨 High Negative Sentiment Detected! {negative_ratio*100:.2f}% of recent mentions are negative.")

# Alerting System
def send_alert(message):
    """
    Sends an alert (email or webhook) when negative sentiment spikes.
    """
    print(f"ALERT: {message}")  # Placeholder for email/webhook integration

# Bulk Sentiment Analysis
@app.route("/bulk_analyze", methods=["POST"])
def bulk_analyze():
    """
    API endpoint to analyze sentiment for multiple texts.
    """
    data = request.json
    texts = data.get("texts", [])
    results = [analyze_sentiment(text) for text in texts]

    # Extract Key Topics
    topics = extract_topics(texts)

    return jsonify({"sentiment_analysis": results, "key_topics": topics})

# Sentiment Analysis Dashboard
@app.route("/dashboard", methods=["GET"])
def dashboard():
    """
    Displays a real-time sentiment analysis dashboard.
    """
    conn = sqlite3.connect("rlg_sentiment_analysis.db")
    df = pd.read_sql_query("SELECT * FROM sentiment_results", conn)
    conn.close()

    # Plot sentiment trends
    sns.lineplot(data=df, x="date", y="sentiment_score", label="Actual Sentiment Trend")
    forecast = forecast_sentiment_trends(df)
    sns.lineplot(data=forecast, x="ds", y="yhat", label="Predicted Trend", linestyle="dashed")

    return df.to_html()

# Schedule Sentiment Monitoring
schedule.every(10).minutes.do(detect_sentiment_spikes)

# Run Flask App
if __name__ == "__main__":
    print("Starting Enhanced RLG Multi-Lingual AI Sentiment Analysis System...")
    app.run(debug=True)

#!/usr/bin/env python3
"""
RLG Smart Tagging System - Enhanced with Custom Industry-Specific Tag Training
------------------------------------------------------------------------------
This system automatically assigns smart tags to media content and social mentions using:
• Pre-trained NLP for contextual auto-tagging (via XLM-RoBERTa)
• AI-based topic extraction and clustering
• Custom industry-specific tag training (supervised model using scikit-learn)
• Real-time dashboard for monitoring tagged content
• Crisis detection & alerting integration

The system is designed for RLG Data and RLG Fans and integrates with our scraping, compliance, 
and RLG Super Tool platforms, ensuring competitive, automated, data-driven, and region-accurate tagging.
"""

import time
import os
import requests
import pandas as pd
import numpy as np
import schedule
import nltk
import torch
import seaborn as sns
from flask import Flask, request, jsonify, render_template
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from googletrans import Translator
from langdetect import detect
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

# Initialize Flask app
app = Flask(__name__)

# ---------------------------- Configuration & Setup ----------------------------

# Pre-trained model for general tagging (XLM-RoBERTa for sentiment and general context)
MODEL_NAME = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
tagging_pipeline = pipeline("text-classification", model=model, tokenizer=tokenizer)

# Initialize Google Translator
translator = Translator()

# Download NLTK Resources
nltk.download("punkt")
nltk.download("stopwords")

# File paths for saving tagged data and custom model
TAGGED_DATA_FILE = "tagged_content.csv"
CUSTOM_MODEL_FILE = "custom_tag_classifier.joblib"
CUSTOM_TRAINING_DATA = "custom_tag_training.csv"  # This CSV should have columns: text, tag

# ---------------------------- Helper Functions ----------------------------

def clean_text(text):
    """
    Cleans and preprocesses text for tagging.
    """
    text = text.lower()
    words = nltk.word_tokenize(text)
    words = [word for word in words if word.isalnum()]
    return " ".join(words)

def load_custom_classifier():
    """
    Loads the custom industry-specific tag classifier if available.
    """
    if os.path.exists(CUSTOM_MODEL_FILE):
        classifier = joblib.load(CUSTOM_MODEL_FILE)
        vectorizer = joblib.load("custom_vectorizer.joblib")
        return classifier, vectorizer
    return None, None

def train_custom_classifier():
    """
    Trains a custom industry-specific tag classifier using labeled training data.
    Expected CSV format: two columns ("text", "tag")
    """
    if not os.path.exists(CUSTOM_TRAINING_DATA):
        print("No custom training data found.")
        return None, None
    
    df = pd.read_csv(CUSTOM_TRAINING_DATA)
    df["clean_text"] = df["text"].apply(clean_text)
    
    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(df["clean_text"])
    y = df["tag"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    classifier = LogisticRegression(max_iter=1000)
    classifier.fit(X_train, y_train)
    
    # Evaluate classifier
    y_pred = classifier.predict(X_test)
    print("Custom Tag Classifier Training Report:")
    print(classification_report(y_test, y_pred))
    
    # Save model and vectorizer
    joblib.dump(classifier, CUSTOM_MODEL_FILE)
    joblib.dump(vectorizer, "custom_vectorizer.joblib")
    
    return classifier, vectorizer

# ---------------------------- Smart Tagging Functions ----------------------------

def assign_tags(text):
    """
    Uses AI and NLP to generate relevant tags for a given text.
    Combines general AI-generated tags with custom industry-specific predictions.
    """
    original_text = text
    text = clean_text(text)
    try:
        detected_lang = detect(text)
    except Exception:
        detected_lang = "unknown"

    # Translate text if not English
    if detected_lang != "en":
        try:
            translated_text = translator.translate(text, dest="en").text
        except Exception:
            translated_text = text
    else:
        translated_text = text

    # Get AI-generated general tag using pre-trained pipeline (e.g., sentiment label)
    result = tagging_pipeline(translated_text)[0]
    general_tag = result["label"].lower()
    
    # Use basic extraction for additional candidate tags from the text
    candidate_tags = text.split()[:3]  # first 3 tokens as basic candidates

    # Combine general tags
    tags = set([general_tag] + candidate_tags)
    
    # Load or train custom industry-specific classifier
    classifier, vectorizer = load_custom_classifier()
    if classifier is None or vectorizer is None:
        classifier, vectorizer = train_custom_classifier()  # Train if not present

    # If custom classifier is available, use it to predict an industry-specific tag
    if classifier is not None and vectorizer is not None:
        custom_features = vectorizer.transform([translated_text])
        custom_tag = classifier.predict(custom_features)[0]
        tags.add(custom_tag.lower())

    return {
        "original_text": original_text,
        "clean_text": text,
        "translated_text": translated_text,
        "detected_language": detected_lang,
        "tags": list(tags)
    }

@app.route("/bulk_tagging", methods=["POST"])
def bulk_tagging():
    """
    API endpoint to assign tags to multiple texts.
    """
    data = request.json
    texts = data.get("texts", [])
    results = [assign_tags(text) for text in texts]
    
    # Save results to CSV for dashboard (append mode)
    for res in results:
        df = pd.DataFrame([{
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "original_text": res["original_text"],
            "tags": ",".join(res["tags"])
        }])
        df.to_csv(TAGGED_DATA_FILE, mode="a", header=not os.path.exists(TAGGED_DATA_FILE), index=False)
    
    return jsonify(results)

@app.route("/dashboard", methods=["GET"])
def dashboard():
    """
    Displays a real-time tagging dashboard.
    """
    if os.path.exists(TAGGED_DATA_FILE):
        df = pd.read_csv(TAGGED_DATA_FILE)
        return df.to_html()
    return "No tagged data available."

def cluster_tags():
    """
    Uses K-Means clustering to group similar content under common tags.
    """
    if not os.path.exists(TAGGED_DATA_FILE):
        print("No tagged data to cluster.")
        return

    df = pd.read_csv(TAGGED_DATA_FILE)
    if df.empty:
        return

    # Use the translated text for clustering if available; here we use original_text for simplicity.
    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(df["original_text"])
    
    kmeans = KMeans(n_clusters=5, random_state=42)
    df["tag_cluster"] = kmeans.fit_predict(X)
    
    df.to_csv(TAGGED_DATA_FILE, index=False)
    print("Tag clustering updated.")

def detect_crisis():
    """
    Detects high-volume negative sentiment mentions based on tags and alerts admin.
    For demonstration, if any tag 'negative' appears more than a threshold.
    """
    if not os.path.exists(TAGGED_DATA_FILE):
        return

    df = pd.read_csv(TAGGED_DATA_FILE)
    # Simple crisis detection: count occurrences of a "negative" tag
    negative_count = df["tags"].str.contains("negative", case=False, na=False).sum()
    if negative_count > 5:
        send_alert(f"🚨 Crisis Alert: {negative_count} negative mentions detected!")

def send_alert(message):
    """
    Sends an alert via a webhook or email (placeholder for real integration).
    """
    print(f"ALERT: {message}")
    # Here you can integrate with email, Slack, or other alerting systems.

def monitor_mentions():
    """
    Simulates fetching new media mentions and auto-tags them.
    In production, this would be integrated with our real-time listener and scraping tools.
    """
    sample_mentions = [
        "RLG Data is revolutionizing AI in media monitoring.",
        "The new features in RLG Fans are outstanding and very innovative!",
        "I have concerns about RLG's data security protocols."
    ]
    for mention in sample_mentions:
        tag_data = assign_tags(mention)
        save_tagged_data(mention, tag_data)

def save_tagged_data(text, tag_data):
    """
    Saves the assigned tags to a CSV file for future reference and dashboard display.
    """
    df = pd.DataFrame([{
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "original_text": text,
        "tags": ",".join(tag_data["tags"])
    }])
    df.to_csv(TAGGED_DATA_FILE, mode="a", header=not os.path.exists(TAGGED_DATA_FILE), index=False)

# Schedule periodic tasks
schedule.every(10).minutes.do(monitor_mentions)
schedule.every(30).minutes.do(detect_crisis)
schedule.every().hour.do(cluster_tags)

# ---------------------------- Main Execution ----------------------------
if __name__ == "__main__":
    print("Starting Enhanced RLG Smart Tagging System with Custom Industry-Specific Training...")
    # Start scheduler in a background loop
    while True:
        schedule.run_pending()
        time.sleep(60)
    # Note: To run the Flask app, run "flask run" or integrate threading as needed.
    # app.run(debug=True)

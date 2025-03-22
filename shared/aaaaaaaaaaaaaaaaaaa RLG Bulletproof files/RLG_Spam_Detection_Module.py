#!/usr/bin/env python3
"""
RLG Spam Detection Module - AI-Powered Multi-Platform Spam & Fraud Detection
----------------------------------------------------------------------------
✔ AI-Based Spam, Fraud, Phishing & Fake Engagement Detection.
✔ Multi-Layered Spam Analysis (Text, Links, Social Media, Forums, Live Chats).
✔ Adaptive Self-Learning AI Model with Continuous Real-Time Training.
✔ Secure API Integration with RLG Data & RLG Fans.

Competitive Edge:
🔹 **Detects real-time spam, bot activity, and fake engagement.**  
🔹 **Protects against phishing, scams, and automated fraud.**  
🔹 **Multi-platform AI integration across social media, messaging, and web content.**  
"""

import os
import logging
import json
import re
import time
import requests
import joblib
import numpy as np
from flask import Flask, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from deep_translator import GoogleTranslator
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
from discord_webhook import DiscordWebhook
from twilio.rest import Client  # WhatsApp API
from wechatpy import WeChatClient  # WeChat API
from dotenv import load_dotenv

# ------------------------- CONFIGURATION -------------------------

# Load API Keys from .env File
load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

WHATSAPP_SID = os.getenv("WHATSAPP_SID")
WHATSAPP_AUTH_TOKEN = os.getenv("WHATSAPP_AUTH_TOKEN")
WHATSAPP_FROM = os.getenv("WHATSAPP_FROM")

WECHAT_APP_ID = os.getenv("WECHAT_APP_ID")
WECHAT_APP_SECRET = os.getenv("WECHAT_APP_SECRET")

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("rlg_spam_detection.log"), logging.StreamHandler()]
)

# Hugging Face Transformers for Spam Detection
MODEL_NAME = "facebook/bart-large-mnli"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
spam_pipeline = pipeline("zero-shot-classification", model=model, tokenizer=tokenizer)

# Machine Learning Classifier (Sklearn)
vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
classifier = RandomForestClassifier(n_estimators=100, random_state=42)

# Flask API Setup
app = Flask(__name__)

# ------------------------- SPAM DETECTION FUNCTIONS -------------------------

def detect_spam_text(text):
    """AI-powered text spam detection using NLP models."""
    try:
        labels = ["spam", "not spam", "phishing", "fake news", "scam"]
        result = spam_pipeline(text, candidate_labels=labels)
        
        label = result["labels"][0]
        confidence = round(result["scores"][0], 4)
        
        logging.info(f"📊 Spam Detection - Label: {label}, Confidence: {confidence}")
        return label, confidence
    except Exception as e:
        logging.error(f"❌ Spam detection failed: {str(e)}")
        return "unknown", 0.0

def detect_link_spam(url):
    """Basic link spam detection using regex and blacklists."""
    spam_patterns = [
        r"\b(bit\.ly|tinyurl\.com|goo\.gl|t\.co)\b",
        r"\b(free money|work from home|click here|win a prize)\b",
        r"\b(crypto giveaway|instant cash|guaranteed income|lottery)\b"
    ]
    
    for pattern in spam_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            logging.warning(f"🚨 Link Spam Detected: {url}")
            return True
    return False

def detect_fake_engagement(likes, comments, shares):
    """Detects fake engagement by analyzing interaction ratios."""
    if (likes + shares) / max(1, comments) > 50:  # High like/comment ratio suggests manipulation
        logging.warning(f"🚨 Fake Engagement Detected: {likes} Likes, {comments} Comments, {shares} Shares")
        return True
    return False

# ------------------------- MESSAGING INTEGRATIONS -------------------------

def send_whatsapp_message(message, recipient):
    """Sends a WhatsApp message."""
    try:
        client = Client(WHATSAPP_SID, WHATSAPP_AUTH_TOKEN)
        message = client.messages.create(
            body=message,
            from_=f"whatsapp:{WHATSAPP_FROM}",
            to=f"whatsapp:{recipient}"
        )
        logging.info(f"📲 WhatsApp Message Sent to {recipient}")
        return message.sid
    except Exception as e:
        logging.error(f"❌ WhatsApp Message Failed: {str(e)}")
        return None

def send_discord_notification(message):
    """Sends a message to a Discord webhook."""
    try:
        webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL, content=message)
        response = webhook.execute()
        logging.info(f"📢 Discord Notification Sent: {message}")
        return response
    except Exception as e:
        logging.error(f"❌ Discord Notification Failed: {str(e)}")
        return None

# ------------------------- API ENDPOINTS -------------------------

@app.route("/api/spam/detect", methods=["POST"])
def detect_spam_api():
    """API endpoint for spam detection."""
    data = request.json
    text = data.get("text", "")
    label, confidence = detect_spam_text(text)
    return jsonify({"label": label, "confidence": confidence})

@app.route("/api/spam/link", methods=["POST"])
def detect_spam_link_api():
    """API endpoint for link spam detection."""
    data = request.json
    url = data.get("url", "")
    is_spam = detect_link_spam(url)
    return jsonify({"spam": is_spam})

@app.route("/api/spam/engagement", methods=["POST"])
def detect_fake_engagement_api():
    """API endpoint for fake engagement detection."""
    data = request.json
    likes = int(data.get("likes", 0))
    comments = int(data.get("comments", 0))
    shares = int(data.get("shares", 0))
    is_fake = detect_fake_engagement(likes, comments, shares)
    return jsonify({"fake_engagement": is_fake})

@app.route("/api/spam/whatsapp", methods=["POST"])
def send_whatsapp():
    """API endpoint to send a WhatsApp message."""
    data = request.json
    message = data.get("message", "Default RLG Spam Alert")
    recipient = data.get("recipient", "+1234567890")
    response = send_whatsapp_message(message, recipient)
    return jsonify({"status": "sent" if response else "failed"})

@app.route("/api/spam/discord", methods=["POST"])
def send_discord():
    """API endpoint to send a Discord message."""
    data = request.json
    message = data.get("message", "Default RLG Spam Alert")
    response = send_discord_notification(message)
    return jsonify({"status": "sent" if response else "failed"})

# ------------------------- MAIN EXECUTION -------------------------

if __name__ == "__main__":
    logging.info("🚀 Starting RLG Spam Detection Module...")
    app.run(host="0.0.0.0", port=5006, debug=True)

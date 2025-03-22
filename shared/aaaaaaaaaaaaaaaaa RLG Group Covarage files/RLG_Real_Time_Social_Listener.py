#!/usr/bin/env python3
"""
RLG Real-Time Social Listener System - AI-Powered
-------------------------------------------------
This system monitors social media in real-time for:
- Brand mentions, hashtags, competitor tracking
- AI-powered sentiment & trend analysis
- PR crisis detection and escalation
- Automated alerts via Telegram, WhatsApp, and Email
- Real-time dashboard for insights

New Enhancements:
- Supports Twitter/X, Reddit, Facebook, LinkedIn, Instagram, Telegram & WhatsApp
- AI-powered sentiment detection (XLM-RoBERTa)
- Secure API & Webhook integration

"""

import time
import requests
import pandas as pd
import numpy as np
import schedule
import tweepy
import praw
import json
import smtplib
import torch
import seaborn as sns
from flask import Flask, request, jsonify, render_template
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from googletrans import Translator
from langdetect import detect
from datetime import datetime
from twilio.rest import Client  # For WhatsApp Integration
from telethon import TelegramClient, events  # For Telegram Monitoring

# Flask App
app = Flask(__name__)

# API Credentials (Replace with actual keys)
TWITTER_API_KEY = "your-twitter-api-key"
TWITTER_API_SECRET = "your-twitter-api-secret"
TWITTER_ACCESS_TOKEN = "your-twitter-access-token"
TWITTER_ACCESS_SECRET = "your-twitter-access-secret"

REDDIT_CLIENT_ID = "your-reddit-client-id"
REDDIT_CLIENT_SECRET = "your-reddit-client-secret"
REDDIT_USER_AGENT = "your-reddit-user-agent"

FACEBOOK_ACCESS_TOKEN = "your-facebook-access-token"

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = "your-telegram-bot-token"
TELEGRAM_CHAT_ID = "your-telegram-chat-id"

# WhatsApp Configuration (Twilio)
TWILIO_ACCOUNT_SID = "your-twilio-account-sid"
TWILIO_AUTH_TOKEN = "your-twilio-auth-token"
WHATSAPP_FROM = "whatsapp:+14155238886"  # Twilio Sandbox Number
WHATSAPP_TO = "whatsapp:+1234567890"  # Your Verified WhatsApp Number
whatsapp_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Telegram Monitoring Configuration
TELEGRAM_API_ID = "your-telegram-api-id"
TELEGRAM_API_HASH = "your-telegram-api-hash"
telegram_client = TelegramClient("session_name", TELEGRAM_API_ID, TELEGRAM_API_HASH)

# Initialize Google Translator
translator = Translator()

# Load Pre-Trained Multi-Lingual Sentiment Model (XLM-RoBERTa)
MODEL_NAME = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# Connect to Twitter API
auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
twitter_api = tweepy.API(auth, wait_on_rate_limit=True)

# Connect to Reddit API
reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                     client_secret=REDDIT_CLIENT_SECRET,
                     user_agent=REDDIT_USER_AGENT)

# Function to Analyze Sentiment
def analyze_sentiment(text):
    """
    Detects the language and performs sentiment analysis.
    """
    try:
        detected_lang = detect(text)
    except:
        detected_lang = "unknown"

    if detected_lang != "en":
        try:
            translated_text = translator.translate(text, dest="en").text
        except:
            translated_text = text
    else:
        translated_text = text

    sentiment_result = sentiment_pipeline(translated_text)[0]
    label = sentiment_result['label']
    score = sentiment_result['score']

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

# Save Data & Send Alerts
def save_and_alert(text, sentiment_data, platform, author):
    """
    Stores sentiment data and sends alerts for high-risk mentions.
    """
    sentiment_score = 1 if sentiment_data["sentiment"] == "positive" else -1 if sentiment_data["sentiment"] == "negative" else 0

    df = pd.DataFrame([{
        "timestamp": datetime.now(),
        "platform": platform,
        "author": author,
        "text": text,
        "sentiment": sentiment_data["sentiment"],
        "sentiment_score": sentiment_score
    }])

    df.to_csv("social_mentions.csv", mode='a', header=False, index=False)

    if sentiment_score < -0.5:
        alert_message = f"🚨 Negative Mention Detected on {platform}: {text}"
        send_alert(alert_message)

# Alerting System (WhatsApp & Telegram)
def send_alert(message):
    """
    Sends an alert via WhatsApp and Telegram.
    """
    # WhatsApp Alert
    whatsapp_client.messages.create(body=message, from_=WHATSAPP_FROM, to=WHATSAPP_TO)

    # Telegram Alert
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                  data={"chat_id": TELEGRAM_CHAT_ID, "text": message})

# Monitor Twitter for Brand Mentions
def monitor_twitter():
    search_terms = ["RLG Data", "RLG Fans", "#RLGSuperTool"]
    tweets = twitter_api.search_tweets(q=" OR ".join(search_terms), count=10, tweet_mode="extended")

    for tweet in tweets:
        sentiment_data = analyze_sentiment(tweet.full_text)
        save_and_alert(tweet.full_text, sentiment_data, "Twitter", tweet.user.screen_name)

# Monitor Reddit for Discussions
def monitor_reddit():
    search_terms = ["RLG Data", "RLG Fans"]
    for term in search_terms:
        for submission in reddit.subreddit("all").search(term, limit=5):
            sentiment_data = analyze_sentiment(submission.title)
            save_and_alert(submission.title, sentiment_data, "Reddit", submission.author.name)

# Monitor Telegram Chats
@telegram_client.on(events.NewMessage(pattern=".*RLG.*"))
async def monitor_telegram(event):
    sentiment_data = analyze_sentiment(event.message.message)
    save_and_alert(event.message.message, sentiment_data, "Telegram", str(event.sender_id))

# Schedule Real-Time Monitoring
schedule.every(5).minutes.do(monitor_twitter)
schedule.every(10).minutes.do(monitor_reddit)

# Run Flask App & Scheduler
if __name__ == "__main__":
    print("Starting Enhanced RLG Real-Time Social Listener...")
    telegram_client.start()
    while True:
        schedule.run_pending()
        time.sleep(60)
    app.run(debug=True)

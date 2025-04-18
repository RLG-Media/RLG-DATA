#!/usr/bin/env python3
"""
RLG Real-Time Media Alerts System
----------------------------------------
This module enables real-time media monitoring for RLG Data and RLG Fans. It:
- Scrapes media sources and detects new mentions
- Sends real-time alerts via Email, Slack, and Webhooks
- Tracks keywords, sentiment, and regional data
- Integrates with RLG's scraping, sentiment analysis, and compliance tools
"""

import re
import time
import json
import requests
import smtplib
import schedule
import pandas as pd
import nltk
from bs4 import BeautifulSoup
from nltk.sentiment import SentimentIntensityAnalyzer
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Download required NLTK resources
nltk.download('vader_lexicon')

# Initialize Sentiment Analyzer
sia = SentimentIntensityAnalyzer()

# Configuration for Alerts
CONFIG = {
    "keywords": ["RLG Data", "RLG Fans", "AI-driven monitoring", "media compliance"],
    "regions": ["USA", "UK", "Canada", "Germany", "Australia"],
    "email_alerts": True,
    "slack_alerts": True,
    "webhook_alerts": True,
    "email_config": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "email_sender": "your-email@gmail.com",
        "email_password": "your-password",
        "email_recipients": ["recipient1@example.com", "recipient2@example.com"]
    },
    "slack_config": {
        "slack_token": "your-slack-bot-token",
        "slack_channel": "#media-alerts"
    },
    "webhook_url": "https://your-webhook-url.com"
}

# Function to clean and preprocess text
def clean_text(text):
    """Removes special characters, excess whitespace, and converts text to lowercase."""
    text = re.sub(r'\W', ' ', text)
    return text.lower().strip()

# Function to analyze sentiment
def analyze_sentiment(text):
    """Returns sentiment classification (positive, neutral, or negative)."""
    sentiment_score = sia.polarity_scores(text)['compound']
    if sentiment_score >= 0.05:
        return "positive"
    elif sentiment_score <= -0.05:
        return "negative"
    return "neutral"

# Function to scrape media sources for new mentions
def scrape_media_sources():
    """Scrapes multiple media sources for relevant mentions."""
    sources = [
        "https://news.google.com/search?q=RLG+Data",
        "https://news.google.com/search?q=RLG+Fans",
        "https://www.bbc.com/news",
        "https://www.nytimes.com/"
    ]
    
    detected_mentions = []
    
    for url in sources:
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(response.text, "html.parser")
            articles = soup.find_all("a", href=True)
            
            for article in articles:
                title = article.text.strip()
                link = article["href"]
                if any(keyword.lower() in title.lower() for keyword in CONFIG["keywords"]):
                    sentiment = analyze_sentiment(title)
                    detected_mentions.append({
                        "title": title,
                        "link": link,
                        "sentiment": sentiment
                    })
        except Exception as e:
            print(f"Error scraping {url}: {e}")
    
    return detected_mentions

# Function to send email alerts
def send_email_alerts(mentions):
    """Sends an email notification with new media mentions."""
    if not CONFIG["email_alerts"] or not mentions:
        return
    
    email_body = "Real-Time Media Alerts:\n\n"
    for mention in mentions:
        email_body += f"{mention['title']} ({mention['sentiment'].capitalize()})\n{mention['link']}\n\n"
    
    try:
        server = smtplib.SMTP(CONFIG["email_config"]["smtp_server"], CONFIG["email_config"]["smtp_port"])
        server.starttls()
        server.login(CONFIG["email_config"]["email_sender"], CONFIG["email_config"]["email_password"])
        for recipient in CONFIG["email_config"]["email_recipients"]:
            server.sendmail(CONFIG["email_config"]["email_sender"], recipient, email_body)
        server.quit()
        print("Email alerts sent successfully.")
    except Exception as e:
        print(f"Error sending email alerts: {e}")

# Function to send Slack alerts
def send_slack_alerts(mentions):
    """Sends media alerts to a Slack channel."""
    if not CONFIG["slack_alerts"] or not mentions:
        return
    
    slack_client = WebClient(token=CONFIG["slack_config"]["slack_token"])
    
    for mention in mentions:
        message = f"*New Media Mention:* {mention['title']} ({mention['sentiment'].capitalize()})\n<{mention['link']}|Read More>"
        try:
            slack_client.chat_postMessage(channel=CONFIG["slack_config"]["slack_channel"], text=message)
        except SlackApiError as e:
            print(f"Error sending Slack alert: {e}")

# Function to send webhook alerts
def send_webhook_alerts(mentions):
    """Sends media alerts to an external webhook."""
    if not CONFIG["webhook_alerts"] or not mentions:
        return
    
    payload = json.dumps({"mentions": mentions})
    try:
        response = requests.post(CONFIG["webhook_url"], data=payload, headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            print("Webhook alerts sent successfully.")
        else:
            print(f"Error sending webhook alerts: {response.text}")
    except Exception as e:
        print(f"Error sending webhook alerts: {e}")

# Function to monitor media mentions and send alerts
def monitor_media_mentions():
    """Main function to detect and send alerts for new media mentions."""
    print("Checking for new media mentions...")
    mentions = scrape_media_sources()
    
    if mentions:
        print(f"New mentions detected: {len(mentions)}")
        send_email_alerts(mentions)
        send_slack_alerts(mentions)
        send_webhook_alerts(mentions)
    else:
        print("No new media mentions found.")

# Schedule the function to run every 30 minutes
schedule.every(30).minutes.do(monitor_media_mentions)

# Run the monitoring continuously
if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(60)

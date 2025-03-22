import os
import json
import requests
import logging
import pandas as pd
from datetime import datetime
from textblob import TextBlob
from deepseek import DeepSeekAI  # AI-powered insights
from googleapiclient.discovery import build
from social_media_api_clients import TwitterClient, TikTokClient, FacebookClient, RedditClient, InstagramClient, YouTubeClient, LinkedInClient, PinterestClient, ThreadsClient, SnapchatClient

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("social_media_trends.log"), logging.StreamHandler()]
)

# API Keys & Configuration
GOOGLE_TRENDS_API_KEY = os.getenv("GOOGLE_TRENDS_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# Initialize API Clients
twitter_client = TwitterClient(TWITTER_BEARER_TOKEN)
tiktok_client = TikTokClient(os.getenv("TIKTOK_API_KEY"))
facebook_client = FacebookClient(os.getenv("FACEBOOK_ACCESS_TOKEN"))
reddit_client = RedditClient(os.getenv("REDDIT_API_KEY"))
instagram_client = InstagramClient(os.getenv("INSTAGRAM_ACCESS_TOKEN"))
youtube_client = YouTubeClient(os.getenv("YOUTUBE_API_KEY"))
linkedin_client = LinkedInClient(os.getenv("LINKEDIN_API_KEY"))
pinterest_client = PinterestClient(os.getenv("PINTEREST_API_KEY"))
threads_client = ThreadsClient(os.getenv("THREADS_API_KEY"))
snapchat_client = SnapchatClient(os.getenv("SNAPCHAT_API_KEY"))

# Google Trends API
def fetch_google_trends(region="US"):
    """Fetches trending topics from Google Trends for a given region."""
    try:
        service = build("trends", "v1beta", developerKey=GOOGLE_TRENDS_API_KEY)
        request = service.trendingsearches().list(region=region)
        response = request.execute()
        return [trend["title"] for trend in response.get("trendingSearchesDays", [])]
    except Exception as e:
        logging.error(f"⚠️ Error fetching Google Trends for {region}: {e}")
        return []

# Fetch Social Media Trends
def fetch_social_media_trends(region="US"):
    """Fetches trending hashtags and topics from multiple social media platforms."""
    trends = {
        "Twitter": twitter_client.get_trending_topics(region),
        "TikTok": tiktok_client.get_trending_hashtags(region),
        "Facebook": facebook_client.get_trending_posts(region),
        "Reddit": reddit_client.get_trending_subreddits(region),
        "Instagram": instagram_client.get_trending_hashtags(region),
        "YouTube": youtube_client.get_trending_videos(region),
        "LinkedIn": linkedin_client.get_trending_articles(region),
        "Pinterest": pinterest_client.get_trending_pins(region),
        "Threads": threads_client.get_trending_posts(region),
        "Snapchat": snapchat_client.get_trending_snaps(region),
        "Google Trends": fetch_google_trends(region),
    }
    return trends

# Sentiment Analysis
def analyze_sentiment(text):
    """Analyzes sentiment of a given text using AI-powered NLP."""
    sentiment = TextBlob(text).sentiment.polarity
    if sentiment > 0.2:
        return "Positive"
    elif sentiment < -0.2:
        return "Negative"
    return "Neutral"

# AI-Powered Trend Analysis
def ai_analyze_trends(trends):
    """Uses DeepSeek AI to analyze social media trends and predict emerging patterns."""
    ai_client = DeepSeekAI(DEEPSEEK_API_KEY)
    trend_data = json.dumps(trends)
    analysis = ai_client.analyze(text=trend_data, task="trend-prediction")
    return analysis

# Save Trends Report
def save_trends_report(trends, region):
    """Saves social media trends as a report."""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"trends_report_{region}_{timestamp}.csv"
    df = pd.DataFrame.from_dict(trends, orient="index").transpose()
    df.to_csv(filename, index=False)
    logging.info(f"✅ Social media trends report saved: {filename}")

# Generate Trend Report
def generate_trend_report(region="US"):
    """Generates and saves a full social media trend report."""
    logging.info(f"🔍 Fetching social media trends for {region}...")
    trends = fetch_social_media_trends(region)
    
    logging.info("📊 Running AI-powered analysis...")
    ai_insights = ai_analyze_trends(trends)
    
    for platform, topics in trends.items():
        for topic in topics:
            sentiment = analyze_sentiment(topic)
            logging.info(f"🔹 {platform} - {topic} - Sentiment: {sentiment}")

    save_trends_report(trends, region)
    
    logging.info("🚀 Trend analysis complete!")
    return {"trends": trends, "ai_insights": ai_insights}

# Run Social Media Trend Analysis
def run_social_media_trends(region="US"):
    """Runs the full social media trends analysis process."""
    logging.info("📢 Running social media regional trends analysis...")
    report = generate_trend_report(region)
    logging.info("✅ Social media trends analysis completed.")
    return report

if __name__ == "__main__":
    run_social_media_trends(region="ZA")  # Example: South Africa Trends

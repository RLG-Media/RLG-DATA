import os
import json
import time
import logging
import requests
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("platform_usage_metrics.log"), logging.StreamHandler()]
)

# Secure Database Connection
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///platform_usage_metrics.db")
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# Platform Usage Metrics Model
class PlatformUsage(Base):
    __tablename__ = "platform_usage"
    id = Column(Integer, primary_key=True, autoincrement=True)
    platform = Column(String, nullable=False)
    active_users = Column(Integer, default=0)
    api_calls = Column(Integer, default=0)
    average_session_time = Column(Float, default=0.0)  # in minutes
    total_engagement = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)

# Social Media API Endpoints for Analytics
PLATFORM_API_ENDPOINTS = {
    "facebook": "https://graph.facebook.com/v12.0/analytics",
    "instagram": "https://graph.instagram.com/me?fields=followers_count",
    "twitter": "https://api.twitter.com/2/tweets/counts/recent",
    "tiktok": "https://open-api.tiktok.com/stats",
    "linkedin": "https://api.linkedin.com/v2/networkSizes/urn:li:person:",
    "youtube": "https://www.googleapis.com/youtube/v3/channels?part=statistics",
    "reddit": "https://www.reddit.com/api/v1/me/karma",
    "snapchat": "https://adsapi.snapchat.com/v1/campaigns",
    "threads": "https://help.instagram.com/517989011717643",
    "pinterest": "https://api.pinterest.com/v5/user_account"
}

# API Authentication Tokens (Stored in Environment Variables)
HEADERS = {
    "Authorization": f"Bearer {os.getenv('API_AUTH_TOKEN', 'your_default_token')}",
    "Content-Type": "application/json"
}

# Fetch Platform Usage Metrics
def fetch_usage_metrics(platform, url):
    """Fetches usage metrics from the platform's API."""
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            metrics = process_metrics(platform, data)
            save_usage_metrics(platform, metrics)
            logging.info(f"✅ {platform.capitalize()} usage metrics updated successfully.")
            return metrics
        else:
            logging.error(f"❌ Failed to fetch metrics for {platform}: HTTP {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"⚠️ Error fetching metrics for {platform}: {str(e)}")
        return None

# Process Metrics Data
def process_metrics(platform, data):
    """Processes raw API data into structured metrics."""
    metrics = {
        "active_users": data.get("active_users", 0),
        "api_calls": data.get("api_calls", 0),
        "average_session_time": data.get("average_session_time", 0.0),
        "total_engagement": data.get("engagement", 0)
    }
    return metrics

# Save Usage Metrics to Database
def save_usage_metrics(platform, metrics):
    """Stores platform usage metrics in the database."""
    entry = PlatformUsage(
        platform=platform,
        active_users=metrics["active_users"],
        api_calls=metrics["api_calls"],
        average_session_time=metrics["average_session_time"],
        total_engagement=metrics["total_engagement"]
    )
    session.add(entry)
    session.commit()

# Retrieve Latest Metrics
def get_latest_metrics():
    """Fetches the most recent usage metrics for all platforms."""
    results = session.query(PlatformUsage).order_by(PlatformUsage.timestamp.desc()).limit(10).all()
    return [{r.platform: r.__dict__} for r in results]

# Run Full Metrics Collection
def run_metrics_collection():
    """Collects and updates usage metrics from all platforms."""
    for platform, url in PLATFORM_API_ENDPOINTS.items():
        fetch_usage_metrics(platform, url)

if __name__ == "__main__":
    run_metrics_collection()

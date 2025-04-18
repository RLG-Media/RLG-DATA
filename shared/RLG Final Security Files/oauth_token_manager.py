import os
import json
import time
import base64
import logging
import requests
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("oauth_token_manager.log"), logging.StreamHandler()]
)

# Secure Database Connection
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///oauth_tokens.db")
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# AES-256 Encryption Key for Token Storage
ENCRYPTION_KEY = os.getenv("OAUTH_ENCRYPTION_KEY", Fernet.generate_key().decode())
cipher = Fernet(ENCRYPTION_KEY.encode())

# OAuth Token Model
class OAuthToken(Base):
    __tablename__ = "oauth_tokens"
    platform = Column(String, primary_key=True)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=False)

Base.metadata.create_all(engine)

# Encrypt & Decrypt Functions
def encrypt_token(token):
    return cipher.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token):
    return cipher.decrypt(encrypted_token.encode()).decode()

# Fetch Token from Database
def get_token(platform):
    """Retrieves and decrypts an OAuth token from the database."""
    token_entry = session.query(OAuthToken).filter_by(platform=platform).first()
    if token_entry:
        return {
            "access_token": decrypt_token(token_entry.access_token),
            "refresh_token": decrypt_token(token_entry.refresh_token) if token_entry.refresh_token else None,
            "expires_at": token_entry.expires_at
        }
    return None

# Save Token to Database
def save_token(platform, access_token, refresh_token, expires_in):
    """Encrypts and stores an OAuth token in the database."""
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
    encrypted_access_token = encrypt_token(access_token)
    encrypted_refresh_token = encrypt_token(refresh_token) if refresh_token else None
    
    token_entry = session.query(OAuthToken).filter_by(platform=platform).first()
    if token_entry:
        token_entry.access_token = encrypted_access_token
        token_entry.refresh_token = encrypted_refresh_token
        token_entry.expires_at = expires_at
    else:
        session.add(OAuthToken(
            platform=platform,
            access_token=encrypted_access_token,
            refresh_token=encrypted_refresh_token,
            expires_at=expires_at
        ))
    session.commit()
    logging.info(f"✅ OAuth token for {platform} saved successfully.")

# Refresh Token Function
def refresh_token(platform, client_id, client_secret, refresh_url):
    """Refreshes an expired OAuth token using the refresh token."""
    token_entry = get_token(platform)
    if not token_entry or not token_entry["refresh_token"]:
        logging.warning(f"⚠️ No refresh token available for {platform}. Re-authentication required.")
        return None

    response = requests.post(refresh_url, data={
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": token_entry["refresh_token"],
        "grant_type": "refresh_token"
    })

    if response.status_code == 200:
        token_data = response.json()
        save_token(
            platform=platform,
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            expires_in=token_data.get("expires_in", 3600)
        )
        return token_data["access_token"]
    else:
        logging.error(f"❌ Failed to refresh token for {platform}: {response.text}")
        return None

# OAuth Token Auto-Refresh Scheduler
def auto_refresh_tokens():
    """Checks and refreshes tokens before they expire."""
    platforms = ["google", "facebook", "instagram", "twitter", "linkedin", "tiktok", "reddit", "youtube", "snapchat"]
    for platform in platforms:
        token_entry = get_token(platform)
        if token_entry and datetime.utcnow() > token_entry["expires_at"] - timedelta(minutes=5):
            logging.info(f"🔄 Refreshing token for {platform}...")
            refresh_token(platform)

# Example OAuth Configurations
OAUTH_CONFIG = {
    "google": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "refresh_url": "https://oauth2.googleapis.com/token"
    },
    "facebook": {
        "client_id": os.getenv("FACEBOOK_CLIENT_ID"),
        "client_secret": os.getenv("FACEBOOK_CLIENT_SECRET"),
        "refresh_url": "https://graph.facebook.com/oauth/access_token"
    },
    "instagram": {
        "client_id": os.getenv("INSTAGRAM_CLIENT_ID"),
        "client_secret": os.getenv("INSTAGRAM_CLIENT_SECRET"),
        "refresh_url": "https://graph.instagram.com/refresh_access_token"
    },
    "twitter": {
        "client_id": os.getenv("TWITTER_CLIENT_ID"),
        "client_secret": os.getenv("TWITTER_CLIENT_SECRET"),
        "refresh_url": "https://api.twitter.com/oauth2/token"
    },
    "linkedin": {
        "client_id": os.getenv("LINKEDIN_CLIENT_ID"),
        "client_secret": os.getenv("LINKEDIN_CLIENT_SECRET"),
        "refresh_url": "https://www.linkedin.com/oauth/v2/accessToken"
    }
}

# Periodically Refresh All Tokens
if __name__ == "__main__":
    auto_refresh_tokens()

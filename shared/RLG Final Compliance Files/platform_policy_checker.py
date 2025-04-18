import os
import json
import logging
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, String, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("platform_policy_checker.log"), logging.StreamHandler()]
)

# Secure Database Connection
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///platform_policies.db")
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# Platform Policy Model
class PlatformPolicy(Base):
    __tablename__ = "platform_policies"
    platform = Column(String, primary_key=True)
    policy_text = Column(String, nullable=False)
    last_updated = Column(DateTime, nullable=False)
    is_compliant = Column(Boolean, default=True)

Base.metadata.create_all(engine)

# Social Media Platforms and Policy URLs
PLATFORM_POLICY_URLS = {
    "facebook": "https://www.facebook.com/policies",
    "instagram": "https://help.instagram.com/581066165581870",
    "twitter": "https://twitter.com/en/tos",
    "tiktok": "https://www.tiktok.com/community-guidelines",
    "linkedin": "https://www.linkedin.com/legal/user-agreement",
    "youtube": "https://www.youtube.com/t/terms",
    "reddit": "https://www.redditinc.com/policies/user-agreement",
    "snapchat": "https://www.snap.com/en-US/terms",
    "threads": "https://help.instagram.com/517989011717643",
    "pinterest": "https://policy.pinterest.com/en/terms-of-service"
}

# Fetch Platform Policies
def fetch_policy(platform, url):
    """Scrapes and fetches the latest platform policy text."""
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            policy_text = soup.get_text()
            save_policy(platform, policy_text)
            logging.info(f"✅ {platform.capitalize()} policy updated successfully.")
            return policy_text
        else:
            logging.error(f"❌ Failed to fetch policy for {platform}: HTTP {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"⚠️ Error fetching policy for {platform}: {str(e)}")
        return None

# Save Policy to Database
def save_policy(platform, policy_text):
    """Stores the latest policy text in the database."""
    last_updated = datetime.utcnow()
    policy_entry = session.query(PlatformPolicy).filter_by(platform=platform).first()
    
    if policy_entry:
        policy_entry.policy_text = policy_text
        policy_entry.last_updated = last_updated
    else:
        session.add(PlatformPolicy(
            platform=platform,
            policy_text=policy_text,
            last_updated=last_updated,
            is_compliant=True
        ))
    
    session.commit()

# Retrieve Stored Policy
def get_stored_policy(platform):
    """Retrieves the latest stored policy from the database."""
    policy_entry = session.query(PlatformPolicy).filter_by(platform=platform).first()
    return policy_entry.policy_text if policy_entry else None

# Check Compliance with Platform Policies
def check_content_compliance(content, platform):
    """Analyzes user content for potential violations of platform policies."""
    policy_text = get_stored_policy(platform)
    if not policy_text:
        logging.warning(f"⚠️ No policy stored for {platform}. Fetching latest version...")
        policy_text = fetch_policy(platform, PLATFORM_POLICY_URLS.get(platform, ""))

    if policy_text and any(keyword in content.lower() for keyword in policy_text.lower().split()):
        logging.warning(f"🚨 Possible policy violation detected for {platform}.")
        return False
    logging.info(f"✅ Content is compliant with {platform}'s policies.")
    return True

# Run Full Policy Compliance Check
def run_policy_check():
    """Fetches, updates, and validates all platform policies."""
    for platform, url in PLATFORM_POLICY_URLS.items():
        fetch_policy(platform, url)

if __name__ == "__main__":
    run_policy_check()

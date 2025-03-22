import os
import json
import logging
import datetime
import requests
import asyncio
from typing import Dict, List, Any, Optional
from openai import OpenAI
from deepseek import DeepSeekAPI
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from email.utils import formataddr
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from PIL import Image
from io import BytesIO

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("RLG_agent.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("RLG Agent")

# API Keys and Configuration
class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    EMAIL_HOST = os.getenv("EMAIL_HOST")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
    EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    SCRAPER_URLS = ["https://rlgdata.com", "https://rlgfans.com"]

# Initialize API Clients
openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
deepseek_client = DeepSeekAPI(api_key=Config.DEEPSEEK_API_KEY)

# RLG Agent Core Class
class RLGAgent:
    def __init__(self):
        self.campaigns = []
        self.email_list = set()
        self.trends = []
        self.load_email_list()
        logger.info("RLG Agent Initialized")

    def load_email_list(self):
        """Load mailing list from stored data."""
        try:
            with open("email_list.json", "r") as file:
                self.email_list = set(json.load(file))
        except FileNotFoundError:
            self.email_list = set()

    def save_email_list(self):
        """Save updated mailing list."""
        with open("email_list.json", "w") as file:
            json.dump(list(self.email_list), file)

    def scrape_emails(self):
        """Scrape emails from registration pages."""
        for url in Config.SCRAPER_URLS:
            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.text, "html.parser")
                emails = set([a.text for a in soup.find_all("a") if "@" in a.text])
                self.email_list.update(emails)
                logger.info(f"Scraped {len(emails)} emails from {url}")
            except Exception as e:
                logger.error(f"Failed to scrape {url}: {str(e)}")
        self.save_email_list()

    def generate_marketing_campaign(self):
        """Create AI-driven marketing campaigns."""
        prompt = """
        Generate a high-converting marketing campaign for RLG Data & RLG Fans. Include:
        - Engaging copy
        - Target audience details
        - Ad copy for different platforms (Twitter, LinkedIn, Instagram, Email)
        - Suggested creatives (images, video ideas)
        - Call-to-action for lead generation
        """
        response = openai_client.Completion.create(
            model="gpt-4",
            prompt=prompt,
            max_tokens=800
        )
        campaign = response["choices"][0]["text"]
        self.campaigns.append(campaign)
        logger.info("New marketing campaign created")
        return campaign

    def send_newsletter(self):
        """Send AI-generated newsletters."""
        newsletter_content = openai_client.Completion.create(
            model="gpt-4",
            prompt="Create an engaging newsletter about RLG Data & RLG Fans.",
            max_tokens=500
        )["choices"][0]["text"]
        
        for email in self.email_list:
            self._send_email(email, "RLG Data & RLG Fans - Latest Updates", newsletter_content)
        logger.info(f"Sent newsletters to {len(self.email_list)} subscribers.")

    def _send_email(self, recipient: str, subject: str, body: str):
        """Send an email."""
        msg = MIMEMultipart()
        msg['From'] = formataddr(("RLG Solutions", Config.EMAIL_USERNAME))
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        
        try:
            server = smtplib.SMTP(Config.EMAIL_HOST, Config.EMAIL_PORT)
            server.starttls()
            server.login(Config.EMAIL_USERNAME, Config.EMAIL_PASSWORD)
            server.sendmail(Config.EMAIL_USERNAME, recipient, msg.as_string())
            server.quit()
            logger.info(f"Email sent to {recipient}")
        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {str(e)}")

    def generate_social_posts(self):
        """Generate 4 daily social media posts using AI."""
        prompt = """
        Generate four high-quality social media posts for RLG Data & RLG Fans. Each post should:
        - Be optimized for Twitter, LinkedIn, and Instagram
        - Include engaging text
        - Suggest hashtags and call-to-actions
        """
        response = openai_client.Completion.create(
            model="gpt-4",
            prompt=prompt,
            max_tokens=1000
        )
        posts = response["choices"][0]["text"].split("\n")
        logger.info("Generated social media posts")
        return posts

    def generate_visual_content(self):
        """Use OpenAI Sora to create images and video content."""
        image_prompt = "Create an engaging promotional image for RLG Data & RLG Fans."
        video_prompt = "Generate a 15-second ad video for RLG Data & RLG Fans."
        
        image_response = openai_client.Image.create(prompt=image_prompt)
        video_response = openai_client.Video.create(prompt=video_prompt)
        
        image_url = image_response["data"]["url"]
        video_url = video_response["data"]["url"]
        logger.info("Generated marketing images and video content")
        return {"image": image_url, "video": video_url}

    def run_automation(self):
        """Run the entire marketing process automatically."""
        self.scrape_emails()
        self.generate_marketing_campaign()
        self.send_newsletter()
        self.generate_social_posts()
        self.generate_visual_content()
        logger.info("RLG Agent completed a full marketing cycle.")

if __name__ == "__main__":
    agent = RLGAgent()
    agent.run_automation()

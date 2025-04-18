# RLG_group_newsletter.py - AI-Powered Automated Newsletter for RLG Data & RLG Fans

import os
import json
import smtplib
import schedule
import time
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
CONFIG = {
    "openai_api_key": os.getenv("OPENAI_API_KEY"),
    "deepseek_api_key": os.getenv("DEEPSEEK_API_KEY"),
    "sora_api_key": os.getenv("SORA_API_KEY"),
    "email_sender": os.getenv("EMAIL_SENDER"),
    "email_password": os.getenv("EMAIL_PASSWORD"),
    "mailing_list_file": "./mailing_list.json",
    "newsletter_schedule": "Monday 09:00",  # Weekly newsletter every Monday at 9 AM
}

# AI Content Generator (ChatGPT & DeepSeek)
def generate_newsletter_content():
    """Generates newsletter content using AI models."""
    prompt = (
        "Write a professional, engaging, and informative newsletter for RLG Data & RLG Fans. "
        "Include insights on data analytics, monetization tips, trending strategies, "
        "and upcoming features. Ensure the content is user-friendly and relevant."
    )
    
    headers = {"Authorization": f"Bearer {CONFIG['deepseek_api_key']}"}
    
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            json={"model": "deepseek-llm-1.3b", "messages": [{"role": "user", "content": prompt}], "max_tokens": 1000},
            headers=headers,
            timeout=10
        )
        
        return response.json()["choices"][0]["message"]["content"]
    
    except requests.RequestException as e:
        print(f"Error generating newsletter content: {e}")
        return "Error: Unable to generate newsletter content."

# AI Image & Video Generator (OpenAI Sora)
def generate_media(prompt, media_type="image"):
    """Generates AI-powered images or videos for newsletters using OpenAI Sora."""
    endpoint = "https://api.openai.com/v1/images" if media_type == "image" else "https://api.openai.com/v1/videos"
    
    headers = {"Authorization": f"Bearer {CONFIG['sora_api_key']}", "Content-Type": "application/json"}
    
    try:
        response = requests.post(endpoint, json={"prompt": prompt}, headers=headers, timeout=10)
        return response.json().get("url", "No media generated")
    
    except requests.RequestException as e:
        print(f"Error generating {media_type}: {e}")
        return None

# Email Sending Function
def send_newsletter():
    """Fetches mailing list and sends AI-generated newsletter to all subscribers."""
    
    # Load mailing list
    try:
        with open(CONFIG["mailing_list_file"], "r") as file:
            mailing_list = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: Mailing list file not found or corrupted.")
        return
    
    if not mailing_list:
        print("No subscribers found in the mailing list.")
        return

    # Generate content and media
    newsletter_content = generate_newsletter_content()
    image_url = generate_media("Marketing image for RLG Data & RLG Fans.")
    
    # Email setup
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(CONFIG["email_sender"], CONFIG["email_password"])

    for subscriber in mailing_list:
        msg = MIMEMultipart()
        msg["From"] = CONFIG["email_sender"]
        msg["To"] = subscriber["email"]
        msg["Subject"] = f"🚀 Weekly Insights from RLG Data & RLG Fans - {time.strftime('%B %d, %Y')}"
        
        email_body = f"""
        <html>
        <body>
            <h2>Hello {subscriber['name']},</h2>
            <p>{newsletter_content}</p>
            <br>
            <p><strong>Featured Image:</strong></p>
            <img src="{image_url}" alt="RLG Data & RLG Fans">
            <br><br>
            <p>Stay ahead with RLG Data & RLG Fans! 🚀</p>
            <p>Best regards,<br><strong>Khoto Zulu</strong><br>Your AI Marketing Agent</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(email_body, "html"))
        
        try:
            server.sendmail(CONFIG["email_sender"], subscriber["email"], msg.as_string())
            print(f"Newsletter sent to {subscriber['email']}")
        except smtplib.SMTPException as e:
            print(f"Error sending email to {subscriber['email']}: {e}")

    server.quit()

# Schedule Weekly Newsletters
schedule.every().monday.at(CONFIG["newsletter_schedule"].split()[1]).do(send_newsletter)

print("RLG Newsletter Agent is running...")

# Run scheduler continuously
while True:
    schedule.run_pending()
    time.sleep(60)

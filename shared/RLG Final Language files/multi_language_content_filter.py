import os
import re
import json
import logging
import requests
import langid
import deep_translator
from googleapiclient.discovery import build
from textblob import TextBlob
from transformers import pipeline
from openai import OpenAI
from deepseek.client import DeepSeekClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("content_filter.log"), logging.StreamHandler()]
)

# API Keys & Services
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GOOGLE_PERSPECTIVE_API_KEY = os.getenv("GOOGLE_PERSPECTIVE_API_KEY")

# AI Clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
deepseek_client = DeepSeekClient(api_key=DEEPSEEK_API_KEY)
sentiment_analyzer = SentimentIntensityAnalyzer()
toxicity_model = pipeline("text-classification", model="unitary/toxic-bert")

# Language Detection & Translation
translator = deep_translator.GoogleTranslator(source="auto", target="en")

# Perspective API for Toxicity Detection
def analyze_toxicity(text):
    """Analyzes content for toxicity using Google's Perspective API."""
    url = f"https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key={GOOGLE_PERSPECTIVE_API_KEY}"
    data = {
        "comment": {"text": text},
        "languages": ["en"],
        "requestedAttributes": {"TOXICITY": {}}
    }
    response = requests.post(url, json=data).json()
    return response.get("attributeScores", {}).get("TOXICITY", {}).get("summaryScore", {}).get("value", 0)

# AI-Powered Content Moderation
def moderate_content(text, language="auto"):
    """Filters inappropriate, spam, or harmful content across multiple languages."""
    if language == "auto":
        language = langid.classify(text)[0]
    
    translated_text = translator.translate(text) if language != "en" else text
    
    # Sentiment Analysis
    sentiment_score = sentiment_analyzer.polarity_scores(translated_text)["compound"]

    # AI-Based Moderation
    gpt_analysis = openai_client.Completion.create(model="gpt-4", prompt=f"Analyze this content: {translated_text}", max_tokens=50)
    deepseek_analysis = deepseek_client.analyze_text(translated_text)

    # Toxicity & Spam Detection
    toxicity_score = analyze_toxicity(translated_text)
    is_toxic = toxicity_score > 0.7 or toxicity_model(translated_text)[0]["label"] == "toxic"

    # Keyword Filtering
    banned_words = ["fake news", "NSFW", "hate speech", "violence", "fraud", "illegal"]
    contains_banned = any(re.search(rf"\b{word}\b", translated_text, re.IGNORECASE) for word in banned_words)

    # Final Decision
    is_harmful = is_toxic or contains_banned or sentiment_score < -0.6

    return {
        "original_text": text,
        "translated_text": translated_text,
        "language": language,
        "sentiment_score": sentiment_score,
        "toxicity_score": toxicity_score,
        "is_toxic": is_toxic,
        "contains_banned_words": contains_banned,
        "is_harmful": is_harmful,
        "ai_analysis": {
            "gpt": gpt_analysis["choices"][0]["text"].strip(),
            "deepseek": deepseek_analysis
        }
    }

# Real-Time Social Media Content Filtering
def filter_social_media_content(platform, content):
    """Filters social media posts from various platforms."""
    result = moderate_content(content)
    
    if result["is_harmful"]:
        logging.warning(f"🚨 [ALERT] Harmful content detected on {platform}: {result}")
        return {"status": "blocked", "details": result}
    
    logging.info(f"✅ [APPROVED] Content passed filtering on {platform}.")
    return {"status": "approved", "details": result}

# Compliance Checker (GDPR, POPIA, CCPA)
def check_compliance(region, text):
    """Ensures content complies with legal regulations in different regions."""
    compliance_rules = {
        "GDPR": ["data protection", "privacy violation"],
        "POPIA": ["South Africa", "data breach"],
        "CCPA": ["California", "user data"],
    }
    
    non_compliant = [law for law, terms in compliance_rules.items() if any(term in text for term in terms)]
    
    return {
        "region": region,
        "is_compliant": not bool(non_compliant),
        "non_compliant_with": non_compliant
    }

# Example Usage
if __name__ == "__main__":
    test_content = "This is a harmful fake news post spreading misinformation."
    result = filter_social_media_content("Twitter", test_content)
    print(json.dumps(result, indent=4))
    
    compliance_check = check_compliance("South Africa", test_content)
    print(json.dumps(compliance_check, indent=4))

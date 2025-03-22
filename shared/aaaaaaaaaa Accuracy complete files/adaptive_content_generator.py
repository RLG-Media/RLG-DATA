import openai
import requests
import json
from datetime import datetime
from textblob import TextBlob
from langdetect import detect
import random
import os

# Load API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# List of supported social media platforms
SOCIAL_MEDIA_PLATFORMS = [
    "Twitter", "Facebook", "Instagram", "LinkedIn", "TikTok",
    "Pinterest", "Reddit", "Snapchat", "Threads", "YouTube"
]

class AdaptiveContentGenerator:
    def __init__(self):
        self.openai_api_key = OPENAI_API_KEY
        self.deepseek_api_key = DEEPSEEK_API_KEY

    def fetch_trending_topics(self, region="global"):
        """
        Fetch trending topics from social media and web sources.
        """
        try:
            response = requests.get(f"https://trends.google.com/trends/api/explore?region={region}")
            if response.status_code == 200:
                return response.json()
            else:
                print("Error fetching trends:", response.text)
                return []
        except Exception as e:
            print(f"Error fetching trending topics: {e}")
            return []

    def analyze_sentiment(self, text):
        """
        Perform sentiment analysis on the given text.
        """
        try:
            sentiment = TextBlob(text).sentiment
            return {"polarity": sentiment.polarity, "subjectivity": sentiment.subjectivity}
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {"polarity": 0, "subjectivity": 0}

    def detect_language(self, text):
        """
        Detect the language of the text.
        """
        try:
            return detect(text)
        except Exception as e:
            print(f"Error detecting language: {e}")
            return "unknown"

    def generate_content(self, topic, tone="informative", platform="Twitter"):
        """
        Generate AI-powered adaptive content for social media.
        """
        try:
            prompt = f"Create a {tone} post about {topic} optimized for {platform}."
            
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": prompt}],
                api_key=self.openai_api_key
            )
            
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Error generating content: {e}")
            return ""

    def personalize_content(self, content, audience="general"):
        """
        Personalize the content based on audience data.
        """
        personalization_options = {
            "general": "Make it friendly and engaging.",
            "tech-savvy": "Include industry-specific jargon.",
            "casual": "Keep it short and fun.",
            "formal": "Use a professional tone."
        }
        tone = personalization_options.get(audience, "Make it engaging.")
        return f"{content} {tone}"

    def schedule_post(self, content, platform):
        """
        Schedule the generated content for posting.
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            post_data = {
                "platform": platform,
                "content": content,
                "scheduled_time": timestamp
            }
            print(f"Scheduled post for {platform}: {content}")
            return post_data
        except Exception as e:
            print(f"Error scheduling post: {e}")
            return {}

    def generate_adaptive_content(self, region="global", platform="Twitter", audience="general"):
        """
        Generate adaptive content based on trending topics and audience preferences.
        """
        trending_topics = self.fetch_trending_topics(region)
        if not trending_topics:
            return "No trending topics available."

        topic = random.choice(trending_topics)
        content = self.generate_content(topic, platform=platform)
        content = self.personalize_content(content, audience)
        
        sentiment = self.analyze_sentiment(content)
        language = self.detect_language(content)
        
        post_data = self.schedule_post(content, platform)

        return {
            "topic": topic,
            "content": content,
            "sentiment": sentiment,
            "language": language,
            "platform": platform,
            "post_data": post_data
        }

if __name__ == "__main__":
    generator = AdaptiveContentGenerator()
    result = generator.generate_adaptive_content(region="South Africa", platform="Instagram", audience="casual")
    print(json.dumps(result, indent=4))

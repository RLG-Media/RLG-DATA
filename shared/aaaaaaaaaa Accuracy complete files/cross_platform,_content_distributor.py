import os
import json
import requests
from datetime import datetime
from social_media_authenticator_services import SocialMediaAuthenticator

# API Keys from Environment Variables
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN")
PINTEREST_ACCESS_TOKEN = os.getenv("PINTEREST_ACCESS_TOKEN")
REDDIT_ACCESS_TOKEN = os.getenv("REDDIT_ACCESS_TOKEN")
SNAPCHAT_ACCESS_TOKEN = os.getenv("SNAPCHAT_ACCESS_TOKEN")
THREADS_ACCESS_TOKEN = os.getenv("THREADS_ACCESS_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Supported Platforms
PLATFORMS = [
    "Twitter", "Facebook", "Instagram", "LinkedIn", "TikTok",
    "Pinterest", "Reddit", "Snapchat", "Threads", "YouTube"
]

class CrossPlatformContentDistributor:
    def __init__(self):
        self.authenticator = SocialMediaAuthenticator()
        self.platforms = PLATFORMS

    def post_content(self, platform, content):
        """
        Posts content to the specified platform.
        """
        platform_handlers = {
            "Twitter": self.post_to_twitter,
            "Facebook": self.post_to_facebook,
            "Instagram": self.post_to_instagram,
            "LinkedIn": self.post_to_linkedin,
            "TikTok": self.post_to_tiktok,
            "Pinterest": self.post_to_pinterest,
            "Reddit": self.post_to_reddit,
            "Snapchat": self.post_to_snapchat,
            "Threads": self.post_to_threads,
            "YouTube": self.post_to_youtube
        }

        handler = platform_handlers.get(platform)
        if handler:
            return handler(content)
        return {"error": f"Platform {platform} not supported."}

    def post_to_twitter(self, content):
        """
        Posts content to Twitter.
        """
        url = "https://api.twitter.com/2/tweets"
        headers = {"Authorization": f"Bearer {TWITTER_API_KEY}"}
        data = {"text": content}

        response = requests.post(url, headers=headers, json=data)
        return response.json()

    def post_to_facebook(self, content):
        """
        Posts content to Facebook.
        """
        url = f"https://graph.facebook.com/me/feed?message={content}&access_token={FACEBOOK_ACCESS_TOKEN}"
        response = requests.post(url)
        return response.json()

    def post_to_instagram(self, content):
        """
        Posts content to Instagram.
        """
        url = f"https://graph.facebook.com/v12.0/me/media?caption={content}&access_token={INSTAGRAM_ACCESS_TOKEN}"
        response = requests.post(url)
        return response.json()

    def post_to_linkedin(self, content):
        """
        Posts content to LinkedIn.
        """
        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {"Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}"}
        data = {"author": "urn:li:person:YOUR_LINKEDIN_ID", "lifecycleState": "PUBLISHED", "specificContent": {"com.linkedin.ugc.ShareContent": {"shareCommentary": {"text": content}, "shareMediaCategory": "NONE"}}, "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}}
        
        response = requests.post(url, headers=headers, json=data)
        return response.json()

    def post_to_tiktok(self, content):
        """
        Posts content to TikTok.
        """
        url = f"https://api.tiktok.com/v1/posts?content={content}&access_token={TIKTOK_ACCESS_TOKEN}"
        response = requests.post(url)
        return response.json()

    def post_to_pinterest(self, content):
        """
        Posts content to Pinterest.
        """
        url = f"https://api.pinterest.com/v5/pins/?description={content}&access_token={PINTEREST_ACCESS_TOKEN}"
        response = requests.post(url)
        return response.json()

    def post_to_reddit(self, content):
        """
        Posts content to Reddit.
        """
        url = f"https://oauth.reddit.com/api/submit"
        headers = {"Authorization": f"Bearer {REDDIT_ACCESS_TOKEN}"}
        data = {"title": "New Post", "text": content, "sr": "your_subreddit", "kind": "self"}

        response = requests.post(url, headers=headers, json=data)
        return response.json()

    def post_to_snapchat(self, content):
        """
        Posts content to Snapchat.
        """
        url = f"https://adsapi.snapchat.com/v1/posts?content={content}&access_token={SNAPCHAT_ACCESS_TOKEN}"
        response = requests.post(url)
        return response.json()

    def post_to_threads(self, content):
        """
        Posts content to Threads.
        """
        url = f"https://api.threads.com/v1/posts?content={content}&access_token={THREADS_ACCESS_TOKEN}"
        response = requests.post(url)
        return response.json()

    def post_to_youtube(self, content):
        """
        Posts content to YouTube Community tab.
        """
        url = "https://www.googleapis.com/youtube/v3/commentThreads"
        headers = {"Authorization": f"Bearer {YOUTUBE_API_KEY}"}
        data = {"snippet": {"topLevelComment": {"snippet": {"textOriginal": content}}}}

        response = requests.post(url, headers=headers, json=data)
        return response.json()

    def distribute_content(self, content, platforms=None):
        """
        Posts content across multiple platforms.
        """
        if platforms is None:
            platforms = self.platforms

        results = []
        for platform in platforms:
            result = self.post_content(platform, content)
            results.append({"platform": platform, "result": result})

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "content": content,
            "distribution_results": results
        }

if __name__ == "__main__":
    distributor = CrossPlatformContentDistributor()
    content_to_post = "🚀 Exciting new updates coming to RLG Data & RLG Fans! Stay tuned. #DataAnalytics #AI"
    distribution_report = distributor.distribute_content(content_to_post)
    print(json.dumps(distribution_report, indent=4))

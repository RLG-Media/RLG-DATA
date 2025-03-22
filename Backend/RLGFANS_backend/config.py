# config.py - Configuration file for RLG Fans

import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

class Config:
    # General Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_default_secret_key')
    FLASK_APP = os.getenv('FLASK_APP', 'app')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/rlg_fans')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '3600'))  # Token expiry in seconds (default 1 hour)

    # Redis configuration (for Celery task queue)
    CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    # Stripe API keys (for payment and subscription management)
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', 'your_stripe_secret_key')
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', 'your_stripe_publishable_key')

    # Mail server configuration (for email notifications)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'your_email@gmail.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'your_email_password')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'your_email@gmail.com')

    # Sentry DSN (for error logging and monitoring)
    SENTRY_DSN = os.getenv('SENTRY_DSN', '')

    # API keys for integrated services and platforms
    ONLYFANS_API_KEY = os.getenv('ONLYFANS_API_KEY', 'your_onlyfans_api_key')
    DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN', 'your_discord_bot_token')
    SNAPCHAT_ACCESS_TOKEN = os.getenv('SNAPCHAT_ACCESS_TOKEN', 'your_snapchat_access_token')
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'your_telegram_bot_token')
    TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID', 'your_twitch_client_id')
    TWITCH_ACCESS_TOKEN = os.getenv('TWITCH_ACCESS_TOKEN', 'your_twitch_access_token')
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', 'your_youtube_api_key')
    TIKTOK_ACCESS_TOKEN = os.getenv('TIKTOK_ACCESS_TOKEN', 'your_tiktok_access_token')
    PINTEREST_ACCESS_TOKEN = os.getenv('PINTEREST_ACCESS_TOKEN', 'your_pinterest_access_token')
    SHOPIFY_ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN', 'your_shopify_access_token')
    TAKEALOT_API_KEY = os.getenv('TAKEALOT_API_KEY', 'your_takealot_api_key')
    MESSENGER_PAGE_ACCESS_TOKEN = os.getenv('MESSENGER_PAGE_ACCESS_TOKEN', 'your_messenger_page_access_token')
    KICK_ACCESS_TOKEN = os.getenv('KICK_ACCESS_TOKEN', 'your_kick_access_token')
    LINKEDIN_ACCESS_TOKEN = os.getenv('LINKEDIN_ACCESS_TOKEN', 'your_linkedin_access_token')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your_openai_api_key')

    # Additional service keys for enhanced functionality
    BRAND_HEALTH_API_KEY = os.getenv('BRAND_HEALTH_API_KEY', 'your_brand_health_api_key')
    CONTENT_PLANNING_API_KEY = os.getenv('CONTENT_PLANNING_API_KEY', 'your_content_planning_api_key')
    CONTENT_SCHEDULING_API_KEY = os.getenv('CONTENT_SCHEDULING_API_KEY', 'your_content_scheduling_api_key')
    CRISIS_MANAGEMENT_API_KEY = os.getenv('CRISIS_MANAGEMENT_API_KEY', 'your_crisis_management_api_key')
    EVENT_MONITORING_API_KEY = os.getenv('EVENT_MONITORING_API_KEY', 'your_event_monitoring_api_key')
    INFLUENCER_MATCHING_API_KEY = os.getenv('INFLUENCER_MATCHING_API_KEY', 'your_influencer_matching_api_key')

    # Platform-specific TOS (Terms of Service) URLs for monitoring and scraping
    TOS_URLS = {
        "onlyfans": os.getenv('ONLYFANS_TOS_URL', 'https://onlyfans.com/terms'),
        "stripchat": os.getenv('STRIPCHAT_TOS_URL', 'https://stripchat.com/terms'),
        # Add remaining platform TOS URLs here as needed
    }

    # Configure additional platform or data-specific parameters
    MAX_CONTENT_FETCH = int(os.getenv('MAX_CONTENT_FETCH', 100))  # Max content items to fetch per request
    TRENDING_ANALYSIS_WINDOW = int(os.getenv('TRENDING_ANALYSIS_WINDOW', 30))  # Analysis window in days

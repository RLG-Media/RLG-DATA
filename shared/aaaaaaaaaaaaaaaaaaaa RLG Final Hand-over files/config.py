import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration settings for RLG Data and RLG Fans."""
    
    # General settings
    APP_NAME = "RLG Super Tool"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    
    # Database configuration
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "rlg_database")
    DB_USER = os.getenv("DB_USER", "rlg_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "securepassword")
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Authentication
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "3600"))  # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", "86400"))  # 1 day
    
    # API Rate Limiting
    RATE_LIMIT = os.getenv("RATE_LIMIT", "100/hour")
    
    # Geolocation & Pricing Configuration
    GEOLOCATION_SERVICE_URL = os.getenv("GEOLOCATION_SERVICE_URL", "https://api.ipgeolocation.io")
    
    # Scraping and Compliance Settings
    SCRAPING_ENABLED = os.getenv("SCRAPING_ENABLED", "True").lower() == "true"
    COMPLIANCE_MONITORING_ENABLED = os.getenv("COMPLIANCE_MONITORING_ENABLED", "True").lower() == "true"
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/rlg_tool.log")
    
    # AI Analysis
    AI_MODEL_PATH = os.getenv("AI_MODEL_PATH", "models/rlg_ai_model.pkl")
    
    # External Services
    PAYMENT_GATEWAY_API = os.getenv("PAYMENT_GATEWAY_API", "https://paymentgateway.com/api")
    EMAIL_SERVICE_API = os.getenv("EMAIL_SERVICE_API", "https://emailservice.com/api")
    
    # Social Integrations
    DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
    WECHAT_API_KEY = os.getenv("WECHAT_API_KEY", "")
    
    # Additional Enhancements & Scalability Features
    CACHING_ENABLED = os.getenv("CACHING_ENABLED", "True").lower() == "true"
    CACHE_TYPE = os.getenv("CACHE_TYPE", "redis")
    CACHE_REDIS_URL = os.getenv("CACHE_REDIS_URL", "redis://localhost:6379/0")
    
    @staticmethod
    def init_app(app):
        """Initialize application with config settings."""
        pass

# Select the appropriate configuration
config = Config

import os

class Config:
    """
    Configuration settings for the RLG Data and RLG Fans application.
    
    Loads configuration from environment variables with sensible defaults.
    This includes settings for:
      - General application environment (development, testing, production)
      - Debug and testing modes
      - Secret key for session management
      - Database connection (SQLAlchemy)
      - External API keys (e.g., SerpAPI, SimilarWeb, Ad Platform APIs)
      - Celery configuration for asynchronous tasks
      - Rate limiting parameters
      - Logging level and regional settings
    """

    # General Settings
    ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
    TESTING = os.getenv("TESTING", "False").lower() in ("true", "1", "yes")
    SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret_key")

    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///rlg_app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # External API Keys and Endpoints
    SERPAPI_KEY = os.getenv("SERPAPI_KEY", "YOUR_SERPAPI_KEY")
    SIMILARWEB_API_KEY = os.getenv("SIMILARWEB_API_KEY", "YOUR_SIMILARWEB_API_KEY")
    # Ad Platform API credentials (if needed)
    AD_API_KEY = os.getenv("AD_API_KEY", "YOUR_AD_API_KEY")
    AD_API_SECRET = os.getenv("AD_API_SECRET", "YOUR_AD_API_SECRET")
    AD_REFRESH_TOKEN = os.getenv("AD_REFRESH_TOKEN", "YOUR_AD_REFRESH_TOKEN")

    # Celery Configuration (for asynchronous tasks)
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = os.getenv("CELERY_TIMEZONE", "UTC")
    ENABLE_CELERY_BEAT = os.getenv("ENABLE_CELERY_BEAT", "False").lower() in ("true", "1", "yes")

    # Rate Limiting Configuration
    RATE_LIMIT_DEFAULT = int(os.getenv("RATE_LIMIT_DEFAULT", "100"))        # Default requests per minute per user/IP
    BURST_LIMIT = int(os.getenv("BURST_LIMIT", "200"))                      # Burst limit for short-term spikes
    GLOBAL_RATE_LIMIT = int(os.getenv("GLOBAL_RATE_LIMIT", "1000"))           # Global limit for all requests
    RATE_LIMIT_RESET_INTERVAL = int(os.getenv("RATE_LIMIT_RESET_INTERVAL", "60"))  # Reset interval in seconds

    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

    # Regional Settings
    DEFAULT_REGION = os.getenv("DEFAULT_REGION", "default")
    SUPPORTED_REGIONS = os.getenv("SUPPORTED_REGIONS", "US,IL,UK,CA,AU").split(",")

    # Additional Configuration Options
    # Add any other configuration parameters relevant to your application here.

if __name__ == "__main__":
    # For testing purposes, print out the configuration settings
    config = Config()
    print("Environment:", config.ENV)
    print("Debug Mode:", config.DEBUG)
    print("Testing Mode:", config.TESTING)
    print("Secret Key:", config.SECRET_KEY)
    print("Database URI:", config.SQLALCHEMY_DATABASE_URI)
    print("SerpAPI Key:", config.SERPAPI_KEY)
    print("SimilarWeb API Key:", config.SIMILARWEB_API_KEY)
    print("Celery Broker URL:", config.CELERY_BROKER_URL)
    print("Global Rate Limit:", config.GLOBAL_RATE_LIMIT)
    print("Supported Regions:", config.SUPPORTED_REGIONS)

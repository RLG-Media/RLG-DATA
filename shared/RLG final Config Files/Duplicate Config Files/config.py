import os
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables from .env file
load_dotenv()

class Config:
    # Flask Application Config
    FLASK_APP = os.getenv("FLASK_APP", "app")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

    # Database Config
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Config
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "superjwtsecretkey")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    # Redis Config (for Celery and Caching)
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL

    # Stripe Config
    STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")

    # Mail Server Config
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() in ["true", "1"]
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME)

    # Sentry Config for Error Monitoring
    SENTRY_DSN = os.getenv("SENTRY_DSN")

    # API Keys for Integrated Services
    ONLYFANS_API_KEY = os.getenv("ONLYFANS_API_KEY")
    STRIPCHAT_API_KEY = os.getenv("STRIPCHAT_API_KEY")
    FANFIX_API_KEY = os.getenv("FANFIX_API_KEY")
    FANSLY_API_KEY = os.getenv("FANSLY_API_KEY")
    FANCENTRO_API_KEY = os.getenv("FANCENTRO_API_KEY")
    MYM_API_KEY = os.getenv("MYM_API_KEY")
    FANVUE_API_KEY = os.getenv("FANVUE_API_KEY")
    IFANS_API_KEY = os.getenv("IFANS_API_KEY")
    FANSO_API_KEY = os.getenv("FANSO_API_KEY")
    FANTIME_API_KEY = os.getenv("FANTIME_API_KEY")
    PATREON_API_KEY = os.getenv("PATREON_API_KEY")
    UNLOCKED_API_KEY = os.getenv("UNLOCKED_API_KEY")
    ADULTNODE_API_KEY = os.getenv("ADULTNODE_API_KEY")
    UNFILTRD_API_KEY = os.getenv("UNFILTRD_API_KEY")
    FLIRTBACK_API_KEY = os.getenv("FLIRTBACK_API_KEY")
    ADMIREME_API_KEY = os.getenv("ADMIREME_API_KEY")
    JUSTFORFANS_API_KEY = os.getenv("JUSTFORFANS_API_KEY")
    MANYVIDS_API_KEY = os.getenv("MANYVIDS_API_KEY")
    SCRILECONNECT_API_KEY = os.getenv("SCRILECONNECT_API_KEY")
    OKFANS_API_KEY = os.getenv("OKFANS_API_KEY")
    FAPELLO_API_KEY = os.getenv("FAPELLO_API_KEY")
    FANSMETRICS_API_KEY = os.getenv("FANSMETRICS_API_KEY")
    SIMPCITY_API_KEY = os.getenv("SIMPCITY_API_KEY")
    AVNSTARS_API_KEY = os.getenv("AVNSTARS_API_KEY")
    SHEER_API_KEY = os.getenv("SHEER_API_KEY")               # New: Sheer service
    PORNHUB_API_KEY = os.getenv("PORNHUB_API_KEY")           # New: Pornhub service

    # Google and Other Social Media API Configurations
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
    TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
    TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
    TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
    LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN")
    PINTEREST_ACCESS_TOKEN = os.getenv("PINTEREST_ACCESS_TOKEN")

    # Additional Configurations (for tools like Flower for Celery Monitoring)
    FLOWER_BASIC_AUTH = os.getenv("FLOWER_BASIC_AUTH", "user:password")

    # Logger Configurations
    LOG_FILE = os.getenv("LOG_FILE", "app.log")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


# Optional subclass for Production Environment
class ProductionConfig(Config):
    FLASK_ENV = "production"
    DEBUG = False


# Optional subclass for Development Environment
class DevelopmentConfig(Config):
    DEBUG = True


# Optional subclass for Testing Environment
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # In-memory database for testing
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing

LOGGING_LEVEL = 'DEBUG'  # Change to INFO or WARNING for production
LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
CENTRALIZED_LOGGING_SERVER = 'http://your-logging-server.com/api/logs'  # Replace with your actual logging server URL
LOG_FILE_PATH = '/var/log/rlg_data_fans.log'  # Replace with the desired path for the log file

ANONYMIZATION_KEY = 'your-fernet-key'  # Use environment variables for better security
DATA_FIELDS_TO_ANONYMIZE = ['email', 'phone_number', 'name', 'address']  # Add more fields as needed
HASH_SALT = 'your-salt-value'  # Use a unique salt for each project

DATABASE_CONFIG = {
    'DB_TYPE': 'mysql',  # or 'postgresql'
    'DB_USER': 'your_db_user',
    'DB_PASSWORD': 'your_db_password',
    'DB_NAME': 'your_db_name',
    'DB_HOST': 'localhost',  # For PostgreSQL, use the appropriate host
}

BACKUP_DIRECTORY = '/path/to/backup/directory'
NOTIFICATION_EMAILS = 'admin@yourdomain.com'
BACKUP_RETENTION_PERIOD = 30  # Retain backups for 30 days

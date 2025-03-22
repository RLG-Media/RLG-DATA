"""
config.py
Centralized configuration file for RLG Data and RLG Fans.
Handles environment-specific settings, secrets, and application configuration.
"""

import os
from dotenv import load_dotenv
from pathlib import Path
from logging.config import dictConfig

# Load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

class Config:
    """
    Base configuration with common settings for all environments.
    """
    # General Application Settings
    APP_NAME = os.getenv("APP_NAME", "RLG Platform")
    ENV = os.getenv("ENV", "development")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")  # Replace with a strong secret in production
    TIMEZONE = os.getenv("TIMEZONE", "UTC")
    
    # Database Configuration
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 5432))
    DB_NAME = os.getenv("DB_NAME", "rlg_data")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Celery Configuration
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    CELERY_WORKER_CONCURRENCY = int(os.getenv("CELERY_WORKER_CONCURRENCY", 4))
    CELERY_TASK_RATE_LIMIT = os.getenv("CELERY_TASK_RATE_LIMIT", "10/s")
    CELERY_RESULT_EXPIRES = int(os.getenv("CELERY_RESULT_EXPIRES", 3600))  # 1 hour

    # Redis Configuration
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    LOG_DIR = BASE_DIR / "logs"
    LOG_FILE = LOG_DIR / "application.log"

    # API Rate Limits (using Flask-Limiter)
    RATE_LIMIT = os.getenv("RATE_LIMIT", "1000 per hour")

    # Security Settings
    ENABLE_CSRF = os.getenv("ENABLE_CSRF", "true").lower() == "true"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"

    # Monitoring and Metrics
    ENABLE_METRICS = os.getenv("ENABLE_METRICS", "false").lower() == "true"
    METRICS_PORT = int(os.getenv("METRICS_PORT", 9100))

    # Feature Flags
    ENABLE_AI_ANALYTICS = os.getenv("ENABLE_AI_ANALYTICS", "false").lower() == "true"
    ENABLE_SOCIAL_MEDIA_SCRAPING = os.getenv("ENABLE_SOCIAL_MEDIA_SCRAPING", "false").lower() == "true"

    # Third-Party Integrations
    SENTRY_DSN = os.getenv("SENTRY_DSN", None)
    GOOGLE_ANALYTICS_ID = os.getenv("GOOGLE_ANALYTICS_ID", None)

    # Email Configuration
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", None)
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", None)
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "noreply@example.com")

    # Backup Configuration
    BACKUP_STORAGE_DIR = BASE_DIR / "backups"
    BACKUP_RETENTION_DAYS = int(os.getenv("BACKUP_RETENTION_DAYS", 7))

    # File Uploads
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))  # 16 MB
    UPLOAD_FOLDER = BASE_DIR / "uploads"

    # Encryption Keys
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "default_encryption_key")  # Replace in production

class DevelopmentConfig(Config):
    """
    Development-specific configuration.
    """
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Enables SQL query logging
    CELERY_TASK_RATE_LIMIT = "20/s"

class ProductionConfig(Config):
    """
    Production-specific configuration.
    """
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    ENABLE_CSRF = True
    LOG_LEVEL = "WARNING"

class TestingConfig(Config):
    """
    Testing-specific configuration.
    """
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # In-memory database for tests

# Environment selection
config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}

ActiveConfig = config_map.get(os.getenv("ENV", "development").lower(), DevelopmentConfig)

# Logging Configuration
LOG_DIR.mkdir(exist_ok=True)  # Ensure log directory exists
dictConfig({
    "version": 1,
    "formatters": {
        "default": {
            "format": Config.LOG_FORMAT,
        },
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": Config.LOG_FILE,
            "formatter": "default",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "level": Config.LOG_LEVEL,
        "handlers": ["file", "console"],
    },
})

# Ensure all critical directories exist
for path in [Config.LOG_DIR, Config.UPLOAD_FOLDER, Config.BACKUP_STORAGE_DIR]:
    path.mkdir(exist_ok=True)

# Print current active environment
print(f"Active Configuration: {os.getenv('ENV', 'development')}")


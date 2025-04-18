import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Application Settings
APP_NAME = os.getenv("APP_NAME", "RLG Data")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1")
TESTING = os.getenv("TESTING", "False").lower() in ("true", "1")
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")  # Replace for production

# Database Configuration
DB_TYPE = os.getenv("DB_TYPE", "sqlite")
if DB_TYPE == "sqlite":
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///app.db")
else:
    SQLALCHEMY_DATABASE_URI = f"{DB_TYPE}://{os.getenv('DB_USER', 'user')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'database')}"
SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", "False").lower() in ("true", "1")

# Security Settings
CSRF_ENABLED = os.getenv("CSRF_ENABLED", "True").lower() in ("true", "1")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key")  # Replace for production
JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 3600))  # 1 hour
JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 86400))  # 1 day

# Email Configuration
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() in ("true", "1")
MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False").lower() in ("true", "1")
MAIL_USERNAME = os.getenv("MAIL_USERNAME", None)
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", None)
MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", f"no-reply@{APP_NAME.lower().replace(' ', '')}.com")

# Celery Configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
CELERY_TASK_SERIALIZER = os.getenv("CELERY_TASK_SERIALIZER", "json")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")

# API Rate Limiting
RATELIMIT_ENABLED = os.getenv("RATELIMIT_ENABLED", "True").lower() in ("true", "1")
RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "200/day;50/hour")

# File Upload Settings
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))  # 16MB

# External API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")

# Feature Flags
ENABLE_ANALYTICS = os.getenv("ENABLE_ANALYTICS", "True").lower() in ("true", "1")
ENABLE_REALTIME_UPDATES = os.getenv("ENABLE_REALTIME_UPDATES", "True").lower() in ("true", "1")

# Environment-specific overrides
ENV = os.getenv("ENV", "development").lower()
if ENV == "production":
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY")  # Ensure this is set in production
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # Ensure this is set in production

elif ENV == "staging":
    DEBUG = True
    TESTING = False

elif ENV == "development":
    DEBUG = True
    TESTING = True

# Print a warning if critical environment variables are missing
missing_vars = [var for var in ["SECRET_KEY", "SQLALCHEMY_DATABASE_URI", "JWT_SECRET_KEY"] if not os.getenv(var)]
if missing_vars:
    print(f"Warning: Missing critical environment variables: {', '.join(missing_vars)}")


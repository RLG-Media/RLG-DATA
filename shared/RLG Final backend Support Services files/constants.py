# Constants for RLG Data and RLG Fans

# General Application Constants
APP_NAME = "RLG Data & RLG Fans"
VERSION = "1.0.0"
DEFAULT_TIMEZONE = "UTC"

# User Role Constants
ROLES = {
    "ADMIN": "Admin",
    "USER": "User",
    "CREATOR": "Creator",
    "PRO": "Pro",
    "ENTERPRISE": "Enterprise"
}

# Pricing Constants
PRICING_TIERS = {
    "DEFAULT": {
        "Creator": {"weekly": 15, "monthly": 59},
        "Pro": {"weekly": 35, "monthly": 99},
        "Enterprise": {"weekly": None, "monthly": 499},
        "MediaPack": {"weekly": None, "monthly": 2000}
    },
    "ISRAEL": {
        "Creator": {"weekly": 35, "monthly": 99},
        "Pro": {"weekly": 65, "monthly": 199},
        "Enterprise": {"weekly": None, "monthly": 699},
        "MediaPack": {"weekly": None, "monthly": 2500}
    }
}

# Geolocation Constants
SPECIAL_REGION_COUNTRY_CODE = "IL"  # Israel
GEOLOCATION_API_URL = "https://ipapi.co/json/"
GEOLOCATION_TIMEOUT = 5  # seconds

# Payment Gateway Constants
STRIPE = {
    "API_KEY": "your_stripe_api_key",
    "CURRENCY": "usd"
}

PAYFAST = {
    "MERCHANT_ID": "your_payfast_merchant_id",
    "MERCHANT_KEY": "your_payfast_merchant_key",
    "PASSPHRASE": "your_payfast_passphrase",  # Optional
    "BASE_URL": "https://sandbox.payfast.co.za/eng/process"
}

# Caching Constants
CACHE = {
    "HOST": "localhost",
    "PORT": 6379,
    "DB": 0,
    "PASSWORD": None,
    "DEFAULT_TTL": 3600  # seconds
}

# Logging Constants
LOGGING = {
    "LEVEL": "INFO",
    "FORMAT": "%(asctime)s - %(levelname)s - %(message)s",
    "HANDLERS": ["stream", "file"],
    "FILE_NAME": "application.log"
}

# API Rate Limits (per user per minute)
RATE_LIMITS = {
    "DEFAULT": 100,
    "PREMIUM": 500,
    "ENTERPRISE": 1000
}

# Notifications
NOTIFICATION_SETTINGS = {
    "EMAIL": True,
    "SMS": False,
    "PUSH": True,
    "DEFAULT_FREQUENCY": "daily"
}

# Analytics Constants
ANALYTICS = {
    "DEFAULT_RETENTION_PERIOD": 365,  # days
    "AGGREGATION_INTERVAL": "monthly"
}

# Security Constants
SECURITY = {
    "PASSWORD_MIN_LENGTH": 8,
    "PASSWORD_COMPLEXITY": {
        "UPPERCASE": 1,
        "LOWERCASE": 1,
        "DIGITS": 1,
        "SPECIAL": 1
    },
    "TOKEN_EXPIRY": 3600,  # seconds
    "JWT_SECRET_KEY": "your_jwt_secret_key",
    "JWT_ALGORITHM": "HS256"
}

# File Storage Constants
FILE_STORAGE = {
    "MAX_UPLOAD_SIZE": 10485760,  # 10 MB
    "ALLOWED_FILE_TYPES": ["pdf", "docx", "xlsx", "csv", "png", "jpg"],
    "STORAGE_PATH": "/var/rlg/uploads"
}

# Email Settings
EMAIL = {
    "SMTP_SERVER": "smtp.example.com",
    "SMTP_PORT": 587,
    "USERNAME": "your_email@example.com",
    "PASSWORD": "your_email_password",
    "USE_TLS": True
}

# Recommendations
RECOMMENDATIONS = {
    "ENABLE": True,
    "MODEL": "collaborative_filtering",
    "UPDATE_INTERVAL": "daily"
}

# Developer Notes
# - Update sensitive keys (e.g., API keys, passwords) with environment variables in production.
# - Consider using a configuration management tool (e.g., dotenv, AWS Secrets Manager).
# - Regularly review and update constants for compliance and scalability.

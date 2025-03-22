import os
from cryptography.fernet import Fernet

# Secret Key Generation (Generate and save securely in production environment)
# Ensure this key is kept confidential and stored securely.
SECRET_KEY = os.getenv('SECRET_KEY', Fernet.generate_key().decode())

# Encrypt/Decrypt Function
def encrypt(data):
    fernet = Fernet(SECRET_KEY)
    encrypted_data = fernet.encrypt(data.encode())
    return encrypted_data

def decrypt(encrypted_data):
    fernet = Fernet(SECRET_KEY)
    decrypted_data = fernet.decrypt(encrypted_data).decode()
    return decrypted_data

# Environment Variables
# Store environment-sensitive secrets like database credentials, API keys, and other confidential data
# Use secure storage or environment-specific secrets management solutions for deployment

# Example: Database connection secrets
DB_USERNAME = os.getenv('DB_USERNAME', 'default_username')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'default_password')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'rlg_data')

# AWS Secrets Management (Example for AWS cloud-based secrets management)
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', 'your_aws_access_key')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', 'your_aws_secret_key')
AWS_REGION = os.getenv('AWS_REGION', 'your_aws_region')

# Redis Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', 'default_redis_password')

# Third-Party API Secrets (Example: social media APIs, cloud APIs, etc.)
FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID', 'your_facebook_app_id')
FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET', 'your_facebook_app_secret')

TWITTER_API_KEY = os.getenv('TWITTER_API_KEY', 'your_twitter_api_key')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET', 'your_twitter_api_secret')

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'your_google_api_key')

# Other API keys and access tokens
INSTAGRAM_ACCESS_TOKEN = os.getenv('INSTAGRAM_ACCESS_TOKEN', 'your_instagram_access_token')
SLACK_API_TOKEN = os.getenv('SLACK_API_TOKEN', 'your_slack_api_token')

# Security Configuration
# Define cryptographic and security-related constants

# Minimum Password Length for Security
MIN_PASSWORD_LENGTH = int(os.getenv('MIN_PASSWORD_LENGTH', '12'))

# Token Secret Keys for JWT (JSON Web Token) or other cryptographic tokens
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key')
JWT_ACCESS_TOKEN_EXPIRY = os.getenv('JWT_ACCESS_TOKEN_EXPIRY', '3600')  # 1 hour
JWT_REFRESH_TOKEN_EXPIRY = os.getenv('JWT_REFRESH_TOKEN_EXPIRY', '86400')  # 24 hours

# Application Secrets
APP_SECRET = os.getenv('APP_SECRET', 'your_application_secret')

# Encryption Key for sensitive data (Example: for encrypting sensitive data)
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', Fernet.generate_key().decode())

# Token Salt for secure hashing (used in password hashing)
TOKEN_SALT = os.getenv('TOKEN_SALT', os.urandom(16).hex())

# External API Integrations
# Secure API key storage and management for integrations with external services

# Example: API keys for payment gateways
PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID', 'your_paypal_client_id')
PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET', 'your_paypal_client_secret')

STRIPE_API_KEY = os.getenv('STRIPE_API_KEY', 'your_stripe_api_key')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', 'your_stripe_secret_key')

# Miscellaneous Secrets
# Store any other sensitive information here

# Sentry DSN for error tracking and monitoring
SENTRY_DSN = os.getenv('SENTRY_DSN', 'your_sentry_dsn')

# Cloud Storage Secrets (Example for AWS S3 or Google Cloud Storage)
AWS_S3_ACCESS_KEY = os.getenv('AWS_S3_ACCESS_KEY', 'your_aws_s3_access_key')
AWS_S3_SECRET_ACCESS_KEY = os.getenv('AWS_S3_SECRET_ACCESS_KEY', 'your_aws_s3_secret_key')

# Encryption Key for AWS S3 Encryption
S3_ENCRYPTION_KEY = os.getenv('S3_ENCRYPTION_KEY', Fernet.generate_key().decode())

# API Gateway Secrets
API_GATEWAY_KEY = os.getenv('API_GATEWAY_KEY', 'your_api_gateway_key')

# Secure Storage Example: Using AWS Secrets Manager
# Ensure that you have configured AWS Secrets Manager to store and manage your secrets securely.
# Environment-sensitive information must be securely stored and accessed through AWS Secrets Manager, 
# HashiCorp Vault, or another secure secrets management solution in production.

# Load Secrets Dynamically in Development and Production
def load_secrets(env='development'):
    if env == 'production':
        # Load production-specific secrets securely from a secrets manager.
        pass  # This would call AWS Secrets Manager, Vault, etc.
    else:
        # Load development secrets directly from environment variables
        secrets = {
            "DB_USERNAME": DB_USERNAME,
            "DB_PASSWORD": DB_PASSWORD,
            "DB_HOST": DB_HOST,
            "DB_PORT": DB_PORT,
            "DB_NAME": DB_NAME,
            "AWS_ACCESS_KEY_ID": AWS_ACCESS_KEY_ID,
            "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY,
            "AWS_REGION": AWS_REGION,
            "REDIS_HOST": REDIS_HOST,
            "REDIS_PORT": REDIS_PORT,
            "REDIS_PASSWORD": REDIS_PASSWORD,
            "FACEBOOK_APP_ID": FACEBOOK_APP_ID,
            "FACEBOOK_APP_SECRET": FACEBOOK_APP_SECRET,
            "TWITTER_API_KEY": TWITTER_API_KEY,
            "TWITTER_API_SECRET": TWITTER_API_SECRET,
            "GOOGLE_API_KEY": GOOGLE_API_KEY,
            "INSTAGRAM_ACCESS_TOKEN": INSTAGRAM_ACCESS_TOKEN,
            "SLACK_API_TOKEN": SLACK_API_TOKEN,
            "MIN_PASSWORD_LENGTH": MIN_PASSWORD_LENGTH,
            "JWT_SECRET_KEY": JWT_SECRET_KEY,
            "JWT_ACCESS_TOKEN_EXPIRY": JWT_ACCESS_TOKEN_EXPIRY,
            "JWT_REFRESH_TOKEN_EXPIRY": JWT_REFRESH_TOKEN_EXPIRY,
            "APP_SECRET": APP_SECRET,
            "ENCRYPTION_KEY": ENCRYPTION_KEY,
            "TOKEN_SALT": TOKEN_SALT,
            "PAYPAL_CLIENT_ID": PAYPAL_CLIENT_ID,
            "PAYPAL_CLIENT_SECRET": PAYPAL_CLIENT_SECRET,
            "STRIPE_API_KEY": STRIPE_API_KEY,
            "STRIPE_SECRET_KEY": STRIPE_SECRET_KEY,
            "SENTRY_DSN": SENTRY_DSN,
            "AWS_S3_ACCESS_KEY": AWS_S3_ACCESS_KEY,
            "AWS_S3_SECRET_ACCESS_KEY": AWS_S3_SECRET_ACCESS_KEY,
            "S3_ENCRYPTION_KEY": S3_ENCRYPTION_KEY,
            "API_GATEWAY_KEY": API_GATEWAY_KEY,
        }
        return secrets

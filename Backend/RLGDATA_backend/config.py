import os

from django import db

class Config:
    """
    Base configuration class.
    Sets default values for all configurations.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a_random_secret_key')  # Use environment variable or default
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///site.db')  # Default to SQLite
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable modification tracking
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True  # Sign cookies
    SESSION_TYPE = 'filesystem'  # Store sessions in the filesystem
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')  # Mail server
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))  # Default port for TLS
    MAIL_USE_TLS = True  # Use TLS
    MAIL_USE_SSL = False  # Don't use SSL
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # Email for sending
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # Email password
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'no-reply@yourdomain.com')  # Default sender email
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')  # Environment setting
    DEBUG = FLASK_ENV == 'development'  # Debug mode for development

    # Rate Limiter settings
    RATELIMIT_DEFAULT = "200 per day;50 per hour"  # Default rate limit settings

    # Sentry DSN for error tracking
    SENTRY_DSN = os.environ.get('SENTRY_DSN')  # Error tracking DSN, optional


class ProductionConfig(Config):
    """
    Production-specific configuration.
    """
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')  # Override with production DB


class DevelopmentConfig(Config):
    """
    Development-specific configuration.
    """
    DEBUG = True


class TestingConfig(Config):
    """
    Testing-specific configuration.
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory database for testing

import os

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://user:jobe2nd@localhost/rlg_data')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Other configurations like mail, secret keys, etc.
    ...
from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions like SQLAlchemy, JWT, etc.
    db.init_app(app)
    ...
    
    return app

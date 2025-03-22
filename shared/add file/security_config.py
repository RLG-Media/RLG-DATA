# security_config.py - Configuration for Security in RLG Data and RLG Fans

import os
from datetime import timedelta

class SecurityConfig:
    """
    Configuration class for handling security settings and best practices.
    This includes authentication, encryption, session management, and other security measures.
    """

    def __init__(self):
        # Secret key used for signing sessions and tokens
        self.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key')

        # Session expiration settings
        self.session_expiration = timedelta(days=1)  # Default session expiration: 1 day

        # CSRF (Cross-Site Request Forgery) settings
        self.csrf_enabled = True  # Enable or disable CSRF protection
        self.csrf_token_lifetime = timedelta(hours=1)  # CSRF token lifetime: 1 hour

        # Encryption settings for sensitive data
        self.encryption_key = os.environ.get('ENCRYPTION_KEY', 'your-encryption-key')
        self.encryption_algorithm = 'AES256'  # Algorithm used for data encryption

        # JWT (JSON Web Token) settings
        self.jwt_secret = os.environ.get('JWT_SECRET', 'your-jwt-secret')
        self.jwt_algorithm = 'HS256'  # JWT Algorithm used for signing tokens
        self.jwt_expiration = timedelta(hours=8)  # JWT token expiration: 8 hours

        # Password hashing settings using bcrypt
        self.password_salt_rounds = 12  # Number of salt rounds for bcrypt

        # Rate limiting configuration
        self.rate_limit_enabled = True  # Enable or disable rate limiting
        self.rate_limit_max_requests = 100  # Maximum allowed requests per IP
        self.rate_limit_time_window = timedelta(minutes=15)  # Time window for rate limiting

        # Two-Factor Authentication (2FA) settings
        self.two_factor_auth_enabled = True  # Enable or disable 2FA
        self.two_factor_auth_token_expiration = timedelta(minutes=10)  # Token expiration for 2FA

        # Whitelisted IPs that can bypass security checks (if any)
        self.whitelisted_ips = ['127.0.0.1', '::1']  # Example IPs for whitelisting

        # Secure cookies settings
        self.secure_cookies = {
            'httponly': True,    # HTTPOnly cookies prevent client-side access
            'secure': True,      # Secure cookies prevent being sent over unencrypted connections
            'samesite': 'Lax'    # Lax or Strict to control cross-site cookies
        }

        # Content Security Policy (CSP) settings
        self.content_security_policy = {
            'default_src': ["'self'"],
            'script_src': ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
            'style_src': ["'self'", "'unsafe-inline'"],
            'img_src': ["'self'", 'data:'],
            'object_src': ["'none'"],
            'frame_src': ["'none'"],
            'connect_src': ["'self'"]
        }

        # Password recovery settings
        self.password_reset_token_expiration = timedelta(hours=24)  # Token expiration for password reset

        # Application lockout settings after too many failed login attempts
        self.lockout_enabled = True  # Enable or disable account lockout after too many attempts
        self.lockout_threshold = 5  # Number of failed login attempts before lockout
        self.lockout_duration = timedelta(minutes=30)  # Duration of lockout

        # Account inactivity settings
        self.inactivity_timeout = timedelta(days=90)  # Inactivity timeout: 90 days

        # Security logging configuration
        self.security_log_file_path = os.path.join(os.path.dirname(__file__), 'security_logs')
        self.security_log_level = 'WARNING'  # Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL

    def get_security_config(self):
        """
        Return a comprehensive dictionary containing all security configurations.
        
        Returns:
            Dictionary with all configurations.
        """
        return {
            "secret_key": self.secret_key,
            "session_expiration": self.session_expiration,
            "csrf_enabled": self.csrf_enabled,
            "csrf_token_lifetime": self.csrf_token_lifetime,
            "encryption_key": self.encryption_key,
            "encryption_algorithm": self.encryption_algorithm,
            "jwt_secret": self.jwt_secret,
            "jwt_algorithm": self.jwt_algorithm,
            "jwt_expiration": self.jwt_expiration,
            "password_salt_rounds": self.password_salt_rounds,
            "rate_limit_enabled": self.rate_limit_enabled,
            "rate_limit_max_requests": self.rate_limit_max_requests,
            "rate_limit_time_window": self.rate_limit_time_window,
            "two_factor_auth_enabled": self.two_factor_auth_enabled,
            "two_factor_auth_token_expiration": self.two_factor_auth_token_expiration,
            "whitelisted_ips": self.whitelisted_ips,
            "secure_cookies": self.secure_cookies,
            "content_security_policy": self.content_security_policy,
            "password_reset_token_expiration": self.password_reset_token_expiration,
            "lockout_enabled": self.lockout_enabled,
            "lockout_threshold": self.lockout_threshold,
            "lockout_duration": self.lockout_duration,
            "inactivity_timeout": self.inactivity_timeout,
            "security_log_file_path": self.security_log_file_path,
            "security_log_level": self.security_log_level
        }

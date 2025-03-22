import logging
import logging.config
from sentry_sdk.integrations.logging import LoggingIntegration
import sentry_sdk
import os

# Sentry DSN for error reporting
SENTRY_DSN = os.getenv('SENTRY_DSN', None)

def setup_logging():
    """
    Configure logging for the entire application.
    Supports console, file logging, and Sentry integration for error monitoring.
    """

    # Setup Sentry integration if SENTRY_DSN is provided
    if SENTRY_DSN:
        sentry_logging = LoggingIntegration(
            level=logging.INFO,          # Capture info and above as breadcrumbs
            event_level=logging.ERROR    # Send errors and above to Sentry as events
        )
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[sentry_logging]
        )

    # Define logging configuration
    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
            'detailed': {
                'format': '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s'
            },
            'json': {  # Optional JSON formatter for structured logging
                'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'level': 'DEBUG'
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': 'logs/rlg_app.log',
                'formatter': 'detailed',
                'level': 'INFO'
            },
            'error_file': {
                'class': 'logging.FileHandler',
                'filename': 'logs/rlg_app_errors.log',
                'formatter': 'detailed',
                'level': 'ERROR'
            },
            'critical_file': {  # For capturing critical logs separately
                'class': 'logging.FileHandler',
                'filename': 'logs/rlg_app_critical.log',
                'formatter': 'detailed',
                'level': 'CRITICAL'
            }
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['console', 'file', 'error_file', 'critical_file'],
                'level': 'INFO',
                'propagate': True
            },
            'rlg_data': {
                'handlers': ['console', 'file', 'error_file'],
                'level': 'INFO',
                'propagate': False
            },
            'rlg_fans': {
                'handlers': ['console', 'file', 'error_file'],
                'level': 'INFO',
                'propagate': False
            },
            'external_services': {  # New logger for external services integrations
                'handlers': ['console', 'file', 'error_file'],
                'level': 'INFO',
                'propagate': False
            },
            'auth': {  # New logger for authentication and security
                'handlers': ['console', 'file', 'error_file'],
                'level': 'INFO',
                'propagate': False
            }
        }
    }

    # Apply logging configuration
    logging.config.dictConfig(LOGGING_CONFIG)

    # Confirm logging setup
    logging.info("Logging configuration successfully loaded.")
    logging.info("Logging active for RLG Data and RLG Fans modules.")
    logging.info("Sentry integration enabled: %s", bool(SENTRY_DSN))

# Initialize logging when this module is imported
setup_logging()

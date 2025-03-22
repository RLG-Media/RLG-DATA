"""
logging_config.py
Centralized logging configuration for RLG Data and RLG Fans.
Provides customizable logging levels, handlers, formatters, and external integration.
"""

import os
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler, SMTPHandler
from typing import Optional

# Constants
LOG_DIR = "logs"
DEFAULT_LOG_FILE = os.path.join(LOG_DIR, "application.log")
DEFAULT_ERROR_LOG_FILE = os.path.join(LOG_DIR, "error.log")
MAX_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5
EMAIL_LOGGING_ENABLED = True
EMAIL_LOGGING_CONFIG = {
    "mailhost": ("smtp.example.com", 587),
    "fromaddr": "alerts@rlgplatform.com",
    "toaddrs": ["admin@rlgplatform.com"],
    "subject": "RLG Platform Error Alert",
    "credentials": ("alerts@rlgplatform.com", "securepassword"),
    "secure": (),
}
SUPPORTED_LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

# Ensure the logs directory exists
os.makedirs(LOG_DIR, exist_ok=True)

def configure_logging(log_level: str = "INFO", enable_console: bool = True) -> None:
    """
    Configures logging for the application.

    Args:
        log_level (str): The minimum logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        enable_console (bool): Whether to log to the console in addition to files.
    """
    if log_level not in SUPPORTED_LOG_LEVELS:
        raise ValueError(f"Invalid log level: {log_level}. Choose from {list(SUPPORTED_LOG_LEVELS.keys())}.")
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(SUPPORTED_LOG_LEVELS[log_level])
    root_logger.handlers = []  # Clear existing handlers

    # Formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handler (Rotating)
    rotating_handler = RotatingFileHandler(
        DEFAULT_LOG_FILE,
        maxBytes=MAX_LOG_FILE_SIZE,
        backupCount=BACKUP_COUNT
    )
    rotating_handler.setLevel(SUPPORTED_LOG_LEVELS[log_level])
    rotating_handler.setFormatter(formatter)
    root_logger.addHandler(rotating_handler)

    # File handler for errors (Timed Rotating)
    error_handler = TimedRotatingFileHandler(
        DEFAULT_ERROR_LOG_FILE,
        when="midnight",
        interval=1,
        backupCount=BACKUP_COUNT
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

    # Console handler (optional)
    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(SUPPORTED_LOG_LEVELS[log_level])
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # Email handler (for critical errors)
    if EMAIL_LOGGING_ENABLED:
        try:
            smtp_handler = SMTPHandler(
                mailhost=EMAIL_LOGGING_CONFIG["mailhost"],
                fromaddr=EMAIL_LOGGING_CONFIG["fromaddr"],
                toaddrs=EMAIL_LOGGING_CONFIG["toaddrs"],
                subject=EMAIL_LOGGING_CONFIG["subject"],
                credentials=EMAIL_LOGGING_CONFIG["credentials"],
                secure=EMAIL_LOGGING_CONFIG.get("secure")
            )
            smtp_handler.setLevel(logging.CRITICAL)
            smtp_handler.setFormatter(formatter)
            root_logger.addHandler(smtp_handler)
        except Exception as e:
            logging.warning(f"Failed to configure email logging: {e}")

    logging.info("Logging configuration successfully initialized.")

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Retrieves a logger instance with the specified name.

    Args:
        name (Optional[str]): Name of the logger. Defaults to the root logger.

    Returns:
        logging.Logger: Configured logger instance.
    """
    return logging.getLogger(name)

# Example usage
if __name__ == "__main__":
    # Initialize logging configuration
    configure_logging(log_level="DEBUG", enable_console=True)

    # Example log messages
    logger = get_logger("RLG Platform")
    logger.debug("This is a debug message.")
    logger.info("System started successfully.")
    logger.warning("This is a warning.")
    logger.error("An error occurred while processing.")
    logger.critical("Critical issue detected!")

import logging
import logging.handlers
import os
from datetime import datetime

# Define log levels
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()  # Default to INFO if not set

# Directory for log files
LOG_DIR = os.getenv("LOG_DIR", "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Log file name with timestamp
LOG_FILE = os.path.join(LOG_DIR, f"application_{datetime.now().strftime('%Y-%m-%d')}.log")

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Max log file size (in bytes) and backup count
MAX_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5  # Keep last 5 log files

def setup_logging():
    """
    Configures the application's logging system.
    """
    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)

    # Formatter
    formatter = logging.Formatter(LOG_FORMAT)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Rotating file handler
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=MAX_LOG_FILE_SIZE, backupCount=BACKUP_COUNT
    )
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Optional: Add an email handler for critical errors
    if os.getenv("ENABLE_EMAIL_LOGGING", "False").lower() == "true":
        email_handler = logging.handlers.SMTPHandler(
            mailhost=(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT", 587))),
            fromaddr=os.getenv("SMTP_FROM"),
            toaddrs=os.getenv("LOG_RECIPIENTS").split(","),
            subject="Critical Error in RLG Application",
            credentials=(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD")),
            secure=()
        )
        email_handler.setLevel(logging.CRITICAL)
        email_handler.setFormatter(formatter)
        logger.addHandler(email_handler)

    # Example message to confirm logging setup
    logger.info("Logging system initialized successfully.")

def get_logger(module_name):
    """
    Returns a logger instance for a specific module.
    
    Args:
        module_name (str): The name of the module or component.

    Returns:
        logging.Logger: Configured logger instance.
    """
    return logging.getLogger(module_name)


# Initialize logging when this module is imported
setup_logging()

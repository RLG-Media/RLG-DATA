import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
import os

# Set up basic configurations
LOG_FORMAT = "%(asctime)s — %(name)s — %(levelname)s — %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Base log directory
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# File handler settings
LOG_FILE = os.path.join(LOG_DIR, "rlg_data.log")
MAX_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5  # Keeps last 5 log files as backup

# Set up file handler
file_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=MAX_LOG_FILE_SIZE, backupCount=BACKUP_COUNT
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT))

# Console handler settings (useful for debugging)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT))

# SMTP handler settings (for critical errors)
smtp_handler = None
if os.getenv("MAIL_SERVER"):
    smtp_handler = SMTPHandler(
        mailhost=(os.getenv("MAIL_SERVER"), int(os.getenv("MAIL_PORT", 587))),
        fromaddr=os.getenv("MAIL_DEFAULT_SENDER"),
        toaddrs=[os.getenv("ADMIN_EMAIL")],
        subject="RLG DATA Application Error",
        credentials=(os.getenv("MAIL_USERNAME"), os.getenv("MAIL_PASSWORD")),
        secure=() if os.getenv("MAIL_USE_TLS", "True") == "True" else None,
    )
    smtp_handler.setLevel(logging.ERROR)
    smtp_handler.setFormatter(logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT))

# Create root logger
def setup_logging(app):
    """
    Configures logging for the application.
    - Adds file handler, console handler, and optional SMTP handler.
    """
    app.logger.setLevel(logging.DEBUG)

    # Attach file and console handlers to the app's logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)

    # Attach SMTP handler for error logging if enabled
    if smtp_handler:
        app.logger.addHandler(smtp_handler)

    app.logger.info("Logging setup complete.")


# Example usage in app initialization (e.g., app.py or __init__.py)
# from logging_config import setup_logging
# setup_logging(app)

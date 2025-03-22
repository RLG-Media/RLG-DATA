# logging_config.py - Configures logging for RLG Fans

import logging
from logging.handlers import RotatingFileHandler
import os

LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), "logs", "rlg_fans.log")
MAX_LOG_FILE_SIZE = 5 * 1024 * 1024  # 5 MB per log file
BACKUP_COUNT = 5  # Number of backup log files

def setup_logging():
    """
    Sets up logging with different levels for file and console output, including log rotation.
    """

    # Ensure the log directory exists
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

    # Create a logger
    logger = logging.getLogger("RLG_Fans")
    logger.setLevel(logging.DEBUG)

    # File Handler with rotation
    file_handler = RotatingFileHandler(
        LOG_FILE_PATH, maxBytes=MAX_LOG_FILE_SIZE, backupCount=BACKUP_COUNT
    )
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_format)

    # Console Handler for quick output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter("%(levelname)s - %(message)s")
    console_handler.setFormatter(console_format)

    # Adding both handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Test the setup
    logger.debug("Logging setup complete: Debug messages enabled.")
    logger.info("Logging setup complete: Console shows info-level messages and above.")

    return logger

# Call setup_logging to initialize logging on import
logger = setup_logging()

# Example usage
if __name__ == "__main__":
    logger.info("RLG Fans logging initialized successfully.")
    logger.debug("This is a debug-level message for troubleshooting.")
    logger.warning("This is a warning-level message for potential issues.")
    logger.error("This is an error-level message indicating something went wrong.")

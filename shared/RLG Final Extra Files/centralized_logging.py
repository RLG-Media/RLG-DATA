import os
import logging
import logging.handlers
from logging import Logger
from datetime import datetime
from .config import LOGGING_LEVEL, LOGGING_FORMAT, CENTRALIZED_LOGGING_SERVER, LOG_FILE_PATH

# Setup default logging level and format
LOGGING_LEVEL = LOGGING_LEVEL if LOGGING_LEVEL else logging.DEBUG
LOGGING_FORMAT = LOGGING_FORMAT if LOGGING_FORMAT else '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Create logger instance
logger = logging.getLogger('RLGLogger')
logger.setLevel(LOGGING_LEVEL)

# Centralized logging handler (e.g., for log aggregation tools such as ELK, Splunk, or others)
class CentralizedLoggingHandler(logging.Handler):
    """
    Custom logging handler to send logs to a centralized server.
    This could be an HTTP API endpoint, a logging service, or a database.
    """
    def emit(self, record):
        try:
            log_entry = self.format(record)
            # Send the log_entry to a centralized logging service
            # Placeholder: You can use requests, Kafka, or other methods to send logs
            # Example: requests.post(CENTRALIZED_LOGGING_SERVER, json={"log": log_entry})
            print(f"Sending log to centralized server: {log_entry}")  # This is for illustration; replace with actual service call
        except Exception as e:
            logger.error(f"Failed to send log to centralized server: {e}")
            super().emit(record)

# File-based logging handler (for local disk logging)
class FileLoggingHandler(logging.Handler):
    """
    Custom logging handler to save logs to a local file system.
    """
    def __init__(self, log_file_path: str):
        super().__init__()
        self.log_file_path = log_file_path
        self.setFormatter(logging.Formatter(LOGGING_FORMAT))

    def emit(self, record):
        try:
            # Format log message
            log_entry = self.format(record)
            with open(self.log_file_path, 'a') as log_file:
                log_file.write(f"{log_entry}\n")
        except Exception as e:
            logger.error(f"Error writing log to file {self.log_file_path}: {e}")
            super().emit(record)

# Setup centralized logging handler
def setup_centralized_logging():
    """
    Configures and sets up logging handlers for centralized logging.
    """
    try:
        # Adding a custom handler for centralized logging (for instance, ELK, Splunk, etc.)
        centralized_handler = CentralizedLoggingHandler()
        centralized_handler.setLevel(LOGGING_LEVEL)
        centralized_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
        logger.addHandler(centralized_handler)
        logger.info("Centralized logging handler initialized.")
    except Exception as e:
        logger.error(f"Error setting up centralized logging: {e}")
        raise

# Setup local file logging
def setup_file_logging():
    """
    Configures and sets up logging to a local file.
    """
    try:
        # Ensure the log directory exists
        os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
        
        # Adding file handler to logger
        file_handler = FileLoggingHandler(LOG_FILE_PATH)
        file_handler.setLevel(LOGGING_LEVEL)
        file_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
        logger.addHandler(file_handler)
        logger.info(f"File logging initialized at: {LOG_FILE_PATH}")
    except Exception as e:
        logger.error(f"Error setting up file logging: {e}")
        raise

# Log rotation setup (optional, if you want to limit log file sizes and keep logs in a rotating manner)
def setup_log_rotation():
    """
    Configures log rotation to avoid large log files.
    """
    try:
        log_rotation_handler = logging.handlers.RotatingFileHandler(
            LOG_FILE_PATH, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        log_rotation_handler.setLevel(LOGGING_LEVEL)
        log_rotation_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
        logger.addHandler(log_rotation_handler)
        logger.info("Log rotation setup complete.")
    except Exception as e:
        logger.error(f"Error setting up log rotation: {e}")
        raise

# Custom log levels (optional, you can create custom log levels for special situations)
def add_custom_log_levels():
    """
    Adds custom log levels if needed for different use cases.
    """
    try:
        logging.addLevelName(60, "URGENT")  # Custom urgent level
        logger.urgent = lambda msg, *args: logger.log(60, msg, *args)
        logger.info("Custom log level 'URGENT' added.")
    except Exception as e:
        logger.error(f"Error adding custom log levels: {e}")
        raise

# Test function to demonstrate logging
def test_logging():
    """
    A test function to demonstrate logging functionality.
    """
    try:
        logger.debug("This is a DEBUG message.")
        logger.info("This is an INFO message.")
        logger.warning("This is a WARNING message.")
        logger.error("This is an ERROR message.")
        logger.critical("This is a CRITICAL message.")
        logger.urgent("This is an URGENT message.")
    except Exception as e:
        logger.error(f"Error in logging test: {e}")

# Initialize logging setup
def initialize_logging():
    """
    Initializes the logging system for RLG Data and RLG Fans.
    - Centralized logging (for log aggregation).
    - Local file logging (for storage).
    - Log rotation (for managing file sizes).
    - Custom log levels (optional).
    """
    setup_file_logging()
    setup_centralized_logging()
    setup_log_rotation()
    add_custom_log_levels()

# Example of running the logging setup
if __name__ == "__main__":
    # Initialize logging configurations
    initialize_logging()
    
    # Test the logging
    test_logging()

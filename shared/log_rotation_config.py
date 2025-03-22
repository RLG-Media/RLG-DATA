# log_rotation_config.py

import logging
from logging.handlers import TimedRotatingFileHandler
import os

# Directory to store logs
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# General log configuration
LOG_FILE_PATH = os.path.join(LOG_DIR, "app.log")
LOG_LEVEL = logging.INFO

# Separate log files for RLG Data and RLG Fans
RLG_DATA_LOG_FILE = os.path.join(LOG_DIR, "rlg_data.log")
RLG_FANS_LOG_FILE = os.path.join(LOG_DIR, "rlg_fans.log")

def setup_logger(name, log_file_path):
    """
    Set up a logger with timed rotating file handler for log rotation.

    Args:
        name (str): Name of the logger.
        log_file_path (str): Path to the log file.
    """
    # Create the logger
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    # Define log format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set up TimedRotatingFileHandler
    handler = TimedRotatingFileHandler(
        log_file_path,
        when="midnight",  # Rotate at midnight
        interval=1,
        backupCount=30  # Keep logs for the past 30 days
    )
    handler.setLevel(LOG_LEVEL)
    handler.setFormatter(formatter)
    
    # Clear any previous handlers
    if logger.hasHandlers():
        logger.handlers.clear()
    
    logger.addHandler(handler)
    
    # Add stream handler for console output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

# Setting up loggers for RLG Data and RLG Fans components
app_logger = setup_logger("app_logger", LOG_FILE_PATH)
rlg_data_logger = setup_logger("rlg_data_logger", RLG_DATA_LOG_FILE)
rlg_fans_logger = setup_logger("rlg_fans_logger", RLG_FANS_LOG_FILE)

# Example usage
if __name__ == "__main__":
    app_logger.info("App logger initialized and running.")
    rlg_data_logger.info("RLG Data logger initialized and running.")
    rlg_fans_logger.info("RLG Fans logger initialized and running.")

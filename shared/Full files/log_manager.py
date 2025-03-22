# log_manager.py

import logging
from logging.handlers import RotatingFileHandler
import os

class LogManager:
    """
    LogManager class for handling logging across the entire application.
    """

    def __init__(self, log_dir='logs', log_file='application.log', max_bytes=10*1024*1024, backup_count=3):
        """
        Initializes the LogManager with log directory and file setup.

        :param log_dir: Directory where logs will be stored.
        :param log_file: Base name of the log file.
        :param max_bytes: Maximum size of the log file before rotation (in bytes).
        :param backup_count: Number of backup files to keep.
        """
        self.log_dir = log_dir
        self.log_file = log_file
        self.max_bytes = max_bytes
        self.backup_count = backup_count

        # Create log directory if it doesn't exist
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        # Initialize the logger
        self.logger = logging.getLogger('ApplicationLogger')
        self.logger.setLevel(logging.DEBUG)

        # Set up rotating file handler
        file_handler = RotatingFileHandler(
            os.path.join(self.log_dir, self.log_file),
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )

        # Define log formatting
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # Add the file handler to the logger
        self.logger.addHandler(file_handler)

    def get_logger(self):
        """
        Returns the configured logger instance.
        """
        return self.logger

    def log_debug(self, message):
        """
        Logs a debug message.
        """
        self.logger.debug(message)

    def log_info(self, message):
        """
        Logs an info message.
        """
        self.logger.info(message)

    def log_warning(self, message):
        """
        Logs a warning message.
        """
        self.logger.warning(message)

    def log_error(self, message):
        """
        Logs an error message.
        """
        self.logger.error(message)

    def log_critical(self, message):
        """
        Logs a critical message.
        """
        self.logger.critical(message)


# Example usage:
if __name__ == '__main__':
    log_manager = LogManager()
    logger = log_manager.get_logger()

    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")

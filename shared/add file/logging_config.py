import logging
import logging.handlers
from pathlib import Path
import os

class LoggingConfig:
    """
    A class to set up and manage logging configurations for RLG Data and RLG Fans.
    This configuration sets up both console and file logging with rotation.
    """
    # Directory where log files will be stored
    LOG_DIRECTORY = Path("logs")
    # Default log level for the root logger
    DEFAULT_LOG_LEVEL = logging.INFO
    # Log formatter for both console and file handlers
    FORMATTER = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    # Log level for file handler (detailed logging)
    FILE_HANDLER_LOG_LEVEL = logging.DEBUG
    # Log level for console handler
    CONSOLE_HANDLER_LOG_LEVEL = logging.INFO
    # Maximum size of a log file (10 MB)
    MAX_LOG_FILE_SIZE = 10 * 1024 * 1024
    # Number of backup log files to keep
    BACKUP_COUNT = 5

    @classmethod
    def setup_logging(cls) -> None:
        """
        Configure the logging system, including creation of log directory,
        setting up console and rotating file handlers, and initializing the root logger.
        """
        # Ensure the log directory exists
        cls.LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)

        # Configure the root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(cls.DEFAULT_LOG_LEVEL)
        # Clear existing handlers to prevent duplicate logs
        if root_logger.hasHandlers():
            root_logger.handlers.clear()
        
        # Add console handler
        root_logger.addHandler(cls._get_console_handler())
        # Add file handler for shared backend logs
        root_logger.addHandler(cls._get_file_handler("rlg_shared_backend.log"))

        root_logger.info("Logging configuration initialized.")

    @classmethod
    def _get_console_handler(cls) -> logging.StreamHandler:
        """
        Create and configure a console (stream) handler.
        
        Returns:
            logging.StreamHandler: Configured console handler.
        """
        console_handler = logging.StreamHandler()
        console_handler.setLevel(cls.CONSOLE_HANDLER_LOG_LEVEL)
        console_handler.setFormatter(cls.FORMATTER)
        return console_handler

    @classmethod
    def _get_file_handler(cls, filename: str) -> logging.handlers.RotatingFileHandler:
        """
        Create and configure a rotating file handler for logging.

        Args:
            filename (str): The name of the log file.

        Returns:
            logging.handlers.RotatingFileHandler: Configured file handler.
        """
        log_file_path = cls.LOG_DIRECTORY / filename
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file_path,
            maxBytes=cls.MAX_LOG_FILE_SIZE,
            backupCount=cls.BACKUP_COUNT
        )
        file_handler.setLevel(cls.FILE_HANDLER_LOG_LEVEL)
        file_handler.setFormatter(cls.FORMATTER)
        return file_handler

    @classmethod
    def get_logger(cls, logger_name: str) -> logging.Logger:
        """
        Retrieve a preconfigured logger by name.

        Args:
            logger_name (str): The name of the logger.

        Returns:
            logging.Logger: Configured logger instance.
        """
        logger_instance = logging.getLogger(logger_name)
        logger_instance.setLevel(cls.DEFAULT_LOG_LEVEL)
        return logger_instance

def set_module_loggers() -> None:
    """
    Configure specific loggers for modules used in RLG Data and RLG Fans.
    This allows fine-tuning of log levels for individual modules.
    """
    module_loggers = {
        "api_routes": logging.DEBUG,
        "authentication_utils": logging.INFO,
        "celery_tasks": logging.DEBUG,
        "dashboard_utils": logging.INFO,
        "db_helpers": logging.WARNING,
        "email_notifications": logging.DEBUG,
        "external_apis": logging.WARNING,
        "inbox_manager": logging.DEBUG,
    }

    for module_name, level in module_loggers.items():
        module_logger = logging.getLogger(module_name)
        module_logger.setLevel(level)
        module_logger.info("Logger for module '%s' set to level %s", module_name, logging.getLevelName(level))

def check_logging_health() -> bool:
    """
    Perform a health check to ensure logging is functioning correctly.

    Returns:
        bool: True if logging is operational; False otherwise.
    """
    try:
        test_logger = logging.getLogger("logging_health_check")
        test_logger.info("Logging health check passed.")
        return True
    except Exception as e:
        print(f"Logging health check failed: {e}")
        return False

# When run as a script, initialize logging and run a quick health test.
if __name__ == "__main__":
    LoggingConfig.setup_logging()
    set_module_loggers()

    # Example logging usage
    example_logger = LoggingConfig.get_logger("example_logger")
    example_logger.debug("This is a DEBUG message.")
    example_logger.info("This is an INFO message.")
    example_logger.warning("This is a WARNING message.")
    example_logger.error("This is an ERROR message.")
    example_logger.critical("This is a CRITICAL message.")

    # Perform a logging health check.
    if check_logging_health():
        print("Logging is operational.")
    else:
        print("Logging is not operational.")

import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
import os
from datetime import datetime

class LoggingService:
    """
    LoggingService provides a centralized logging mechanism with support for:
    - File logging with rotation
    - Email alerts for critical errors
    - Platform-specific logging
    - Dynamic log formatting
    """
    
    def __init__(self, platform, log_dir="logs", email_alerts=False, email_config=None):
        """
        Initialize the logging service.

        Args:
            platform (str): The platform (e.g., "RLG Data" or "RLG Fans").
            log_dir (str): Directory for storing log files.
            email_alerts (bool): Enable email alerts for critical errors.
            email_config (dict): Email configuration for SMTPHandler.
        """
        self.platform = platform
        self.log_dir = log_dir
        self.email_alerts = email_alerts
        self.email_config = email_config

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        self.logger = logging.getLogger(platform)
        self.logger.setLevel(logging.DEBUG)

        # Setup handlers
        self._setup_file_handler()
        if self.email_alerts:
            self._setup_email_handler()

    def _setup_file_handler(self):
        """
        Set up a rotating file handler for logging to a file.
        """
        log_file = os.path.join(self.log_dir, f"{self.platform.replace(' ', '_').lower()}_log.log")
        file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5)
        file_handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def _setup_email_handler(self):
        """
        Set up an email handler for critical error alerts.
        """
        if not self.email_config:
            raise ValueError("Email configuration is required for email alerts.")

        email_handler = SMTPHandler(
            mailhost=(self.email_config["smtp_server"], self.email_config["smtp_port"]),
            fromaddr=self.email_config["from_email"],
            toaddrs=self.email_config["to_emails"],
            subject=f"Critical Error in {self.platform}",
            credentials=(self.email_config["smtp_user"], self.email_config["smtp_password"]),
            secure=()
        )
        email_handler.setLevel(logging.CRITICAL)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        email_handler.setFormatter(formatter)
        self.logger.addHandler(email_handler)

    def log(self, level, message, extra_data=None):
        """
        Log a message with the specified level.

        Args:
            level (str): Logging level (e.g., "INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL").
            message (str): Log message.
            extra_data (dict): Additional data to include in the log.
        """
        extra = {"platform": self.platform, "extra_data": extra_data or {}}
        log_message = f"{message} | Extra Data: {extra['extra_data']}"
        if level.upper() == "DEBUG":
            self.logger.debug(log_message, extra=extra)
        elif level.upper() == "INFO":
            self.logger.info(log_message, extra=extra)
        elif level.upper() == "WARNING":
            self.logger.warning(log_message, extra=extra)
        elif level.upper() == "ERROR":
            self.logger.error(log_message, extra=extra)
        elif level.upper() == "CRITICAL":
            self.logger.critical(log_message, extra=extra)
        else:
            raise ValueError(f"Invalid log level: {level}")

    def log_event(self, event_name, event_data):
        """
        Log a structured event with additional context.

        Args:
            event_name (str): Name of the event (e.g., "UserLogin", "PaymentProcessed").
            event_data (dict): Details about the event.
        """
        message = f"Event: {event_name} | Data: {event_data}"
        self.logger.info(message)

# Example Usage:
if __name__ == "__main__":
    email_config = {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "from_email": "admin@example.com",
        "to_emails": ["alert@example.com"],
        "smtp_user": "admin@example.com",
        "smtp_password": "securepassword"
    }

    # Initialize logging service for RLG Data
    logging_service = LoggingService(
        platform="RLG Data",
        email_alerts=True,
        email_config=email_config
    )

    # Log a basic message
    logging_service.log("INFO", "Application started.")

    # Log a critical error with email alert
    logging_service.log("CRITICAL", "Database connection failed.", extra_data={"host": "db.example.com"})

    # Log a structured event
    logging_service.log_event("UserRegistration", {"user_id": 123, "email": "user@example.com"})

logging_service = LoggingService(
    platform="RLG Data",
    log_dir="logs",
    email_alerts=True,
    email_config=email_config
)
logging_service.log("INFO", "Application started.")
logging_service.log("ERROR", "An error occurred.", extra_data={"error_code": 500})

logging_service.log_event("UserLogin", {"user_id": 123, "ip_address": "192.168.1.1"})

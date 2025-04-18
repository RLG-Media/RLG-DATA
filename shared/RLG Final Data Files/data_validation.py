"""
data_validation.py
Provides data validation utilities for RLG Data and RLG Fans.
Ensures accuracy, integrity, and security of data across multiple modules.
"""

import re
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from email_validator import validate_email, EmailNotValidError
import jsonschema
from jsonschema.exceptions import ValidationError as JSONSchemaValidationError
import logging

# Configurations and constants
from config import ActiveConfig

# Logger setup
logger = logging.getLogger(__name__)


class DataValidation:
    """
    A utility class for data validation across different contexts.
    """

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validates an email address.

        Args:
            email (str): Email address to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        try:
            validate_email(email)
            logger.info(f"Email validation succeeded: {email}")
            return True
        except EmailNotValidError as e:
            logger.warning(f"Invalid email: {email}. Error: {e}")
            return False

    @staticmethod
    def validate_phone_number(phone_number: str, country_code: Optional[str] = None) -> bool:
        """
        Validates a phone number using regex (basic validation).

        Args:
            phone_number (str): Phone number to validate.
            country_code (str, optional): Country code for context-specific validation.

        Returns:
            bool: True if valid, False otherwise.
        """
        # Example basic regex for international numbers
        phone_regex = r"^\+?[1-9]\d{1,14}$"
        if re.match(phone_regex, phone_number):
            logger.info(f"Phone number validation succeeded: {phone_number}")
            return True
        else:
            logger.warning(f"Invalid phone number: {phone_number}")
            return False

    @staticmethod
    def validate_date(date_str: str, format: str = "%Y-%m-%d") -> bool:
        """
        Validates a date string against a specific format.

        Args:
            date_str (str): Date string to validate.
            format (str): Expected date format (default: '%Y-%m-%d').

        Returns:
            bool: True if valid, False otherwise.
        """
        try:
            datetime.strptime(date_str, format)
            logger.info(f"Date validation succeeded: {date_str}")
            return True
        except ValueError:
            logger.warning(f"Invalid date: {date_str}. Expected format: {format}")
            return False

    @staticmethod
    def validate_file_path(file_path: str, allowed_extensions: Optional[List[str]] = None) -> bool:
        """
        Validates a file path and checks for allowed extensions.

        Args:
            file_path (str): File path to validate.
            allowed_extensions (List[str], optional): List of allowed file extensions.

        Returns:
            bool: True if valid, False otherwise.
        """
        if not os.path.isfile(file_path):
            logger.warning(f"Invalid file path: {file_path}")
            return False

        if allowed_extensions:
            _, ext = os.path.splitext(file_path)
            if ext.lower() not in [f".{ext.lower()}" for ext in allowed_extensions]:
                logger.warning(f"File extension '{ext}' not allowed for file: {file_path}")
                return False

        logger.info(f"File path validation succeeded: {file_path}")
        return True

    @staticmethod
    def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """
        Validates data against a JSON schema.

        Args:
            data (dict): Data to validate.
            schema (dict): JSON schema.

        Returns:
            bool: True if valid, False otherwise.
        """
        try:
            jsonschema.validate(instance=data, schema=schema)
            logger.info("JSON schema validation succeeded.")
            return True
        except JSONSchemaValidationError as e:
            logger.warning(f"JSON schema validation failed. Error: {e}")
            return False

    @staticmethod
    def validate_username(username: str) -> bool:
        """
        Validates a username based on length and allowed characters.

        Args:
            username (str): Username to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        if 3 <= len(username) <= 30 and re.match(r"^[a-zA-Z0-9_]+$", username):
            logger.info(f"Username validation succeeded: {username}")
            return True
        else:
            logger.warning(f"Invalid username: {username}")
            return False

    @staticmethod
    def validate_api_response(response: Dict[str, Any], required_keys: List[str]) -> bool:
        """
        Validates an API response for required keys.

        Args:
            response (dict): API response data.
            required_keys (List[str]): List of keys expected in the response.

        Returns:
            bool: True if valid, False otherwise.
        """
        missing_keys = [key for key in required_keys if key not in response]
        if missing_keys:
            logger.warning(f"API response validation failed. Missing keys: {missing_keys}")
            return False

        logger.info("API response validation succeeded.")
        return True


# Example schema for validation
USER_DATA_SCHEMA = {
    "type": "object",
    "properties": {
        "username": {"type": "string", "minLength": 3, "maxLength": 30},
        "email": {"type": "string", "format": "email"},
        "date_of_birth": {"type": "string", "format": "date"},
    },
    "required": ["username", "email", "date_of_birth"],
}

# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    validator = DataValidation()

    # Test email validation
    email = "test@example.com"
    validator.validate_email(email)

    # Test username validation
    username = "valid_user_123"
    validator.validate_username(username)

    # Test JSON schema validation
    user_data = {
        "username": "valid_user",
        "email": "valid@example.com",
        "date_of_birth": "1990-01-01",
    }
    validator.validate_json_schema(user_data, USER_DATA_SCHEMA)

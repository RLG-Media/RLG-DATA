import re
from urllib.parse import urlparse
from datetime import datetime

# Regular expression for validating an email address
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

# Regular expression for validating a URL (basic validation)
URL_REGEX = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https:// or ftp://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # Domain name
    r'localhost|'  # localhost
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # IPv4 address
    r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # IPv6 address
    r'(?::\d+)?'  # Optional port number
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

# Error Messages
class ValidationError(Exception):
    """Custom Exception class for validation errors."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

# Validator Functions

def is_valid_email(email: str) -> bool:
    """Validates an email address using a regex pattern."""
    if not email or not re.match(EMAIL_REGEX, email):
        raise ValidationError("Invalid email format.")
    return True

def is_valid_url(url: str) -> bool:
    """Validates a URL structure using regex."""
    if not url or not re.match(URL_REGEX, url):
        raise ValidationError("Invalid URL format.")
    return True

def is_secure_url(url: str) -> bool:
    """Validates that a URL uses HTTPS."""
    parsed_url = urlparse(url)
    if parsed_url.scheme != "https":
        raise ValidationError("URL must use HTTPS.")
    return True

def is_valid_username(username: str, min_length=3, max_length=25) -> bool:
    """
    Validates a username for length and character restrictions.
    Allows only alphanumeric characters, underscores, and dots.
    """
    if not username:
        raise ValidationError("Username cannot be empty.")
    if len(username) < min_length or len(username) > max_length:
        raise ValidationError(f"Username must be between {min_length} and {max_length} characters.")
    if not re.match(r'^[a-zA-Z0-9_.]+$', username):
        raise ValidationError("Username can only contain letters, numbers, underscores, and periods.")
    return True

def is_valid_password(password: str, min_length=8) -> bool:
    """
    Validates a password for minimum length and complexity.
    Ensures at least 1 uppercase, 1 lowercase, 1 number, and 1 special character.
    """
    if len(password) < min_length:
        raise ValidationError(f"Password must be at least {min_length} characters long.")
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r'[a-z]', password):
        raise ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r'[0-9]', password):
        raise ValidationError("Password must contain at least one number.")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError("Password must contain at least one special character.")
    return True

def validate_phone_number(phone: str) -> bool:
    """
    Validates a phone number to ensure it contains only digits and is 10-15 characters long.
    """
    if not re.match(r'^\d{10,15}$', phone):
        raise ValidationError("Phone number must be between 10 and 15 digits.")
    return True

def validate_non_empty_string(value: str) -> bool:
    """
    Validates that a string is non-empty and not just whitespace.
    """
    if not value or not value.strip():
        raise ValidationError("Value cannot be empty or whitespace.")
    return True

def is_valid_date(date_str: str, date_format: str = "%Y-%m-%d") -> bool:
    """
    Validates if a string is a valid date in a given format (default: YYYY-MM-DD).
    """
    try:
        datetime.strptime(date_str, date_format)
        return True
    except ValueError:
        raise ValidationError(f"Date must be in format {date_format}.")

def validate_file_extension(filename: str, allowed_extensions: list = None) -> bool:
    """
    Validates the file extension for allowed types (e.g., .jpg, .png, .pdf).
    """
    if not allowed_extensions:
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'docx', 'txt']

    if '.' not in filename or filename.split('.')[-1].lower() not in allowed_extensions:
        raise ValidationError(f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}.")
    return True

def validate_positive_number(value: str) -> bool:
    """
    Validates if a string represents a positive number.
    """
    try:
        num = float(value)
        if num <= 0:
            raise ValidationError("Number must be positive.")
        return True
    except ValueError:
        raise ValidationError("Invalid number format.")

def validate_json_format(json_string: str) -> bool:
    """
    Validates if a string is in valid JSON format.
    """
    try:
        import json
        json.loads(json_string)
        return True
    except ValueError:
        raise ValidationError("Invalid JSON format.")

# Usage Example
if __name__ == '__main__':
    try:
        assert is_valid_email("test@example.com")
        assert is_valid_url("https://example.com")
        assert is_valid_password("ValidPass123!")
        assert validate_phone_number("1234567890")
        print("All validations passed.")
    except ValidationError as e:
        print(f"Validation error: {e.message}")

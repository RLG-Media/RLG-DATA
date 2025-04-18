import hashlib
import json
import os
import random
import re
import string
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, Optional

import pytz
from flask import request, jsonify, current_app


# Utility Functions
def hash_password(password: str, salt: Optional[str] = None) -> str:
    """
    Hashes a password with an optional salt for additional security.
    """
    salt = salt or os.urandom(16).hex()
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${hashed.hex()}"


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verifies a password against its hashed value.
    """
    try:
        salt, hashed = hashed_password.split('$')
        return hash_password(password, salt).split('$')[1] == hashed
    except ValueError:
        return False


def generate_random_string(length: int = 12, use_special_chars: bool = False) -> str:
    """
    Generates a random string of a given length.
    """
    chars = string.ascii_letters + string.digits
    if use_special_chars:
        chars += "!@#$%^&*()-_+=<>?"
    return ''.join(random.choice(chars) for _ in range(length))


def is_valid_email(email: str) -> bool:
    """
    Validates an email address using regex.
    """
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email) is not None


def load_json(file_path: str) -> Optional[Dict]:
    """
    Loads a JSON file and returns its contents as a dictionary.
    """
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_json(file_path: str, data: Dict) -> None:
    """
    Saves a dictionary to a JSON file.
    """
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


def utc_now() -> datetime:
    """
    Returns the current UTC time.
    """
    return datetime.now(pytz.utc)


def localize_time(dt: datetime, timezone: str) -> datetime:
    """
    Converts a datetime object to the specified timezone.
    """
    tz = pytz.timezone(timezone)
    return dt.astimezone(tz)


# Decorators
def json_response(func):
    """
    Wraps a Flask route to ensure the response is JSON formatted.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            response = func(*args, **kwargs)
            if isinstance(response, tuple):
                data, status = response
            else:
                data, status = response, 200
            return jsonify(data), status
        except Exception as e:
            current_app.logger.error(f"Error in {func.__name__}: {str(e)}")
            return jsonify({"error": str(e)}), 500
    return wrapper


def requires_auth(func):
    """
    Ensures the request is authenticated by checking for an 'Authorization' header.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Unauthorized access"}), 401
        # Perform token validation logic here (e.g., decode JWT)
        return func(*args, **kwargs)
    return wrapper


# Time Utilities
def time_difference_in_seconds(time1: datetime, time2: datetime) -> int:
    """
    Calculates the difference between two datetime objects in seconds.
    """
    delta = abs(time1 - time2)
    return int(delta.total_seconds())


def add_time_interval(base_time: datetime, seconds: int = 0, minutes: int = 0, hours: int = 0, days: int = 0) -> datetime:
    """
    Adds a time interval to a datetime object.
    """
    return base_time + timedelta(seconds=seconds, minutes=minutes, hours=hours, days=days)


# Configuration Utilities
def get_env_variable(key: str, default: Optional[Any] = None) -> Any:
    """
    Retrieves an environment variable or returns a default value.
    """
    return os.getenv(key, default)


def parse_config(config_file: str) -> Dict[str, Any]:
    """
    Parses a JSON configuration file.
    """
    config = load_json(config_file)
    if config is None:
        raise ValueError(f"Configuration file {config_file} is invalid or missing.")
    return config


# Example Usage
if __name__ == "__main__":
    print(generate_random_string(16, use_special_chars=True))
    print(is_valid_email("test@example.com"))
    print(utc_now())

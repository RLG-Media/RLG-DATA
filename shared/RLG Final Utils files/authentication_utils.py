# authentication_utils.py - Authentication Utilities for RLG Data and RLG Fans

import bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token
from datetime import datetime, timedelta
from backend.database import get_user_by_email, save_user, update_user_last_login
from backend.error_handlers import AuthenticationError
from shared.logging_config import logger

# Constants
ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
REFRESH_TOKEN_EXPIRES = timedelta(days=7)

def hash_password(plain_text_password):
    """
    Hashes a plain text password using bcrypt.

    Args:
        plain_text_password (str): The user's plain text password.

    Returns:
        str: The hashed password.
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(plain_text_password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


def verify_password(plain_text_password, hashed_password):
    """
    Verifies a plain text password against a hashed password.

    Args:
        plain_text_password (str): The user's plain text password.
        hashed_password (str): The hashed password stored in the database.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password.encode('utf-8'))


def authenticate_user(email, password):
    """
    Authenticates a user by their email and password.

    Args:
        email (str): The user's email.
        password (str): The user's plain text password.

    Returns:
        dict: A dictionary containing the user's tokens and information.

    Raises:
        AuthenticationError: If authentication fails.
    """
    user = get_user_by_email(email)
    if not user:
        logger.warning(f"Authentication failed: User with email {email} not found.")
        raise AuthenticationError("Invalid email or password.")

    if not verify_password(password, user["password"]):
        logger.warning(f"Authentication failed: Incorrect password for email {email}.")
        raise AuthenticationError("Invalid email or password.")

    # Generate tokens
    access_token = create_access_token(identity=user["id"], expires_delta=ACCESS_TOKEN_EXPIRES)
    refresh_token = create_refresh_token(identity=user["id"], expires_delta=REFRESH_TOKEN_EXPIRES)

    # Update last login
    update_user_last_login(user["id"])

    logger.info(f"User {email} authenticated successfully.")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_info": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"]
        }
    }


def validate_user_permissions(user_id, action):
    """
    Validates whether a user has permission to perform a specific action.

    Args:
        user_id (int): The user's ID.
        action (str): The action to validate permissions for.

    Raises:
        AuthenticationError: If the user does not have permission.
    """
    user = get_user_by_id(user_id)
    if not user:
        logger.error(f"Permission validation failed: User {user_id} not found.")
        raise AuthenticationError("User not found.")

    if action not in user["permissions"]:
        logger.warning(f"Permission denied: User {user_id} attempted {action}.")
        raise AuthenticationError(f"Permission denied for action: {action}")

    logger.info(f"User {user_id} has permission for action: {action}.")


def refresh_tokens(refresh_token):
    """
    Refreshes access and refresh tokens using a valid refresh token.

    Args:
        refresh_token (str): The user's refresh token.

    Returns:
        dict: A dictionary containing the new tokens.

    Raises:
        AuthenticationError: If the refresh token is invalid or expired.
    """
    try:
        decoded_token = decode_token(refresh_token)
        user_id = decoded_token["sub"]

        # Generate new tokens
        access_token = create_access_token(identity=user_id, expires_delta=ACCESS_TOKEN_EXPIRES)
        new_refresh_token = create_refresh_token(identity=user_id, expires_delta=REFRESH_TOKEN_EXPIRES)

        logger.info(f"Tokens refreshed for user {user_id}.")
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token
        }
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise AuthenticationError("Invalid or expired refresh token.")


def register_user(email, password, name, role="user"):
    """
    Registers a new user.

    Args:
        email (str): The user's email.
        password (str): The user's plain text password.
        name (str): The user's name.
        role (str): The user's role (default: "user").

    Returns:
        dict: A dictionary containing the user's information.

    Raises:
        AuthenticationError: If the user already exists or registration fails.
    """
    existing_user = get_user_by_email(email)
    if existing_user:
        logger.warning(f"Registration failed: User with email {email} already exists.")
        raise AuthenticationError("User already exists.")

    hashed_password = hash_password(password)
    user_id = save_user(email, hashed_password, name, role)

    logger.info(f"User {email} registered successfully with ID {user_id}.")
    return {
        "id": user_id,
        "email": email,
        "name": name,
        "role": role
    }

import os
import random
import string
import json
import logging
from datetime import datetime, timedelta
from typing import Optional
from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash, check_password_hash
from .database import db_session
from .models import ApiKey, User
from .exceptions import ApiKeyError

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Encryption key for API Key handling (you can also store this securely in an environment variable)
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "your_secret_encryption_key_here")
cipher_suite = Fernet(ENCRYPTION_KEY.encode())

def generate_api_key(length: int = 32) -> str:
    """Generate a random alphanumeric API key."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def encrypt_api_key(api_key: str) -> str:
    """Encrypt the API key using Fernet encryption."""
    encrypted_key = cipher_suite.encrypt(api_key.encode())
    return encrypted_key.decode()

def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt the encrypted API key using Fernet decryption."""
    decrypted_key = cipher_suite.decrypt(encrypted_key.encode())
    return decrypted_key.decode()

def validate_api_key(api_key: str) -> bool:
    """Validate the format of the API key (length, characters, etc.)."""
    if len(api_key) != 32 or not api_key.isalnum():
        logger.error(f"Invalid API key format: {api_key}")
        return False
    return True

def create_api_key(user_id: int, expiration_days: int = 30) -> dict:
    """Create a new API key for a user."""
    try:
        # Generate API key and encrypt it
        api_key = generate_api_key()
        encrypted_api_key = encrypt_api_key(api_key)
        
        # Store the API key in the database
        expiration_date = datetime.utcnow() + timedelta(days=expiration_days)
        new_api_key = ApiKey(user_id=user_id, api_key=encrypted_api_key, expiration_date=expiration_date)

        db_session.add(new_api_key)
        db_session.commit()

        logger.info(f"API key created for user {user_id}")
        return {
            "api_key": api_key,
            "expiration_date": expiration_date.isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error creating API key: {str(e)}")
        raise ApiKeyError("Error generating API key.")

def revoke_api_key(user_id: int, api_key: str) -> bool:
    """Revoke the API key for a user."""
    try:
        # Validate the API key format
        if not validate_api_key(api_key):
            raise ApiKeyError("Invalid API key format.")

        # Search for the API key in the database
        api_key_record = db_session.query(ApiKey).filter_by(user_id=user_id).first()

        if not api_key_record:
            raise ApiKeyError(f"No API key found for user {user_id}.")

        # Decrypt and check the provided API key against the stored one
        decrypted_key = decrypt_api_key(api_key_record.api_key)
        if api_key != decrypted_key:
            raise ApiKeyError("API key mismatch.")

        # Delete the API key record from the database
        db_session.delete(api_key_record)
        db_session.commit()

        logger.info(f"API key revoked for user {user_id}")
        return True
    
    except ApiKeyError as e:
        logger.error(f"Error revoking API key: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise ApiKeyError("An unexpected error occurred while revoking the API key.")

def list_api_keys(user_id: int) -> Optional[list]:
    """List all active API keys for a user."""
    try:
        # Fetch API keys for the given user
        api_keys = db_session.query(ApiKey).filter_by(user_id=user_id).all()
        
        if not api_keys:
            logger.info(f"No API keys found for user {user_id}")
            return None
        
        # Decrypt the API keys for response
        decrypted_keys = [
            {
                "api_key": decrypt_api_key(api_key.api_key),
                "expiration_date": api_key.expiration_date.isoformat()
            }
            for api_key in api_keys
        ]

        return decrypted_keys
    
    except Exception as e:
        logger.error(f"Error listing API keys: {str(e)}")
        raise ApiKeyError("Error retrieving API keys.")

def validate_user_permissions(user_id: int, required_role: str) -> bool:
    """Validate that the user has the required permissions to manage API keys."""
    user = db_session.query(User).filter_by(id=user_id).first()
    if user and user.role == required_role:
        return True
    return False

def update_api_key(user_id: int, old_api_key: str, new_api_key: str) -> dict:
    """Update the existing API key for a user."""
    try:
        # Validate the new API key format
        if not validate_api_key(new_api_key):
            raise ApiKeyError("Invalid new API key format.")
        
        # Retrieve the user's current API key
        api_key_record = db_session.query(ApiKey).filter_by(user_id=user_id).first()

        if not api_key_record:
            raise ApiKeyError(f"No API key found for user {user_id}.")
        
        # Decrypt and compare the old API key with the stored one
        decrypted_key = decrypt_api_key(api_key_record.api_key)
        if old_api_key != decrypted_key:
            raise ApiKeyError("Old API key mismatch.")

        # Encrypt the new API key and update it in the database
        encrypted_new_api_key = encrypt_api_key(new_api_key)
        api_key_record.api_key = encrypted_new_api_key
        db_session.commit()

        logger.info(f"API key updated for user {user_id}")
        return {
            "api_key": new_api_key,
            "expiration_date": api_key_record.expiration_date.isoformat()
        }
    
    except ApiKeyError as e:
        logger.error(f"Error updating API key: {str(e)}")
        raise ApiKeyError(str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise ApiKeyError("An unexpected error occurred while updating the API key.")


import hashlib
import hmac
import jwt
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, Optional
from flask import request, jsonify, abort

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Secret keys for signing and encryption (must be securely stored in environment variables)
SECRET_KEY = "your-very-secure-secret-key"  # Replace with environment variable
JWT_SECRET = "your-jwt-secret-key"  # Replace with environment variable
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 60

class SecurityManager:
    """
    SecurityManager handles security-related operations including API protection, encryption, 
    and token-based authentication.
    """

    @staticmethod
    def generate_hash(data: str, salt: Optional[str] = None) -> str:
        """
        Generate a secure hash for the given data.

        Args:
            data (str): The data to hash.
            salt (Optional[str]): Optional salt for additional security.

        Returns:
            str: The hashed data.
        """
        if not salt:
            salt = hashlib.sha256(os.urandom(32)).hexdigest()
        hashed_data = hashlib.pbkdf2_hmac("sha256", data.encode(), salt.encode(), 100000)
        return salt + ":" + hashed_data.hex()

    @staticmethod
    def verify_hash(data: str, hashed_data: str) -> bool:
        """
        Verify if the given data matches the hashed data.

        Args:
            data (str): The original data.
            hashed_data (str): The hashed data to verify against.

        Returns:
            bool: True if data matches, False otherwise.
        """
        salt, hash_value = hashed_data.split(":")
        return hashlib.pbkdf2_hmac("sha256", data.encode(), salt.encode(), 100000).hex() == hash_value

    @staticmethod
    def generate_jwt(payload: Dict[str, Any]) -> str:
        """
        Generate a JSON Web Token (JWT).

        Args:
            payload (Dict[str, Any]): Data to include in the token.

        Returns:
            str: The generated JWT.
        """
        payload["exp"] = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    @staticmethod
    def decode_jwt(token: str) -> Optional[Dict[str, Any]]:
        """
        Decode a JSON Web Token (JWT).

        Args:
            token (str): The JWT to decode.

        Returns:
            Optional[Dict[str, Any]]: Decoded payload if valid, otherwise None.
        """
        try:
            return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            logging.error("Token has expired.")
            return None
        except jwt.InvalidTokenError:
            logging.error("Invalid token.")
            return None

    @staticmethod
    def require_jwt_auth(f):
        """
        Flask decorator to enforce JWT-based authentication.

        Args:
            f: Flask route function.

        Returns:
            Wrapped function.
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get("Authorization", "").split("Bearer ")[-1]
            if not token:
                abort(401, description="Authorization token is missing.")
            decoded_token = SecurityManager.decode_jwt(token)
            if not decoded_token:
                abort(401, description="Invalid or expired token.")
            return f(*args, **kwargs)
        return decorated_function

    @staticmethod
    def validate_hmac_signature(secret: str, message: str, signature: str) -> bool:
        """
        Validate an HMAC signature for message integrity.

        Args:
            secret (str): Secret key used for HMAC.
            message (str): The original message.
            signature (str): The provided signature.

        Returns:
            bool: True if valid, False otherwise.
        """
        calculated_signature = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(calculated_signature, signature)

    @staticmethod
    def enforce_rate_limiting(client_id: str, limit: int, period_seconds: int, cache: Dict) -> bool:
        """
        Enforce API rate limiting for a client.

        Args:
            client_id (str): Unique identifier for the client.
            limit (int): Maximum allowed requests.
            period_seconds (int): Time window in seconds for the limit.
            cache (Dict): In-memory cache for tracking requests.

        Returns:
            bool: True if request is allowed, False otherwise.
        """
        current_time = datetime.utcnow().timestamp()
        if client_id not in cache:
            cache[client_id] = []
        # Remove outdated requests
        cache[client_id] = [t for t in cache[client_id] if current_time - t <= period_seconds]
        if len(cache[client_id]) >= limit:
            return False
        cache[client_id].append(current_time)
        return True

    @staticmethod
    def sanitize_input(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize input data to prevent injection attacks.

        Args:
            data (Dict[str, Any]): Input data to sanitize.

        Returns:
            Dict[str, Any]: Sanitized data.
        """
        sanitized_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized_data[key] = value.replace("<", "&lt;").replace(">", "&gt;")
            else:
                sanitized_data[key] = value
        return sanitized_data


# Example Usage
if __name__ == "__main__":
    # Example for hash generation and verification
    original_password = "secure_password123"
    hashed_password = SecurityManager.generate_hash(original_password)
    assert SecurityManager.verify_hash(original_password, hashed_password)

    # Example for JWT token generation and decoding
    token = SecurityManager.generate_jwt({"user_id": "12345", "role": "admin"})
    print(f"Generated Token: {token}")
    decoded_payload = SecurityManager.decode_jwt(token)
    print(f"Decoded Token: {decoded_payload}")

    # Example for HMAC signature validation
    message = "important-message"
    secret = "secret-key"
    signature = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    assert SecurityManager.validate_hmac_signature(secret, message, signature)

    # Example for sanitizing input
    unsafe_data = {"username": "<script>alert('hacked')</script>", "email": "user@example.com"}
    safe_data = SecurityManager.sanitize_input(unsafe_data)
    print(f"Sanitized Data: {safe_data}")

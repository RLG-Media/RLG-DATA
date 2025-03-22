import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any
from flask import request, jsonify, make_response

# Secret key for JWT (update with a secure, environment-specific key in production)
SECRET_KEY = "your-secure-secret-key"

# Password hashing utility
class PasswordManager:
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a plain text password.

        Args:
            password: Plain text password.

        Returns:
            Hashed password.
        """
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify a plain text password against a hashed password.

        Args:
            password: Plain text password.
            hashed_password: Hashed password.

        Returns:
            True if the password matches, False otherwise.
        """
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# Token-based authentication
class TokenManager:
    @staticmethod
    def generate_token(user_id: str, expiry_hours: int = 24) -> str:
        """
        Generate a JWT token.

        Args:
            user_id: Unique identifier for the user.
            expiry_hours: Token validity in hours.

        Returns:
            JWT token as a string.
        """
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=expiry_hours),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """
        Verify a JWT token.

        Args:
            token: JWT token.

        Returns:
            Decoded payload if token is valid.

        Raises:
            Exception if the token is invalid or expired.
        """
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise Exception("Token has expired.")
        except jwt.InvalidTokenError:
            raise Exception("Invalid token.")

# Authentication handler
class AuthenticationService:
    def __init__(self, user_database: Dict[str, Any]):
        """
        Initialize the authentication service.

        Args:
            user_database: Mock database or an interface for user management.
        """
        self.user_database = user_database

    def register_user(self, username: str, password: str) -> Dict[str, Any]:
        """
        Register a new user.

        Args:
            username: Unique username.
            password: Plain text password.

        Returns:
            A dictionary with registration status.
        """
        if username in self.user_database:
            return {"status": "error", "message": "Username already exists."}

        hashed_password = PasswordManager.hash_password(password)
        self.user_database[username] = {
            "password": hashed_password,
            "created_at": datetime.utcnow(),
        }
        return {"status": "success", "message": "User registered successfully."}

    def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user with a username and password.

        Args:
            username: Username.
            password: Plain text password.

        Returns:
            A dictionary containing authentication status and token if successful.
        """
        user = self.user_database.get(username)
        if not user:
            return {"status": "error", "message": "User not found."}

        if not PasswordManager.verify_password(password, user["password"]):
            return {"status": "error", "message": "Incorrect password."}

        token = TokenManager.generate_token(username)
        return {"status": "success", "token": token}

    def authorize_request(self) -> Dict[str, Any]:
        """
        Middleware to authorize API requests.

        Returns:
            Decoded token payload if successful.

        Raises:
            Exception if authorization fails.
        """
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise Exception("Authorization header missing or invalid.")

        token = auth_header.split(" ")[1]
        return TokenManager.verify_token(token)

# Example usage
if __name__ == "__main__":
    # Mock user database
    user_db = {}

    auth_service = AuthenticationService(user_db)

    # Register user
    print(auth_service.register_user("test_user", "secure_password123"))

    # Authenticate user
    login_response = auth_service.authenticate_user("test_user", "secure_password123")
    print(login_response)

    if login_response["status"] == "success":
        token = login_response["token"]
        print("Generated Token:", token)

        # Verify token
        try:
            decoded = TokenManager.verify_token(token)
            print("Decoded Token:", decoded)
        except Exception as e:
            print(str(e))

"""
auth_service.py
Handles authentication and authorization for RLG Data and RLG Fans.
"""

import bcrypt
import jwt
import datetime
from typing import Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models import User, Role
from config import settings

# Constants
JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

class AuthService:
    """
    Handles user authentication, token generation, and authorization logic.
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hashes a plain text password using bcrypt.
        """
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verifies a password against a bcrypt hash.
        """
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    @staticmethod
    def create_access_token(data: Dict[str, Any]) -> str:
        """
        Creates a JWT access token with an expiration time.
        """
        to_encode = data.copy()
        to_encode.update({"exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)})
        token = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token

    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """
        Creates a JWT refresh token with an extended expiration time.
        """
        to_encode = data.copy()
        to_encode.update({"exp": datetime.datetime.utcnow() + datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)})
        token = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token

    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """
        Decodes and validates a JWT token.
        """
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    @staticmethod
    def authenticate_user(email: str, password: str, db: Session) -> User:
        """
        Authenticates a user by email and password.
        """
        user = db.query(User).filter(User.email == email).first()
        if not user or not AuthService.verify_password(password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return user

    @staticmethod
    def generate_tokens(user: User) -> Dict[str, str]:
        """
        Generates access and refresh tokens for a user.
        """
        data = {"sub": user.id, "email": user.email, "role": user.role.name}
        access_token = AuthService.create_access_token(data)
        refresh_token = AuthService.create_refresh_token(data)
        return {"access_token": access_token, "refresh_token": refresh_token}

    @staticmethod
    def refresh_access_token(refresh_token: str) -> str:
        """
        Generates a new access token using a valid refresh token.
        """
        payload = AuthService.decode_token(refresh_token)
        new_access_token = AuthService.create_access_token(payload)
        return new_access_token

    @staticmethod
    def has_permission(user: User, required_role: str) -> bool:
        """
        Checks if the user has the required role for access.
        """
        return user.role.name.lower() == required_role.lower()

# Example API Usage
def login(email: str, password: str, db: Session) -> Dict[str, str]:
    """
    Handles user login, returns access and refresh tokens.
    """
    user = AuthService.authenticate_user(email, password, db)
    tokens = AuthService.generate_tokens(user)
    return tokens

def register_user(user_data: Dict[str, str], db: Session) -> User:
    """
    Registers a new user.
    """
    # Check if the user already exists
    if db.query(User).filter(User.email == user_data["email"]).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = AuthService.hash_password(user_data["password"])
    new_user = User(
        email=user_data["email"],
        username=user_data["username"],
        password=hashed_password,
        role_id=user_data["role_id"]
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Additional Security Recommendations
# 1. Rate Limiting: Use middleware or third-party services to limit login attempts.
# 2. Password Policies: Enforce strong password requirements during user registration.
# 3. Multi-Factor Authentication (MFA): Add support for MFA to enhance security.
# 4. Audit Logging: Record authentication events for audit and monitoring.

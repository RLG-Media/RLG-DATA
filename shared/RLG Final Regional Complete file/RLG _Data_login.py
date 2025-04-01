#!/usr/bin/env python3
"""
RLG_Data_login.py

This module handles user login for RLG Data & RLG Fans.
It provides a secure authentication endpoint that validates user credentials,
generates a JWT token, and returns user details including their locked location data.
For demonstration purposes, an in-memory user store is used; in production, use a secure database
with properly hashed passwords.

Special Note:
- Users from Israel (Special Region) have their location locked, and their pricing is fixed.
- The login response for such users includes the message:
      "עם ישראל חי!, הפתרון הטכנולוגי שישנה את העתיד."
"""

import os
import logging
import datetime
import jwt
from flask import Flask, request, jsonify

# ------------------------- CONFIGURATION -------------------------
# Set up logging
LOG_FILE = "rlg_data_login.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)
logger = logging.getLogger("RLGDataLogin")

# JWT configuration: In production, store the secret in environment variables
JWT_SECRET = os.getenv("JWT_SECRET", "your_jwt_secret_key")
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 3600  # Token valid for 1 hour

# ------------------------- DEMO USER DATABASE -------------------------
# For demonstration only; replace with a secure database in production.
# NOTE: Passwords must be stored securely (hashed) in production.
users_db = {
    "user123": {
        "username": "user123",
        "email": "user123@example.com",
        "password": "password123",  # DO NOT store plain-text passwords in production!
        "location": {"country": "Israel", "city": "Tel Aviv"},
        "location_locked": True,
        "special_message": "עם ישראל חי!, הפתרון הטכנולוגי שישנה את העתיד."
    },
    "user456": {
        "username": "user456",
        "email": "user456@example.com",
        "password": "password456",
        "location": {"country": "United States", "city": "New York"},
        "location_locked": False,
        "special_message": ""
    }
}

# ------------------------- FLASK APP SETUP -------------------------
app = Flask(__name__)

# ------------------------- HELPER FUNCTIONS -------------------------

def generate_token(user):
    """
    Generates a JWT token for the given user.
    
    Parameters:
        user (dict): The user record.
    
    Returns:
        str: A JWT token.
    """
    payload = {
        "username": user["username"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

# ------------------------- LOGIN ENDPOINT -------------------------

@app.route("/login", methods=["POST"])
def login():
    """
    Authenticates a user.

    Expected JSON payload:
        - username: str
        - password: str

    Returns:
        JSON object with a JWT token and user details upon successful login.
        If authentication fails, returns an error message.
    """
    try:
        data = request.get_json()
        if not data or "username" not in data or "password" not in data:
            logger.warning("Missing username or password in login request.")
            return jsonify({"error": "Username and password are required."}), 400

        username = data["username"]
        password = data["password"]

        # Retrieve the user from the in-memory database (replace with a real DB lookup in production)
        user = users_db.get(username)
        if not user:
            logger.warning(f"Login failed: User '{username}' not found.")
            return jsonify({"error": "Invalid credentials."}), 401

        # For production, verify hashed password. Here, a simple string comparison is used.
        if user["password"] != password:
            logger.warning(f"Login failed: Incorrect password for user '{username}'.")
            return jsonify({"error": "Invalid credentials."}), 401

        # Generate JWT token for the authenticated user
        token = generate_token(user)
        logger.info(f"User '{username}' logged in successfully.")

        # Build the response payload
        response_payload = {
            "message": "Login successful.",
            "token": token,
            "user": {
                "username": user["username"],
                "email": user["email"],
                "location": user["location"],
                "location_locked": user["location_locked"],
                "special_message": user["special_message"]
            }
        }
        return jsonify(response_payload), 200

    except Exception as e:
        logger.error(f"Error during login: {e}")
        return jsonify({"error": "An error occurred during login. Please try again."}), 500

@app.route("/users", methods=["GET"])
def list_users():
    """
    (For debugging purposes) Returns a list of all users.
    WARNING: Do not expose this endpoint in production.
    """
    return jsonify(users_db)

# ------------------------- MAIN EXECUTION -------------------------

if __name__ == "__main__":
    logger.info("🚀 Starting RLG Data & RLG Fans Login Service...")
    app.run(host="0.0.0.0", port=5002, debug=True)

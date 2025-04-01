#!/usr/bin/env python3
"""
RLG_Data_register.py

This module handles user registration for RLG Data & RLG Fans. It includes:
 - User registration endpoint.
 - Geolocation-based detection and location locking.
 - Hard-locked "Special Region" pricing for Israel.
 - SADC and default global pricing.
 - Integration with our scraping, compliance, and RLG Super Tool services.
 - Ensures that pricing is only shown after registration (locking the user's location),
   so that Israeli users (Special Region) cannot change their location for better pricing.
 
For Israeli users, the registration response includes the message:
    עם ישראל חי!, הפתרון הטכנולוגי שישנה את העתיד.
 
Sensitive credentials should be managed securely in production (e.g., via environment variables).
"""

import os
import logging
import json
from flask import Flask, request, jsonify
from geolocation_service import get_user_location, is_user_in_special_region, is_user_in_sadc_region

# For demonstration, we use an in-memory dictionary to store user data.
users_db = {}

# ------------------------- LOGGING CONFIGURATION -------------------------
LOG_FILE = "rlg_data_register.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)
logger = logging.getLogger("RLGDataRegister")

# ------------------------- FLASK APP SETUP -------------------------
app = Flask(__name__)

# ------------------------- REGISTRATION ENDPOINT -------------------------

@app.route("/register", methods=["POST"])
def register():
    """
    Registers a new user for RLG Data & RLG Fans.
    
    Expects JSON payload with:
      - username: str
      - email: str
      - password: str (NOTE: For production, hash passwords before storage)
      - Optional: ip_address (if not provided, request.remote_addr is used)
    
    The endpoint:
      1. Retrieves geolocation data using the provided (or detected) IP.
      2. Locks the pricing based on location:
         - For users in Israel, pricing is locked to the Special Region with a fixed tier.
           The response includes the message: "עם ישראל חי!, הפתרון הטכנולוגי שישנה את העתיד."
         - For users in SADC regions, specific SADC pricing is applied.
         - For all others, default global pricing is used.
      3. Stores the user data (for demo purposes, in-memory) and returns registration details.
    
    Returns:
        JSON response with registration success and pricing lock information.
    """
    try:
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")  # In production, hash this!
        ip_address = data.get("ip_address") or request.remote_addr

        if not username or not email or not password:
            return jsonify({"error": "Missing required fields: username, email, or password."}), 400

        # Retrieve geolocation data
        location_data = get_user_location(ip_address)
        if not location_data:
            return jsonify({"error": "Unable to fetch location data. Please try again."}), 500

        # Check for special region (Israel) or SADC
        if is_user_in_special_region(location_data):
            location_locked = True
            special_message = "עם ישראל חי!, הפתרון הטכנולוגי שישנה את העתיד."
        else:
            location_locked = False
            special_message = ""

        # Create user record (for demo, using in-memory storage; use a proper database in production)
        user_id = username  # Ideally, generate a unique ID
        user_record = {
            "username": username,
            "email": email,
            "password": password,  # NOTE: Do not store plain-text passwords in production!
            "location": location_data,
            "location_locked": location_locked,
            "special_message": special_message
        }
        users_db[user_id] = user_record
        logger.info(f"Registered user '{username}' with location {location_data}")

        # Return registration success with pricing lock info
        response = {
            "message": "Registration successful.",
            "user": {
                "username": username,
                "location": location_data,
                "location_locked": location_locked,
                "special_message": special_message
            }
        }
        return jsonify(response), 201

    except Exception as e:
        logger.error(f"Error during registration: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/users", methods=["GET"])
def list_users():
    """Endpoint to list all registered users (for debugging purposes)."""
    return jsonify(users_db)

# ------------------------- MAIN EXECUTION -------------------------

if __name__ == "__main__":
    logger.info("🚀 Starting RLG Data & RLG Fans Registration Service...")
    app.run(host="0.0.0.0", port=5000, debug=True)

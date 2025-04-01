#!/usr/bin/env python3
"""
RLG_Data_Home.py

This module serves as the landing page for RLG Data & RLG Fans.
It displays user-specific information if the user is registered (with locked location-based pricing)
and shows a general introduction with region-based pricing details for unregistered users.

Key Features:
- For registered users, displays locked pricing details (with special handling for Israel as "Special Region").
- For unregistered users, uses geolocation (via get_user_location) to display a general pricing range.
- For users in Israel, pricing is hard locked and shown as "Special Region" with the message:
    "עם ישראל חי!, הפתרון הטכנולוגי שישנה את העתיד."
- Integrates with our scraping, compliance, and RLG Super Tool services.
- Fully scalable, automated, and data-driven.
"""

import os
import logging
from flask import Flask, render_template, request, session
from geolocation_service import get_user_location
from pricing_handler import get_pricing  # Assumes this function returns a pricing dict based on IP
from RLG_Data_register import users_db  # In-memory user store from our registration module (for demo)

# ------------------------- LOGGING CONFIGURATION -------------------------
LOG_FILE = "rlg_data_home.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)
logger = logging.getLogger("RLGDataHome")

# ------------------------- FLASK APP SETUP -------------------------
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your_secret_key")

# ------------------------- HOME ENDPOINT -------------------------
@app.route("/")
def home():
    """
    Home endpoint for RLG Data & RLG Fans.
    
    - If the user is registered (present in session), it displays personalized pricing and other details.
    - If not registered, it fetches geolocation data from the visitor's IP, determines regional pricing,
      and shows a general introduction. For Israeli users, it displays "Special Region" pricing with
      the special Hebrew message.
    """
    # Check if user is logged in (for demo purposes, we assume session['user'] is set after login/registration)
    if "user" in session:
        user = session["user"]
        # Registered user's details include locked location and pricing (already determined at registration)
        logger.info(f"Registered user '{user['username']}' accessing home page.")
        return render_template("home.html", user=user, pricing=user.get("pricing_details"))
    
    # For unregistered users, detect location using request.remote_addr
    user_location = get_user_location(request.remote_addr)
    if user_location:
        # Determine pricing based on detected location
        pricing = get_pricing(request.remote_addr)  # get_pricing returns a pricing dict for the region
        # If the detected country is Israel, replace it with a "Special Region" label and message.
        if user_location.get("country") == "Israel":
            region_display = "Special Region"
            special_message = "עם ישראל חי!, הפתרון הטכנולוגי שישנה את העתיד."
        else:
            region_display = user_location.get("country")
            special_message = ""
    else:
        pricing = None
        region_display = "Unknown"
        special_message = ""

    # Render the home page with general information
    logger.info("Unregistered user accessing home page with location: %s", user_location)
    return render_template("home.html", user=None, pricing=pricing, 
                           region_name=region_display, special_message=special_message)

# ------------------------- MAIN EXECUTION -------------------------
if __name__ == "__main__":
    logger.info("🚀 Starting RLG Data & RLG Fans Home Service...")
    app.run(host="0.0.0.0", port=5003, debug=True)

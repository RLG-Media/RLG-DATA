# home_page.py
# Backend logic for serving and managing the home page for RLG Data and RLG Fans

from flask import Blueprint, render_template, jsonify, request
from datetime import datetime
import logging

# Blueprint for home page routes
home_page_bp = Blueprint('home_page', __name__)

# Logger configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Sample dynamic content for the home page
HERO_SECTION_CONTENT = {
    "title": "Welcome to RLG",
    "subtitle": "Your all-in-one data and fan management solution.",
    "cta": {
        "text": "Get Started",
        "url": "/register"
    }
}

TESTIMONIALS = [
    {"user": "John D.", "feedback": "RLG transformed my business!", "rating": 5},
    {"user": "Sophia R.", "feedback": "Incredible tools for managing my fans.", "rating": 4.5},
    {"user": "Alex T.", "feedback": "A must-have for any content creator!", "rating": 5},
]

FEATURES = [
    {"icon": "analytics", "title": "Powerful Analytics", "description": "Track, analyze, and improve your performance."},
    {"icon": "integration", "title": "Seamless Integrations", "description": "Connect to platforms like Instagram, TikTok, and more."},
    {"icon": "automation", "title": "Automation Tools", "description": "Save time with intelligent task automation."},
]

@home_page_bp.route('/', methods=['GET'])
def home():
    """
    Renders the home page template with dynamic content.
    """
    logger.info("Serving the home page.")
    try:
        return render_template(
            'home_page.html',
            hero_content=HERO_SECTION_CONTENT,
            testimonials=TESTIMONIALS,
            features=FEATURES,
            current_year=datetime.now().year
        )
    except Exception as e:
        logger.error(f"Error rendering the home page: {e}")
        return render_template('error.html', error_message="An error occurred while loading the home page.")

@home_page_bp.route('/api/testimonials', methods=['GET'])
def get_testimonials():
    """
    API endpoint to fetch testimonials dynamically.
    """
    logger.info("Fetching testimonials data.")
    try:
        return jsonify({"success": True, "data": TESTIMONIALS})
    except Exception as e:
        logger.error(f"Error fetching testimonials: {e}")
        return jsonify({"success": False, "message": "Unable to fetch testimonials."}), 500

@home_page_bp.route('/api/features', methods=['GET'])
def get_features():
    """
    API endpoint to fetch features dynamically.
    """
    logger.info("Fetching features data.")
    try:
        return jsonify({"success": True, "data": FEATURES})
    except Exception as e:
        logger.error(f"Error fetching features: {e}")
        return jsonify({"success": False, "message": "Unable to fetch features."}), 500

@home_page_bp.route('/contact', methods=['POST'])
def contact_us():
    """
    Handles contact form submissions.
    """
    logger.info("Received a contact form submission.")
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')

        if not name or not email or not message:
            logger.warning("Incomplete contact form submission.")
            return jsonify({"success": False, "message": "All fields are required."}), 400

        # Simulate sending an email or saving the message
        logger.info(f"Contact form submitted: {name}, {email}, {message}")
        return jsonify({"success": True, "message": "Thank you for reaching out. We'll get back to you soon."})
    except Exception as e:
        logger.error(f"Error handling contact form: {e}")
        return jsonify({"success": False, "message": "An error occurred. Please try again later."}), 500

@home_page_bp.route('/api/log-event', methods=['POST'])
def log_event():
    """
    Logs user interaction events for analytics purposes.
    """
    logger.info("Logging user event.")
    try:
        event_data = request.json
        event_name = event_data.get('event')
        additional_data = event_data.get('data', {})

        logger.info(f"Event logged: {event_name}, Data: {additional_data}")
        return jsonify({"success": True, "message": "Event logged successfully."})
    except Exception as e:
        logger.error(f"Error logging event: {e}")
        return jsonify({"success": False, "message": "Unable to log event."}), 500

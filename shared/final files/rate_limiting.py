from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging

# Set up logging to track rate limiting issues
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize Limiter with a default strategy of limiting requests by IP address
limiter = Limiter(app, key_func=get_remote_address)

# Define a rate limit strategy for RLG Data and RLG Fans
# 100 requests per minute per IP for general endpoints
DEFAULT_LIMIT = "100 per minute"

# 10 requests per second per IP for high-priority endpoints (e.g., API requests)
HIGH_PRIORITY_LIMIT = "10 per second"

# Define rate limits for specific routes
@app.route('/')
@limiter.limit(DEFAULT_LIMIT)
def home():
    """
    Home route that demonstrates rate limiting on general endpoints.
    """
    return jsonify({"message": "Welcome to RLG Data & Fans!"})


@app.route('/api/data', methods=['GET'])
@limiter.limit(DEFAULT_LIMIT)
def get_data():
    """
    This route handles general data retrieval with a rate limit of 100 requests per minute.
    """
    return jsonify({"data": "Here is some important data from RLG Data & Fans!"})


@app.route('/api/update', methods=['POST'])
@limiter.limit(HIGH_PRIORITY_LIMIT)
def update_data():
    """
    High-priority endpoint (e.g., data updates) with more strict rate limiting.
    """
    # Implement data update logic here
    return jsonify({"message": "Data updated successfully!"})


@app.route('/api/retrieve-stats', methods=['GET'])
@limiter.limit(DEFAULT_LIMIT)
def retrieve_stats():
    """
    Another endpoint with rate limiting, providing system statistics.
    """
    return jsonify({"stats": "Here are the system statistics."})


@app.errorhandler(429)
def ratelimit_error(error):
    """
    Handle rate-limiting errors (HTTP 429: Too Many Requests).
    This is triggered when a user exceeds their rate limit.
    """
    return jsonify({
        "error": "Too Many Requests",
        "message": "You have exceeded the rate limit. Please try again later."
    }), 429


@app.before_first_request
def setup_rate_limiting():
    """
    Set up any initial configuration for rate limiting (e.g., adjusting limits dynamically).
    """
    try:
        logger.info("Rate limiting setup complete.")
    except Exception as e:
        logger.error(f"Error setting up rate limiting: {str(e)}")


# Example to show how we can dynamically change rate limits (not used in this basic example, but useful for the future)
@app.route('/api/set-limits', methods=['POST'])
def set_dynamic_limits():
    """
    Endpoint to dynamically change rate limits based on user needs or usage patterns.
    This can be extended to allow admins to set different limits for different IPs or user types.
    """
    # This could include logic to set limits based on user role, plan, or time of day
    new_limit = request.json.get('limit', DEFAULT_LIMIT)
    limiter.limit(new_limit)
    return jsonify({"message": f"Rate limit updated to {new_limit}."}), 200


# Testing if the app runs
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

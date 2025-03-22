"""
rate_limiting.py
----------------
API rate limiting to prevent abuse and control resource consumption.
Handles token-based, IP-based, and user-specific rate limits.
"""

from flask import Flask, request, jsonify
from redis import Redis
from ratelimit import RateLimit  # Ensure your 'ratelimit' package provides a RateLimit class with a method 'redis_exceed'
from functools import wraps
from datetime import timedelta, datetime
from logging_config import get_logger  # Custom logger configuration module

# Initialize logger
logger = get_logger("RateLimiting")

# Configuration for rate limits
RATE_LIMIT_CONFIG = {
    "global": RateLimit(limit=100, period=3600),         # 100 requests per hour globally
    "user_specific": RateLimit(limit=10, period=60),       # 10 requests per minute per user
    "ip_specific": RateLimit(limit=50, period=300),        # 50 requests every 5 minutes per IP
}

# Initialize Redis (update host/port as needed for your deployment)
redis_client = Redis(host='localhost', port=6379, db=0)

def get_rate_limit_key():
    """
    Constructs a rate-limiting key based on request details.
    It uses the remote IP, Authorization token, or falls back to a default key.
    
    Returns:
        str: The rate limit key.
    """
    if request.headers.get('Authorization'):
        # Token-based limit (assumes "Bearer <token>")
        return f"token:{request.headers.get('Authorization').split()[-1]}"
    elif request.remote_addr:
        # IP-based limit
        return f"ip:{request.remote_addr}"
    else:
        return "default"

def apply_rate_limit(rate_limit_type: str):
    """
    Decorator to apply rate limiting to a Flask route.
    
    Args:
        rate_limit_type (str): The type of rate limit to apply ("global", "user_specific", "ip_specific").
    
    Returns:
        function: The decorated function enforcing rate limits.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = get_rate_limit_key()
            rate_limit = RATE_LIMIT_CONFIG.get(rate_limit_type)
            if rate_limit is None:
                logger.warning(f"Unknown rate limit type: {rate_limit_type}. Proceeding without rate limiting.")
                return func(*args, **kwargs)
            try:
                # This method is assumed to return a tuple: (remaining_requests, reset_time)
                remaining, reset_time = rate_limit.redis_exceed(redis_client, key)
                if remaining <= 0:
                    # If no requests remain, log and return a 429 response
                    reset_in_seconds = int((reset_time - datetime.utcnow()).total_seconds())
                    logger.warning(f"Rate limit exceeded for key {key}. Resets in {reset_in_seconds} seconds.")
                    response = jsonify({"error": "Rate limit exceeded. Please try again later."})
                    response.status_code = 429
                    response.headers["X-RateLimit-Limit"] = rate_limit.limit
                    response.headers["X-RateLimit-Remaining"] = 0
                    response.headers["X-RateLimit-Reset"] = reset_in_seconds
                    return response
                # Otherwise, proceed with the request
                response = func(*args, **kwargs)
                # Add rate limit headers to the response
                response.headers["X-RateLimit-Limit"] = rate_limit.limit
                response.headers["X-RateLimit-Remaining"] = remaining
                response.headers["X-RateLimit-Reset"] = int(reset_time.timestamp())
                return response
            except Exception as e:
                logger.error(f"Error applying rate limit: {e}")
                return jsonify({"error": "Server error"}), 500
        return wrapper
    return decorator

# Create Flask application and define sample endpoints
app = Flask(__name__)

@app.route('/api/data', methods=['GET'])
@apply_rate_limit("ip_specific")  # Apply IP-based rate limit
def get_data():
    # Placeholder logic for processing the GET request.
    return jsonify({"data": "Here is the data you requested"})

@app.route('/api/user/action', methods=['POST'])
@apply_rate_limit("user_specific")  # Apply user-specific rate limit
def user_action():
    # Placeholder logic for processing user-specific actions.
    return jsonify({"message": "User action processed successfully"})

@app.route('/api/global/status', methods=['GET'])
@apply_rate_limit("global")  # Apply global rate limit
def global_status():
    # Return a simple status message.
    return jsonify({"status": "System is operational"})

if __name__ == "__main__":
    logger.info("Starting rate limiting service.")
    app.run(debug=True)

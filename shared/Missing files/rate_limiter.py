"""
rate_limiting.py
----------------
API rate limiting to prevent abuse and control resource consumption.
Handles token-based, IP-based, and user-specific rate limits.
"""

import time
from flask import Flask, request, jsonify, g
from functools import wraps
from datetime import timedelta, datetime
import redis

# Initialize Flask app
app = Flask(__name__)

# Configure Redis (update host/port as needed for production)
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

# Rate Limiting Configuration
DEFAULT_RATE_LIMIT = 100      # Default requests per minute per user/IP
BURST_LIMIT = 200             # Burst limit for short-term spikes
GLOBAL_RATE_LIMIT = 1000      # Global limit for all requests
RATE_LIMIT_RESET_INTERVAL = 60  # Reset interval in seconds

def get_requester_identifier():
    """
    Determine the requester identifier.
    Prioritizes user ID from headers, falls back to IP address.
    
    Returns:
        str: A string identifier for rate limiting.
    """
    user_id = request.headers.get("X-User-ID")
    if user_id:
        return f"user:{user_id}"
    return f"ip:{request.remote_addr}"

def rate_limit(limit=DEFAULT_RATE_LIMIT, burst=BURST_LIMIT, interval=RATE_LIMIT_RESET_INTERVAL):
    """
    Rate limiting decorator that applies limits based on the provided parameters.

    Args:
        limit (int): Maximum requests allowed in the given interval.
        burst (int): Additional burst requests allowed.
        interval (int): Time window in seconds for rate limiting.

    Returns:
        function: Decorated function that enforces the rate limit.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Determine the rate limit key (user or IP based)
            identifier = get_requester_identifier()
            key = f"rate_limit:{identifier}"
            
            # Get current count for this identifier
            current_count = redis_client.get(key)
            current_count = int(current_count) if current_count else 0

            # Check global limit
            global_key = "rate_limit:global"
            global_count = redis_client.get(global_key)
            global_count = int(global_count) if global_count else 0

            if global_count >= GLOBAL_RATE_LIMIT:
                logger_message = f"Global rate limit exceeded. Global count: {global_count}"
                app.logger.warning(logger_message)
                return jsonify({"error": "Global rate limit exceeded", "retry_after": interval}), 429

            if current_count >= limit + burst:
                retry_after = redis_client.ttl(key)
                logger_message = f"Rate limit exceeded for {identifier}. Count: {current_count}, Retry after: {retry_after} seconds."
                app.logger.warning(logger_message)
                return jsonify({"error": "Rate limit exceeded", "retry_after": retry_after}), 429

            # Increment the counters for this identifier and global counter
            redis_client.incr(key)
            redis_client.incr(global_key)

            # Ensure expiration is set on the keys
            redis_client.expire(key, interval)
            redis_client.expire(global_key, interval)

            return func(*args, **kwargs)
        return wrapper
    return decorator

@app.before_request
def apply_global_rate_limit():
    """
    Global middleware to check the overall rate limit before processing each request.
    """
    global_key = "rate_limit:global"
    global_count = redis_client.get(global_key)
    global_count = int(global_count) if global_count else 0

    if global_count >= GLOBAL_RATE_LIMIT:
        return jsonify({
            "error": "Global rate limit exceeded",
            "retry_after": RATE_LIMIT_RESET_INTERVAL
        }), 429

@app.route("/api/data", methods=["GET"])
@rate_limit(limit=50, burst=100)
def get_data():
    """
    Example API endpoint protected by IP-specific rate limiting.
    """
    return jsonify({"message": "Data retrieved successfully!"})

@app.route("/api/status", methods=["GET"])
@rate_limit(limit=20, burst=50)
def get_status():
    """
    Example API endpoint with lower rate limits for status checks.
    """
    return jsonify({"message": "API status retrieved successfully!"})

@app.route("/api/unlimited", methods=["GET"])
def unlimited_access():
    """
    Example API endpoint without rate limiting.
    """
    return jsonify({"message": "Unlimited access granted!"})

def reset_rate_limit(identifier=None):
    """
    Reset rate limits for a specific identifier or all if not specified.

    Args:
        identifier (str, optional): Specific requester identifier (e.g., "user:123" or "ip:1.2.3.4").
    """
    if identifier:
        redis_client.delete(f"rate_limit:{identifier}")
    else:
        keys = redis_client.keys("rate_limit:*")
        for key in keys:
            redis_client.delete(key)

@app.route("/api/reset", methods=["POST"])
def reset_limits():
    """
    API endpoint to reset rate limits for testing or administrative purposes.
    Expects JSON with an optional "identifier" field.
    """
    identifier = request.json.get("identifier")
    reset_rate_limit(identifier)
    return jsonify({"message": "Rate limits reset successfully"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)

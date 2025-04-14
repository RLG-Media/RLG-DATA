"""
rate_limiter.py
----------------
API rate limiting to prevent abuse and control resource consumption.
Handles token-based, IP-based, and user-specific rate limits using Redis.
It supports configurable per-identifier and global limits, including burst capacity and automatic key expiration.
Additional logging helps monitor usage and debugging.

Enhancements:
  - Configurable limits using constants
  - Global rate limiting across all requests
  - Utility to reset limits for testing or administration
  - Integration-ready for RLG Data & RLG Fans (including scraping, compliance, AI Insights, reporting, monetization, etc.)
  - Ensures that pricing tiers (including Special Region pricing for Israel and dedicated SADC tiers) are part of our broader platform compliance
"""

import time
import logging
from flask import Flask, request, jsonify
from functools import wraps
from datetime import timedelta, datetime
import redis

# ------------------------------------------------------------------
# Flask Application (if running rate limiter standalone for testing)
# ------------------------------------------------------------------
app = Flask(__name__)

# ------------------------------------------------------------------
# Logging Configuration
# ------------------------------------------------------------------
logger = logging.getLogger("rate_limiter")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# ------------------------------------------------------------------
# Redis Connection Setup (adjust host/port for production)
# ------------------------------------------------------------------
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

# ------------------------------------------------------------------
# Rate Limiting Configuration Constants
# ------------------------------------------------------------------
DEFAULT_RATE_LIMIT = 100      # requests per minute per user/IP by default
BURST_LIMIT = 200             # allowable burst requests above the default
GLOBAL_RATE_LIMIT = 1000      # overall limit for all requests in the system per minute
RATE_LIMIT_RESET_INTERVAL = 60  # reset interval in seconds

# ------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------
def get_requester_identifier():
    """
    Determine a unique identifier for the requester.
    Tries to use a user ID from the headers ("X-User-ID") if available, otherwise falls back to IP.
    
    Returns:
        str: e.g., "user:123" or "ip:192.168.1.1"
    """
    user_id = request.headers.get("X-User-ID")
    if user_id:
        return f"user:{user_id}"
    return f"ip:{request.remote_addr}"

# ------------------------------------------------------------------
# Rate Limiting Decorator
# ------------------------------------------------------------------
def rate_limit(limit=DEFAULT_RATE_LIMIT, burst=BURST_LIMIT, interval=RATE_LIMIT_RESET_INTERVAL):
    """
    Decorator to enforce rate limiting on an endpoint.
    
    Args:
        limit (int): Maximum requests allowed in the interval.
        burst (int): Additional burst requests allowed.
        interval (int): Time window in seconds.
        
    Returns:
        function: The decorated endpoint function.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            identifier = get_requester_identifier()
            key = f"rate_limit:{identifier}"
            # Global counter key
            global_key = "rate_limit:global"
            
            # Retrieve current counts
            current_count = int(redis_client.get(key) or 0)
            global_count = int(redis_client.get(global_key) or 0)
            
            # Check global rate limit first
            if global_count >= GLOBAL_RATE_LIMIT:
                logger.warning(f"Global rate limit exceeded. Global count: {global_count}")
                return jsonify({"error": "Global rate limit exceeded", "retry_after": interval}), 429
            
            # Check identifier-specific (user or IP) limit
            if current_count >= (limit + burst):
                retry_after = redis_client.ttl(key)
                logger.warning(f"Rate limit exceeded for {identifier} (count: {current_count}, retry_after: {retry_after} seconds)")
                return jsonify({"error": "Rate limit exceeded", "retry_after": retry_after}), 429
            
            # Increment counts
            redis_client.incr(key)
            redis_client.incr(global_key)
            
            # Set expiration if not already set
            if redis_client.ttl(key) == -1:
                redis_client.expire(key, interval)
            if redis_client.ttl(global_key) == -1:
                redis_client.expire(global_key, interval)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# ------------------------------------------------------------------
# Global Rate Limit Middleware (Optional)
# ------------------------------------------------------------------
@app.before_request
def enforce_global_rate_limit():
    """
    Middleware that checks the global rate limit before processing any request.
    """
    global_key = "rate_limit:global"
    global_count = int(redis_client.get(global_key) or 0)
    if global_count >= GLOBAL_RATE_LIMIT:
        return jsonify({
            "error": "Global rate limit exceeded",
            "retry_after": RATE_LIMIT_RESET_INTERVAL
        }), 429

# ------------------------------------------------------------------
# Example Endpoints Protected by Rate Limiting
# ------------------------------------------------------------------

@app.route("/api/data", methods=["GET"])
@rate_limit(limit=50, burst=100)
def get_data():
    """
    Example endpoint: Returns sample data with rate limiting.
    """
    return jsonify({"message": "Data retrieved successfully!"})

@app.route("/api/status", methods=["GET"])
@rate_limit(limit=20, burst=50)
def get_status():
    """
    Example endpoint: Returns system status with lower rate limits.
    """
    return jsonify({"message": "API status retrieved successfully!"})

@app.route("/api/unlimited", methods=["GET"])
def unlimited_access():
    """
    Example endpoint without rate limiting.
    """
    return jsonify({"message": "Unlimited access granted!"})

# ------------------------------------------------------------------
# Rate Limit Reset Utility Functions & Endpoint
# ------------------------------------------------------------------
def reset_rate_limit(identifier: str = None):
    """
    Resets rate limits for a specific identifier or all identifiers if none provided.
    
    Args:
        identifier (str): E.g., "user:123" or "ip:1.2.3.4"
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
    API endpoint to reset rate limits. Useful for testing or admin purposes.
    Expects JSON payload with an optional "identifier" field.
    """
    identifier = request.json.get("identifier")
    reset_rate_limit(identifier)
    return jsonify({"message": "Rate limits reset successfully"})

# ------------------------------------------------------------------
# Main Execution (for standalone testing)
# ------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)

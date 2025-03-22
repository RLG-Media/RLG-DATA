import time
import logging
import json
import redis
from flask import request, jsonify, abort
from functools import wraps
from config import REDIS_CONFIG, API_THROTTLE_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Connect to Redis
redis_client = redis.StrictRedis(host=REDIS_CONFIG["host"], port=REDIS_CONFIG["port"], db=0, decode_responses=True)

# Load API throttle settings
DEFAULT_RATE_LIMIT = API_THROTTLE_CONFIG.get("default_rate_limit", 100)  # Requests per minute
USER_TIERS = API_THROTTLE_CONFIG.get("user_tiers", {
    "free": 50,
    "premium": 500,
    "enterprise": 5000
})
BLOCK_DURATION = API_THROTTLE_CONFIG.get("block_duration", 3600)  # 1-hour block for abuse
REGION_LIMITS = API_THROTTLE_CONFIG.get("region_limits", {
    "US": 200,
    "EU": 150,
    "Asia": 100,
    "Israel": 50
})


class APILimiter:
    """Implements API rate limiting and throttling for RLG Data and RLG Fans."""

    def __init__(self):
        self.redis_client = redis_client

    def get_user_tier_limit(self, user_id: str) -> int:
        """Determines API request limits based on user subscription tier."""
        user_tier = self.redis_client.get(f"user_tier:{user_id}") or "free"
        return USER_TIERS.get(user_tier, DEFAULT_RATE_LIMIT)

    def get_region_limit(self, region: str) -> int:
        """Fetches API limits based on the user's region."""
        return REGION_LIMITS.get(region, DEFAULT_RATE_LIMIT)

    def rate_limit_exceeded(self, identifier: str, limit: int) -> bool:
        """Checks if a user or IP has exceeded the rate limit."""
        key = f"api_limit:{identifier}"
        request_count = self.redis_client.incr(key)

        if request_count == 1:
            self.redis_client.expire(key, 60)  # Reset every 1 minute

        if request_count > limit:
            logging.warning(f"Rate limit exceeded for {identifier}. Blocking for {BLOCK_DURATION} seconds.")
            self.redis_client.setex(f"blocked:{identifier}", BLOCK_DURATION, "blocked")
            return True

        return False

    def is_blocked(self, identifier: str) -> bool:
        """Checks if a user or IP is currently blocked."""
        return self.redis_client.exists(f"blocked:{identifier}")

    def get_api_limit(self, user_id: str, ip: str, region: str) -> int:
        """Determines the applicable API limit based on user, IP, and region."""
        user_limit = self.get_user_tier_limit(user_id)
        region_limit = self.get_region_limit(region)
        return min(user_limit, region_limit)  # Applies the strictest limit

    def enforce_rate_limit(self, func):
        """Decorator to enforce API rate limiting on protected endpoints."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = request.headers.get("User-ID", "guest")
            ip = request.remote_addr
            region = request.headers.get("Region", "Global")

            identifier = f"{user_id}:{ip}"
            api_limit = self.get_api_limit(user_id, ip, region)

            # Check if user or IP is blocked
            if self.is_blocked(identifier):
                abort(403, description="Too many requests. Access temporarily blocked.")

            # Apply rate limiting
            if self.rate_limit_exceeded(identifier, api_limit):
                abort(429, description="Rate limit exceeded. Please slow down.")

            return func(*args, **kwargs)

        return wrapper


# Initialize API Limiter
api_limiter = APILimiter()

# Example Flask route with rate limiting
from flask import Flask
app = Flask(__name__)

@app.route("/fetch-data", methods=["GET"])
@api_limiter.enforce_rate_limit
def fetch_data():
    return jsonify({"message": "API response with protected data"})

if __name__ == "__main__":
    app.run(debug=True)

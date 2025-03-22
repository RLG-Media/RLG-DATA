import time
import json
import logging
import redis
import gzip
import pickle
from functools import wraps
from hashlib import sha256
from config import REDIS_CONFIG, CACHE_EXPIRY_SETTINGS

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Connect to Redis
redis_client = redis.StrictRedis(
    host=REDIS_CONFIG["host"], port=REDIS_CONFIG["port"], db=0, decode_responses=False
)

# Cache Expiry Settings
DEFAULT_CACHE_EXPIRY = CACHE_EXPIRY_SETTINGS.get("default", 300)  # 5 minutes
USER_TIER_EXPIRY = CACHE_EXPIRY_SETTINGS.get("user_tier_expiry", {
    "free": 180,  # 3 minutes
    "premium": 600,  # 10 minutes
    "enterprise": 1800  # 30 minutes
})
REGION_EXPIRY = CACHE_EXPIRY_SETTINGS.get("region_expiry", {
    "US": 300,
    "EU": 400,
    "Asia": 200,
    "Israel": 150
})


class CacheOptimization:
    """Implements optimized caching for RLG Data and RLG Fans."""

    def __init__(self):
        self.redis_client = redis_client

    def generate_cache_key(self, prefix: str, *args) -> str:
        """Generates a unique cache key based on parameters."""
        key_data = f"{prefix}:" + ":".join(map(str, args))
        return sha256(key_data.encode()).hexdigest()

    def get_cache_expiry(self, user_id: str, region: str) -> int:
        """Determines cache expiry time based on user tier and region."""
        user_tier = self.redis_client.get(f"user_tier:{user_id}") or "free"
        tier_expiry = USER_TIER_EXPIRY.get(user_tier, DEFAULT_CACHE_EXPIRY)
        region_expiry = REGION_EXPIRY.get(region, DEFAULT_CACHE_EXPIRY)
        return min(tier_expiry, region_expiry)

    def compress_data(self, data):
        """Compresses data using gzip for efficient storage."""
        return gzip.compress(pickle.dumps(data))

    def decompress_data(self, compressed_data):
        """Decompresses data retrieved from cache."""
        return pickle.loads(gzip.decompress(compressed_data))

    def cache_result(self, prefix: str, expiry_time=None):
        """Decorator to cache function results based on parameters."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                user_id = kwargs.get("user_id", "guest")
                region = kwargs.get("region", "Global")
                cache_key = self.generate_cache_key(prefix, *args, *kwargs.values())

                # Check cache
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    logging.info(f"Cache hit for key: {cache_key}")
                    return self.decompress_data(cached_data)

                # Call function and cache result
                result = func(*args, **kwargs)
                expiry = expiry_time or self.get_cache_expiry(user_id, region)
                self.redis_client.setex(cache_key, expiry, self.compress_data(result))
                logging.info(f"Cache set for key: {cache_key} with expiry: {expiry} seconds")
                return result

            return wrapper
        return decorator

    def invalidate_cache(self, prefix: str, *args):
        """Invalidates cache for specific keys."""
        cache_key = self.generate_cache_key(prefix, *args)
        self.redis_client.delete(cache_key)
        logging.info(f"Cache invalidated for key: {cache_key}")

    def clear_cache(self):
        """Clears all cache (use with caution)."""
        self.redis_client.flushdb()
        logging.warning("All cache data has been cleared!")


# Initialize Cache Optimization
cache_optimizer = CacheOptimization()

# Example Usage
@cache_optimizer.cache_result("user_data", expiry_time=600)
def get_user_data(user_id: str, region: str):
    """Simulated function fetching user data."""
    time.sleep(2)  # Simulate delay
    return {"user_id": user_id, "region": region, "data": "User analytics and insights"}

if __name__ == "__main__":
    print(get_user_data(user_id="123", region="US"))  # First call (cache miss)
    print(get_user_data(user_id="123", region="US"))  # Second call (cache hit)

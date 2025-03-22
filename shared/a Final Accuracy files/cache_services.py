import redis
import json
import logging
from typing import Any, Optional

# Configure the logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("cache_logs.log"),
        logging.StreamHandler()
    ]
)

class CacheService:
    """
    Service class for managing caching operations for RLG Data and RLG Fans.
    Supports Redis for in-memory caching with efficient key-value storage.
    """

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, password: Optional[str] = None):
        """
        Initialize the CacheService with Redis configuration.

        Args:
            host: Redis server hostname.
            port: Redis server port.
            db: Redis database number.
            password: Optional password for Redis authentication.
        """
        self.redis_client = redis.StrictRedis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True
        )
        try:
            self.redis_client.ping()
            logging.info("Connected to Redis server at %s:%d", host, port)
        except redis.ConnectionError as e:
            logging.error("Failed to connect to Redis server: %s", e)
            raise

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Store a value in the cache with an optional time-to-live (TTL).

        Args:
            key: The key under which the value is stored.
            value: The value to store (will be serialized to JSON if not a string).
            ttl: Time-to-live in seconds (optional).
        """
        try:
            if not isinstance(value, str):
                value = json.dumps(value)
            self.redis_client.set(key, value, ex=ttl)
            logging.info("Key '%s' set in cache with TTL: %s", key, ttl)
        except Exception as e:
            logging.error("Failed to set key '%s' in cache: %s", key, e)
            raise

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache by key.

        Args:
            key: The key to retrieve.

        Returns:
            The value stored under the key, or None if the key does not exist.
        """
        try:
            value = self.redis_client.get(key)
            if value is not None:
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    pass
            logging.info("Key '%s' retrieved from cache", key)
            return value
        except Exception as e:
            logging.error("Failed to get key '%s' from cache: %s", key, e)
            raise

    def delete(self, key: str):
        """
        Delete a value from the cache by key.

        Args:
            key: The key to delete.
        """
        try:
            result = self.redis_client.delete(key)
            if result:
                logging.info("Key '%s' deleted from cache", key)
            else:
                logging.warning("Key '%s' not found in cache", key)
        except Exception as e:
            logging.error("Failed to delete key '%s' from cache: %s", key, e)
            raise

    def flush_all(self):
        """
        Clear all data from the cache.
        """
        try:
            self.redis_client.flushall()
            logging.info("All keys flushed from cache")
        except Exception as e:
            logging.error("Failed to flush all keys from cache: %s", e)
            raise

    def get_keys(self, pattern: str = "*") -> list:
        """
        Retrieve a list of keys matching a pattern.

        Args:
            pattern: The pattern to match keys (default is '*', which matches all keys).

        Returns:
            A list of matching keys.
        """
        try:
            keys = self.redis_client.keys(pattern)
            logging.info("Keys retrieved with pattern '%s': %d found", pattern, len(keys))
            return keys
        except Exception as e:
            logging.error("Failed to retrieve keys with pattern '%s': %s", pattern, e)
            raise

# Example usage
if __name__ == "__main__":
    try:
        cache_service = CacheService()

        # Set a key with a TTL of 60 seconds
        cache_service.set("example_key", {"value": 123}, ttl=60)

        # Get the value of the key
        value = cache_service.get("example_key")
        print("Retrieved from cache:", value)

        # Get all keys
        keys = cache_service.get_keys()
        print("Keys in cache:", keys)

        # Delete the key
        cache_service.delete("example_key")

        # Flush all keys
        cache_service.flush_all()

    except Exception as e:
        logging.error("An error occurred: %s", e)

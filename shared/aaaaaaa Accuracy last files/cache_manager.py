"""
cache_manager.py
Manages caching operations for RLG Data and RLG Fans to improve performance and reduce redundant data processing.
"""

from typing import Any, Optional
import time
import redis
from hashlib import sha256
from config import settings
from logging_service import logger

# Constants
CACHE_TTL = settings.CACHE_TTL  # Default Time-to-Live for cache entries (in seconds)
REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT
REDIS_PASSWORD = settings.REDIS_PASSWORD


class CacheManager:
    """
    Provides methods to interact with the Redis cache.
    """
    def __init__(self):
        try:
            self.redis_client = redis.StrictRedis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD,
                decode_responses=True,
            )
            # Test the connection
            self.redis_client.ping()
            logger.info("Successfully connected to Redis.")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise ConnectionError("Unable to connect to Redis server.")

    def generate_cache_key(self, *args: Any, **kwargs: Any) -> str:
        """
        Generates a unique cache key based on input arguments.
        
        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            str: A SHA-256 hash representing the unique cache key.
        """
        key_base = str(args) + str(kwargs)
        return sha256(key_base.encode("utf-8")).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieves a value from the cache.
        
        Args:
            key (str): The cache key.

        Returns:
            Optional[Any]: The cached value, or None if the key does not exist.
        """
        try:
            value = self.redis_client.get(key)
            if value:
                logger.debug(f"Cache hit for key: {key}")
            else:
                logger.debug(f"Cache miss for key: {key}")
            return value
        except Exception as e:
            logger.error(f"Error retrieving cache for key {key}: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = CACHE_TTL) -> None:
        """
        Stores a value in the cache.
        
        Args:
            key (str): The cache key.
            value (Any): The value to cache.
            ttl (Optional[int]): Time-to-Live for the cache entry in seconds.
        """
        try:
            self.redis_client.setex(key, ttl, value)
            logger.debug(f"Value set in cache for key: {key}, TTL: {ttl}s")
        except Exception as e:
            logger.error(f"Error setting cache for key {key}: {e}")

    def delete(self, key: str) -> None:
        """
        Deletes a cache entry by key.
        
        Args:
            key (str): The cache key to delete.
        """
        try:
            self.redis_client.delete(key)
            logger.debug(f"Cache entry deleted for key: {key}")
        except Exception as e:
            logger.error(f"Error deleting cache for key {key}: {e}")

    def flush(self) -> None:
        """
        Clears the entire cache.
        """
        try:
            self.redis_client.flushdb()
            logger.info("Cache successfully cleared.")
        except Exception as e:
            logger.error(f"Error flushing cache: {e}")

    def cache_decorator(self, ttl: Optional[int] = CACHE_TTL):
        """
        A decorator to cache the results of a function.
        
        Args:
            ttl (Optional[int]): Time-to-Live for the cache entry in seconds.
        
        Returns:
            Callable: The wrapped function with caching.
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                cache_key = self.generate_cache_key(func.__name__, *args, **kwargs)
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    return cached_result

                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl)
                return result
            return wrapper
        return decorator

    def get_cache_stats(self) -> dict:
        """
        Retrieves cache statistics such as hits, misses, and memory usage.
        
        Returns:
            dict: Cache statistics.
        """
        try:
            stats = self.redis_client.info()
            logger.debug(f"Cache stats retrieved: {stats}")
            return {
                "hits": stats.get("keyspace_hits", 0),
                "misses": stats.get("keyspace_misses", 0),
                "memory_used": stats.get("used_memory_human", "N/A"),
            }
        except Exception as e:
            logger.error(f"Error retrieving cache stats: {e}")
            return {}

    def cache_exists(self, key: str) -> bool:
        """
        Checks if a cache key exists.
        
        Args:
            key (str): The cache key.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        try:
            exists = self.redis_client.exists(key)
            logger.debug(f"Cache key exists: {key} -> {exists}")
            return bool(exists)
        except Exception as e:
            logger.error(f"Error checking cache existence for key {key}: {e}")
            return False


# Example Usage
# cache_manager = CacheManager()
# cache_manager.set("test_key", "test_value")
# value = cache_manager.get("test_key")
# cache_manager.delete("test_key")
# cache_manager.flush()

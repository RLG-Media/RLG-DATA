import os
import logging
import redis
from django.core.cache import cache
from functools import wraps
from .config import CACHE_REDIS_URL, CACHE_TIMEOUT

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache configuration
CACHE_TIMEOUT_DEFAULT = 60 * 15  # 15 minutes default timeout
REDIS_CONNECTION_POOL = None

# Initialize Redis connection pool (if needed for larger-scale applications)
def initialize_redis_connection():
    """
    Initializes the Redis connection pool using the configuration provided.
    This allows multiple connections to be reused efficiently.
    """
    global REDIS_CONNECTION_POOL
    if REDIS_CONNECTION_POOL is None:
        try:
            REDIS_CONNECTION_POOL = redis.ConnectionPool.from_url(CACHE_REDIS_URL)
            logger.info(f"Redis connection pool initialized with URL: {CACHE_REDIS_URL}")
        except Exception as e:
            logger.error(f"Error initializing Redis connection: {e}")
            raise ConnectionError("Failed to initialize Redis connection pool.")

# Function to get cache data with default timeout
def get_cache_data(key: str):
    """
    Retrieves data from the cache using the provided key.
    If the data is not found, returns None.
    
    Args:
        key (str): The cache key to retrieve data.
    
    Returns:
        object: The cached data or None if the key does not exist in the cache.
    """
    try:
        data = cache.get(key)
        if data:
            logger.info(f"Cache hit for key: {key}")
        else:
            logger.warning(f"Cache miss for key: {key}")
        return data
    except Exception as e:
        logger.error(f"Error retrieving data from cache for key {key}: {e}")
        return None

# Function to set cache data with expiration
def set_cache_data(key: str, value: object, timeout: int = CACHE_TIMEOUT_DEFAULT):
    """
    Stores data in the cache with the specified key and an optional timeout.
    If timeout is not provided, it defaults to CACHE_TIMEOUT_DEFAULT.
    
    Args:
        key (str): The cache key.
        value (object): The data to be cached.
        timeout (int): The expiration time in seconds (default is 15 minutes).
    """
    try:
        cache.set(key, value, timeout=timeout)
        logger.info(f"Data cached with key: {key} and timeout: {timeout}s")
    except Exception as e:
        logger.error(f"Error setting data in cache for key {key}: {e}")
        raise CacheError(f"Failed to set data in cache for key: {key}")

# Function to delete cache data for a specific key
def delete_cache_data(key: str):
    """
    Deletes data from the cache using the specified key.
    
    Args:
        key (str): The cache key to delete.
    """
    try:
        cache.delete(key)
        logger.info(f"Cache data deleted for key: {key}")
    except Exception as e:
        logger.error(f"Error deleting data from cache for key {key}: {e}")
        raise CacheError(f"Failed to delete data from cache for key: {key}")

# Cache decorator for automatic caching of function results
def cache_function_result(key: str, timeout: int = CACHE_TIMEOUT_DEFAULT):
    """
    A decorator to cache the result of a function.
    
    Args:
        key (str): The cache key.
        timeout (int): The expiration time in seconds (default is 15 minutes).
        
    Returns:
        function: A wrapped function that caches its result.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if result is already in cache
            cached_data = get_cache_data(key)
            if cached_data:
                return cached_data
            # If not in cache, call the function and store the result in cache
            result = func(*args, **kwargs)
            set_cache_data(key, result, timeout)
            return result
        return wrapper
    return decorator

# Caching for large datasets or frequently accessed data
def cache_large_data(key: str, data_function, timeout: int = CACHE_TIMEOUT_DEFAULT):
    """
    Caches the result of a large dataset retrieval function.
    
    Args:
        key (str): The cache key.
        data_function (callable): The function that retrieves the data.
        timeout (int): The expiration time in seconds (default is 15 minutes).
    """
    try:
        # Check if the data is already cached
        cached_data = get_cache_data(key)
        if cached_data:
            return cached_data

        # If not cached, retrieve the data using the provided function
        data = data_function()
        # Store the result in cache for future access
        set_cache_data(key, data, timeout)
        return data
    except Exception as e:
        logger.error(f"Error caching large data for key {key}: {e}")
        raise CacheError(f"Failed to cache large data for key: {key}")

# Function to clear all cached data (use cautiously)
def clear_all_cache():
    """
    Clears all cached data. Use with caution as it may affect performance.
    """
    try:
        cache.clear()
        logger.info("All cached data has been cleared.")
    except Exception as e:
        logger.error(f"Error clearing all cache data: {e}")
        raise CacheError("Failed to clear all cache data.")

# Custom exception for cache errors
class CacheError(Exception):
    pass

# Function to manually expire a cached key (useful for manual cache invalidation)
def expire_cache_key(key: str):
    """
    Manually expire a cached key.
    
    Args:
        key (str): The cache key to expire.
    """
    try:
        cache.delete(key)
        logger.info(f"Manually expired cache for key: {key}")
    except Exception as e:
        logger.error(f"Error expiring cache for key {key}: {e}")
        raise CacheError(f"Failed to expire cache for key: {key}")

# Initialize the Redis connection pool if necessary
initialize_redis_connection()

# Example usage of caching functions (replace with actual function calls in your application)
if __name__ == "__main__":
    # Example for setting cache data
    set_cache_data("user_data:12345", {"name": "John Doe", "age": 30})

    # Example for getting cache data
    user_data = get_cache_data("user_data:12345")
    print(user_data)

    # Example for deleting cache data
    delete_cache_data("user_data:12345")

    # Example for caching function results
    @cache_function_result("user_data:12345")
    def fetch_user_data():
        # Simulate fetching data from a database or external API
        return {"name": "John Doe", "age": 30}
    
    user_data = fetch_user_data()  # First call will fetch and cache the result
    print(user_data)

    # Example for clearing all cache
    clear_all_cache()

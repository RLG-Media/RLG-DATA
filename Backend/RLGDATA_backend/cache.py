import redis
import pickle
import hashlib
import logging
from functools import wraps
from config import CACHE_TIMEOUT

# Configure logging
logging.basicConfig(level=logging.INFO)

# Connect to Redis
cache = redis.StrictRedis(host='localhost', port=6379, db=0)

def generate_cache_key(func_name, *args, **kwargs):
    """
    Generate a unique cache key based on the function name and its arguments.
    
    :param func_name: The name of the function
    :param args: The positional arguments of the function
    :param kwargs: The keyword arguments of the function
    :return: A hashed cache key
    """
    key = f"{func_name}:{args}:{kwargs}"
    return hashlib.sha256(key.encode()).hexdigest()

def cache_result(timeout=CACHE_TIMEOUT):
    """
    Decorator that caches the result of a function using Redis.
    
    :param timeout: Time in seconds before the cache expires (default is defined in config)
    :return: Cached result if available, otherwise the original function result
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate a unique cache key based on the function and its arguments
            cache_key = generate_cache_key(func.__name__, *args, **kwargs)
            try:
                # Check if the result is already cached
                cached_result = cache.get(cache_key)
                if cached_result:
                    logging.info(f"Cache hit for {func.__name__} with key: {cache_key}")
                    return pickle.loads(cached_result)

                # Call the original function and cache the result
                result = func(*args, **kwargs)
                cache.setex(cache_key, timeout, pickle.dumps(result))
                logging.info(f"Cache miss for {func.__name__}. Caching result with key: {cache_key}")

                return result

            except (redis.RedisError, Exception) as e:
                logging.error(f"Error accessing Redis cache: {e}")
                # Fallback to executing the function without caching in case of an error
                return func(*args, **kwargs)

        return wrapper
    return decorator

def invalidate_cache(func_name, *args, **kwargs):
    """
    Invalidate the cache for a specific function and its arguments.
    
    :param func_name: The name of the function
    :param args: The positional arguments
    :param kwargs: The keyword arguments
    :return: True if cache key is successfully deleted, False otherwise
    """
    cache_key = generate_cache_key(func_name, *args, **kwargs)
    try:
        result = cache.delete(cache_key)
        if result:
            logging.info(f"Cache invalidated for {func_name} with key: {cache_key}")
            return True
        else:
            logging.info(f"No cache to invalidate for {func_name} with key: {cache_key}")
            return False
    except redis.RedisError as e:
        logging.error(f"Error invalidating cache for {func_name}: {e}")
        return False

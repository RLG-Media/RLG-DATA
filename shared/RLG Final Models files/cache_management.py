import time
from typing import Any, Callable, Optional, Dict
from cachetools import LRUCache, TTLCache

class CacheManager:
    """
    A class for managing in-memory caching with support for multiple cache types.
    """

    def __init__(self, cache_type: str = "ttl", max_size: int = 100, ttl: int = 300):
        """
        Initialize the CacheManager.

        Args:
            cache_type: Type of cache ("ttl" for time-to-live, "lru" for least recently used).
            max_size: Maximum size of the cache.
            ttl: Time-to-live for cached items (only applicable for "ttl" cache type).
        """
        if cache_type == "ttl":
            self.cache = TTLCache(maxsize=max_size, ttl=ttl)
        elif cache_type == "lru":
            self.cache = LRUCache(maxsize=max_size)
        else:
            raise ValueError("Invalid cache type. Supported types are 'ttl' and 'lru'.")

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache.

        Args:
            key: Key to retrieve.

        Returns:
            Cached value or None if the key is not found.
        """
        return self.cache.get(key)

    def set(self, key: str, value: Any) -> None:
        """
        Store a value in the cache.

        Args:
            key: Key for the value.
            value: Value to cache.
        """
        self.cache[key] = value

    def delete(self, key: str) -> None:
        """
        Remove a key from the cache.

        Args:
            key: Key to remove.
        """
        if key in self.cache:
            del self.cache[key]

    def clear(self) -> None:
        """
        Clear the entire cache.
        """
        self.cache.clear()

    def size(self) -> int:
        """
        Get the current size of the cache.

        Returns:
            Number of items in the cache.
        """
        return len(self.cache)

    def contains(self, key: str) -> bool:
        """
        Check if a key exists in the cache.

        Args:
            key: Key to check.

        Returns:
            True if the key exists, False otherwise.
        """
        return key in self.cache


class CacheDecorator:
    """
    A class providing a caching decorator for functions.
    """

    def __init__(self, cache_manager: CacheManager):
        """
        Initialize the CacheDecorator.

        Args:
            cache_manager: Instance of CacheManager to use for caching.
        """
        self.cache_manager = cache_manager

    def cache(self, key_func: Callable[..., str]):
        """
        Decorator to cache the results of a function.

        Args:
            key_func: Function to generate cache keys from arguments.

        Returns:
            Wrapped function with caching applied.
        """

        def decorator(func: Callable):
            def wrapper(*args, **kwargs):
                cache_key = key_func(*args, **kwargs)
                if self.cache_manager.contains(cache_key):
                    return self.cache_manager.get(cache_key)

                result = func(*args, **kwargs)
                self.cache_manager.set(cache_key, result)
                return result

            return wrapper

        return decorator


# Example Usage
if __name__ == "__main__":
    # Initialize a TTL cache
    cache_manager = CacheManager(cache_type="ttl", max_size=50, ttl=600)

    # Function to generate cache keys based on arguments
    def generate_key(*args, **kwargs):
        return f"key_{args}_{kwargs}"

    # Apply caching to a function
    @CacheDecorator(cache_manager).cache(key_func=generate_key)
    def slow_function(x, y):
        time.sleep(2)  # Simulate a slow computation
        return x + y

    # Test the caching mechanism
    print("First call (uncached):", slow_function(1, 2))
    print("Second call (cached):", slow_function(1, 2))

    # Cache management
    print("Cache contains 'key_1_2':", cache_manager.contains("key_1_2"))
    print("Cache size:", cache_manager.size())
    cache_manager.clear()
    print("Cache cleared. Current size:", cache_manager.size())

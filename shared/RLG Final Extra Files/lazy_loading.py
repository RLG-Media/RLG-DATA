import time
import logging
import asyncio
from functools import wraps
from collections import defaultdict
from threading import Lock

# Initialize logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Cache to store already loaded data, avoiding redundant database queries or heavy computations
cache = defaultdict(dict)
cache_lock = Lock()

# Simulate database fetching or heavy computation
async def fetch_data_from_db(data_id):
    """Simulate an asynchronous database query or computation."""
    logger.info(f"Fetching data for ID: {data_id}...")
    await asyncio.sleep(2)  # Simulate a delay in fetching data (e.g., DB query time)
    return {"data": f"Data for {data_id}", "id": data_id}

def lazy_load_data(func):
    """Decorator to implement lazy loading."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        data_id = args[0]  # Assuming the first argument is the data identifier (e.g., `data_id`)

        # Check if data is already cached
        with cache_lock:
            if data_id in cache:
                logger.info(f"Returning cached data for ID: {data_id}")
                return cache[data_id]

        # Fetch data if not cached
        logger.info(f"Data not cached. Fetching data for ID: {data_id}")
        data = await func(*args, **kwargs)

        # Cache the data for future use
        with cache_lock:
            cache[data_id] = data
            logger.info(f"Data for ID: {data_id} cached successfully.")
        
        return data
    return wrapper

class LazyLoader:
    """Class for implementing lazy loading functionality for both RLG Data and RLG Fans."""

    def __init__(self):
        self.data = {}

    @lazy_load_data
    async def load_data(self, data_id):
        """Load data with lazy loading. Data will be fetched from the database or API when needed."""
        return await fetch_data_from_db(data_id)

    async def get_data(self, data_id):
        """Get data, either from the cache or by fetching it."""
        # Check the cache first, then fetch if necessary
        data = await self.load_data(data_id)
        return data

    async def get_multiple_data(self, data_ids):
        """Fetch multiple pieces of data asynchronously, using lazy loading for each."""
        tasks = [self.get_data(data_id) for data_id in data_ids]
        return await asyncio.gather(*tasks)

    def clear_cache(self):
        """Clear the cached data."""
        with cache_lock:
            cache.clear()
        logger.info("Cache cleared.")

    def get_cache(self):
        """Retrieve the cached data."""
        return cache

# Example of a simulated cache key eviction based on memory/size limits
def simulate_cache_eviction():
    """Simulate cache eviction when cache exceeds a certain size."""
    max_cache_size = 5  # Define a max size for the cache
    if len(cache) > max_cache_size:
        # Evict the first item (FIFO eviction)
        evicted_key = list(cache.keys())[0]
        del cache[evicted_key]
        logger.info(f"Cache eviction triggered. Removed key: {evicted_key}")

async def main():
    """Main function to demonstrate lazy loading."""
    lazy_loader = LazyLoader()

    # Simulating data load requests
    data_ids = [1, 2, 3, 4, 5, 6, 1]  # Notice the duplicate ID to demonstrate caching
    results = await lazy_loader.get_multiple_data(data_ids)

    # Output the results of lazy loading
    for result in results:
        logger.info(f"Loaded: {result}")

    # Cache stats after loading
    logger.info(f"Cache after loading: {lazy_loader.get_cache()}")

    # Simulate a cache eviction scenario
    simulate_cache_eviction()
    logger.info(f"Cache after eviction: {lazy_loader.get_cache()}")

    # Clear the cache
    lazy_loader.clear_cache()
    logger.info(f"Cache after clearing: {lazy_loader.get_cache()}")

if __name__ == "__main__":
    # Run the main async function
    asyncio.run(main())

import time
import threading
from collections import defaultdict, deque
from typing import Dict, List, Optional

class APIThrottlingManager:
    """
    API Throttling Manager for managing rate limits across multiple platforms.
    Supports RLG Data and RLG Fans, ensuring requests stay within rate limits.
    """

    def __init__(self):
        self.rate_limits = defaultdict(lambda: {"limit": 0, "window": 0, "queue": deque()})
        self.lock = threading.Lock()

    def configure_rate_limit(self, platform: str, limit: int, window: int):
        """
        Configure rate limits for a specific platform.

        Args:
            platform (str): Platform name (e.g., "twitter", "facebook").
            limit (int): Maximum number of requests allowed.
            window (int): Time window for the limit (in seconds).
        """
        with self.lock:
            self.rate_limits[platform]["limit"] = limit
            self.rate_limits[platform]["window"] = window

    def is_request_allowed(self, platform: str) -> bool:
        """
        Check if a request is allowed under the current rate limit for the platform.

        Args:
            platform (str): Platform name.

        Returns:
            bool: True if the request is allowed, False otherwise.
        """
        with self.lock:
            if platform not in self.rate_limits:
                raise ValueError(f"Rate limit for platform '{platform}' is not configured.")

            current_time = time.time()
            request_queue = self.rate_limits[platform]["queue"]
            limit = self.rate_limits[platform]["limit"]
            window = self.rate_limits[platform]["window"]

            # Remove expired requests from the queue
            while request_queue and current_time - request_queue[0] > window:
                request_queue.popleft()

            # Check if the request is within the rate limit
            if len(request_queue) < limit:
                request_queue.append(current_time)
                return True

            return False

    def wait_and_execute(self, platform: str, func, *args, **kwargs):
        """
        Wait until the request is allowed and execute the given function.

        Args:
            platform (str): Platform name.
            func (callable): Function to execute.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            Any: Result of the executed function.
        """
        while not self.is_request_allowed(platform):
            time.sleep(0.1)  # Wait before retrying

        return func(*args, **kwargs)

    def batch_request_handler(self, platform: str, requests: List[callable], delay: Optional[float] = None):
        """
        Handle a batch of requests, ensuring compliance with rate limits.

        Args:
            platform (str): Platform name.
            requests (List[callable]): List of callable request functions.
            delay (float, optional): Delay between consecutive requests (in seconds).

        Returns:
            List: Results of executed requests.
        """
        results = []
        for request in requests:
            self.wait_and_execute(platform, request)
            results.append(request())
            if delay:
                time.sleep(delay)

        return results

# Example usage
if __name__ == "__main__":
    throttling_manager = APIThrottlingManager()

    # Configure rate limits for platforms
    throttling_manager.configure_rate_limit("twitter", limit=300, window=900)  # 300 requests per 15 minutes
    throttling_manager.configure_rate_limit("facebook", limit=200, window=600)  # 200 requests per 10 minutes

    def example_api_request():
        print("Request executed at", time.strftime("%Y-%m-%d %H:%M:%S"))

    # Simulate requests
    for _ in range(10):
        if throttling_manager.is_request_allowed("twitter"):
            throttling_manager.wait_and_execute("twitter", example_api_request)

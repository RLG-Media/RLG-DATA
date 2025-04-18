import time
from collections import defaultdict, deque
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("api_rate_limit_manager.log"), logging.StreamHandler()]
)

class APIRateLimitManager:
    """
    Manages API rate limits for multiple users or API keys using various algorithms.
    """

    def __init__(self, default_limit=100, window_duration=60, algorithm="sliding_window"):
        """
        Initialize the rate limit manager.
        :param default_limit: Default number of requests allowed per window.
        :param window_duration: Duration of the time window in seconds.
        :param algorithm: Algorithm to use for rate limiting ('fixed_window', 'sliding_window', 'token_bucket').
        """
        self.default_limit = default_limit
        self.window_duration = window_duration
        self.algorithm = algorithm
        self.usage = defaultdict(deque)  # Tracks requests for sliding window
        self.token_buckets = defaultdict(lambda: self.default_limit)  # Token bucket capacity
        self.last_refill = defaultdict(lambda: time.time())  # Token bucket refill timestamps
        logging.info("APIRateLimitManager initialized.")

    def is_request_allowed(self, user_key):
        """
        Check if a request is allowed for a given user or API key.
        :param user_key: Unique identifier for the user or API key.
        :return: True if the request is allowed, False otherwise.
        """
        if self.algorithm == "fixed_window":
            return self._fixed_window(user_key)
        elif self.algorithm == "sliding_window":
            return self._sliding_window(user_key)
        elif self.algorithm == "token_bucket":
            return self._token_bucket(user_key)
        else:
            logging.error(f"Unknown algorithm: {self.algorithm}")
            return False

    def _fixed_window(self, user_key):
        """
        Fixed window rate limiting.
        :param user_key: Unique identifier for the user or API key.
        :return: True if the request is allowed, False otherwise.
        """
        current_time = int(time.time() / self.window_duration)
        if user_key not in self.usage or self.usage[user_key]["window"] != current_time:
            self.usage[user_key] = {"window": current_time, "count": 0}
        if self.usage[user_key]["count"] < self.default_limit:
            self.usage[user_key]["count"] += 1
            return True
        return False

    def _sliding_window(self, user_key):
        """
        Sliding window rate limiting.
        :param user_key: Unique identifier for the user or API key.
        :return: True if the request is allowed, False otherwise.
        """
        current_time = time.time()
        window_start = current_time - self.window_duration

        # Remove outdated requests
        while self.usage[user_key] and self.usage[user_key][0] < window_start:
            self.usage[user_key].popleft()

        if len(self.usage[user_key]) < self.default_limit:
            self.usage[user_key].append(current_time)
            return True
        return False

    def _token_bucket(self, user_key):
        """
        Token bucket rate limiting.
        :param user_key: Unique identifier for the user or API key.
        :return: True if the request is allowed, False otherwise.
        """
        current_time = time.time()
        elapsed_time = current_time - self.last_refill[user_key]
        refill_tokens = int(elapsed_time * (self.default_limit / self.window_duration))

        # Refill tokens based on elapsed time
        self.token_buckets[user_key] = min(
            self.default_limit, self.token_buckets[user_key] + refill_tokens
        )
        self.last_refill[user_key] = current_time

        if self.token_buckets[user_key] > 0:
            self.token_buckets[user_key] -= 1
            return True
        return False

    def reset_limit(self, user_key):
        """
        Reset the rate limit for a specific user or API key.
        :param user_key: Unique identifier for the user or API key.
        """
        if user_key in self.usage:
            del self.usage[user_key]
        if user_key in self.token_buckets:
            self.token_buckets[user_key] = self.default_limit
        logging.info(f"Rate limit reset for user: {user_key}")

    def set_limit(self, user_key, limit):
        """
        Set a custom rate limit for a specific user or API key.
        :param user_key: Unique identifier for the user or API key.
        :param limit: Custom limit for the user.
        """
        self.default_limit = limit
        self.reset_limit(user_key)
        logging.info(f"Custom rate limit set for user: {user_key}")

    def log_usage(self):
        """
        Log the current rate limit usage for all users.
        """
        for user_key, usage_data in self.usage.items():
            logging.info(f"User {user_key}: {len(usage_data)} requests in the current window.")
        for user_key, tokens in self.token_buckets.items():
            logging.info(f"User {user_key}: {tokens} tokens remaining.")

# Example Usage
if __name__ == "__main__":
    rate_limiter = APIRateLimitManager(default_limit=5, window_duration=10, algorithm="sliding_window")

    user = "user_123"
    for i in range(10):
        if rate_limiter.is_request_allowed(user):
            print(f"Request {i+1}: Allowed")
        else:
            print(f"Request {i+1}: Denied")
        time.sleep(1)  # Simulate 1-second intervals between requests

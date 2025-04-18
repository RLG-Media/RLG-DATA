import asyncio
import aiohttp
import time
import logging
import random
from statistics import mean
from concurrent.futures import ThreadPoolExecutor

# Initialize logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Configurable parameters for load testing
LOAD_TEST_CONFIG = {
    "url": "https://example.com/api",  # API endpoint to test
    "concurrent_users": 100,           # Number of concurrent users to simulate
    "requests_per_user": 10,           # Number of requests each user will make
    "timeout": 5,                      # Timeout for each request in seconds
    "rate_limit": 5,                   # Rate limit for requests per second (requests per second per user)
}

class LoadTester:
    """Class to handle load testing tasks."""

    def __init__(self, config):
        self.config = config
        self.session = None
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.latencies = []

    async def make_request(self, session, url):
        """Perform a single HTTP request."""
        try:
            start_time = time.time()
            async with session.get(url, timeout=self.config['timeout']) as response:
                end_time = time.time()
                latency = end_time - start_time
                self.latencies.append(latency)

                if response.status == 200:
                    self.successful_requests += 1
                else:
                    self.failed_requests += 1

                self.total_requests += 1
                return latency, response.status
        except Exception as e:
            self.failed_requests += 1
            logger.error(f"Request failed: {e}")
            return None, None

    async def user_load(self, user_id):
        """Simulate a user making multiple requests."""
        async with aiohttp.ClientSession() as session:
            for _ in range(self.config['requests_per_user']):
                latency, status = await self.make_request(session, self.config['url'])
                if latency is not None:
                    logger.info(f"User {user_id} - Request finished in {latency:.2f}s with status {status}")

    async def start_load_test(self):
        """Start the load test by simulating multiple users."""
        logger.info(f"Starting load test with {self.config['concurrent_users']} concurrent users.")
        tasks = []
        for user_id in range(self.config['concurrent_users']):
            tasks.append(self.user_load(user_id))

        start_time = time.time()
        await asyncio.gather(*tasks)
        end_time = time.time()

        total_time = end_time - start_time
        logger.info(f"Load test completed in {total_time:.2f}s.")
        self.report_metrics(total_time)

    def report_metrics(self, total_time):
        """Generate and report performance metrics."""
        if self.latencies:
            avg_latency = mean(self.latencies)
            max_latency = max(self.latencies)
            min_latency = min(self.latencies)
            throughput = self.total_requests / total_time
        else:
            avg_latency = max_latency = min_latency = throughput = 0

        success_rate = (self.successful_requests / self.total_requests) * 100 if self.total_requests else 0
        failure_rate = (self.failed_requests / self.total_requests) * 100 if self.total_requests else 0

        logger.info("Performance Metrics:")
        logger.info(f"Total Requests: {self.total_requests}")
        logger.info(f"Successful Requests: {self.successful_requests}")
        logger.info(f"Failed Requests: {self.failed_requests}")
        logger.info(f"Average Latency: {avg_latency:.2f}s")
        logger.info(f"Max Latency: {max_latency:.2f}s")
        logger.info(f"Min Latency: {min_latency:.2f}s")
        logger.info(f"Throughput (requests/sec): {throughput:.2f}")
        logger.info(f"Success Rate: {success_rate:.2f}%")
        logger.info(f"Failure Rate: {failure_rate:.2f}%")

    def stress_test(self):
        """Run stress testing beyond normal traffic conditions."""
        # Increase number of users and requests per user for stress testing
        self.config['concurrent_users'] = 500
        self.config['requests_per_user'] = 50
        asyncio.run(self.start_load_test())

    def run(self):
        """Execute the load test with the current configuration."""
        asyncio.run(self.start_load_test())

# Example of running the load tester with the above configuration
if __name__ == "__main__":
    load_tester = LoadTester(LOAD_TEST_CONFIG)
    load_tester.run()

    # Optional: Trigger a stress test if needed (this will stress the system beyond normal operation)
    # load_tester.stress_test()

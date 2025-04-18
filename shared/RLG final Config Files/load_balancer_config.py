import random
import time
import logging
from collections import defaultdict
from threading import Lock
from config import LOAD_BALANCER_CONFIG
from health_check import check_server_health

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class LoadBalancer:
    """Smart Load Balancer for RLG Data and RLG Fans, ensuring efficient traffic distribution."""

    def __init__(self):
        self.servers = LOAD_BALANCER_CONFIG.get("servers", [])
        self.server_status = {server: "healthy" for server in self.servers}
        self.request_count = defaultdict(int)
        self.lock = Lock()
        self.balancing_strategy = LOAD_BALANCER_CONFIG.get("strategy", "round_robin")
        self.current_index = 0  # For round-robin strategy

    def get_best_server(self, user_region=None):
        """Selects the best available server based on the chosen load balancing strategy."""
        with self.lock:
            healthy_servers = [s for s in self.servers if self.server_status[s] == "healthy"]

            if not healthy_servers:
                logging.error("No available servers. All are down!")
                return None

            if self.balancing_strategy == "round_robin":
                server = healthy_servers[self.current_index % len(healthy_servers)]
                self.current_index += 1

            elif self.balancing_strategy == "least_connections":
                server = min(healthy_servers, key=lambda s: self.request_count[s])

            elif self.balancing_strategy == "region_based" and user_region:
                region_servers = [s for s in healthy_servers if user_region in s]
                if region_servers:
                    server = random.choice(region_servers)
                else:
                    server = random.choice(healthy_servers)

            elif self.balancing_strategy == "adaptive_ai":
                server = self._adaptive_ai_routing(healthy_servers)

            else:
                server = random.choice(healthy_servers)

            self.request_count[server] += 1
            return server

    def _adaptive_ai_routing(self, healthy_servers):
        """Implements AI-based adaptive balancing considering server load, region, and past performance."""
        # Simulate AI decision-making based on request history and performance
        weighted_servers = sorted(
            healthy_servers,
            key=lambda s: (self.request_count[s], random.random())  # Sort by least requests with some randomness
        )
        return weighted_servers[0]

    def release_server(self, server):
        """Releases a server after handling a request."""
        if server in self.request_count:
            self.request_count[server] = max(0, self.request_count[server] - 1)

    def perform_health_check(self):
        """Regularly checks the health of all servers and updates their status."""
        for server in self.servers:
            is_healthy = check_server_health(server)
            self.server_status[server] = "healthy" if is_healthy else "unhealthy"
            logging.info(f"Server {server} is now {self.server_status[server]}.")

    def add_server(self, server):
        """Dynamically adds a new server to the pool."""
        with self.lock:
            if server not in self.servers:
                self.servers.append(server)
                self.server_status[server] = "healthy"
                logging.info(f"Added new server: {server}")

    def remove_server(self, server):
        """Removes a server from the pool."""
        with self.lock:
            if server in self.servers:
                self.servers.remove(server)
                self.server_status.pop(server, None)
                self.request_count.pop(server, None)
                logging.warning(f"Removed server: {server}")

# Example Usage
if __name__ == "__main__":
    load_balancer = LoadBalancer()

    user_request_region = "US-East"
    selected_server = load_balancer.get_best_server(user_request_region)

    if selected_server:
        logging.info(f"Routing request to {selected_server}")
        time.sleep(1)  # Simulate request handling
        load_balancer.release_server(selected_server)
    else:
        logging.error("No available servers to handle request.")

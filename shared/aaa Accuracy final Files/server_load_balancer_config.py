import os
import logging
from typing import List, Dict, Optional
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("load_balancer.log"),
        logging.StreamHandler()
    ]
)

class LoadBalancerConfig:
    """
    Configuration and management for server load balancing in RLG Data and RLG Fans.
    Supports auto-scaling, health checks, and dynamic traffic routing.
    """

    def __init__(self):
        self.servers: List[Dict] = []  # List of servers with their configurations
        self.health_check_endpoint = "/health"  # Default health check endpoint
        self.scaling_threshold = {
            "cpu": 80,  # Percentage
            "memory": 75  # Percentage
        }
        self.scaling_enabled = True
        logging.info("LoadBalancerConfig initialized.")

    def add_server(self, server_id: str, server_url: str):
        """
        Add a server to the load balancer.

        Args:
            server_id (str): Unique identifier for the server.
            server_url (str): URL of the server.
        """
        self.servers.append({
            "id": server_id,
            "url": server_url,
            "status": "healthy"
        })
        logging.info("Server added: %s (%s)", server_id, server_url)

    def remove_server(self, server_id: str):
        """
        Remove a server from the load balancer by its ID.

        Args:
            server_id (str): Unique identifier for the server.
        """
        self.servers = [s for s in self.servers if s["id"] != server_id]
        logging.info("Server removed: %s", server_id)

    def check_server_health(self):
        """
        Perform health checks on all servers in the load balancer.
        """
        for server in self.servers:
            try:
                response = requests.get(server["url"] + self.health_check_endpoint, timeout=5)
                if response.status_code == 200:
                    server["status"] = "healthy"
                else:
                    server["status"] = "unhealthy"
                logging.info("Health check for %s: %s", server["id"], server["status"])
            except Exception as e:
                server["status"] = "unhealthy"
                logging.error("Health check failed for %s: %s", server["id"], e)

    def route_request(self, request_data: Dict) -> Optional[str]:
        """
        Route a request to the healthiest available server.

        Args:
            request_data (Dict): Data about the incoming request.

        Returns:
            Optional[str]: URL of the server that will handle the request or None if no server is available.
        """
        healthy_servers = [s for s in self.servers if s["status"] == "healthy"]
        if not healthy_servers:
            logging.error("No healthy servers available.")
            return None

        # Basic round-robin routing for simplicity
        selected_server = healthy_servers[0]
        self.servers.append(self.servers.pop(0))  # Rotate the list
        logging.info("Request routed to server: %s (%s)", selected_server["id"], selected_server["url"])
        return selected_server["url"]

    def auto_scale(self, server_metrics: List[Dict]):
        """
        Automatically scale servers based on metrics like CPU and memory usage.

        Args:
            server_metrics (List[Dict]): List of server metrics containing `id`, `cpu_usage`, and `memory_usage`.
        """
        if not self.scaling_enabled:
            logging.info("Auto-scaling is disabled.")
            return

        for metrics in server_metrics:
            if metrics["cpu_usage"] > self.scaling_threshold["cpu"] or metrics["memory_usage"] > self.scaling_threshold["memory"]:
                logging.warning(
                    "Server %s exceeds scaling thresholds: CPU=%d%%, Memory=%d%%",
                    metrics["id"], metrics["cpu_usage"], metrics["memory_usage"]
                )
                self.add_additional_capacity(metrics["id"])

    def add_additional_capacity(self, server_id: str):
        """
        Add additional capacity (e.g., spin up a new server) when a server exceeds thresholds.

        Args:
            server_id (str): The server ID that triggered the scaling.
        """
        new_server_id = f"{server_id}-scaled-{len(self.servers) + 1}"
        new_server_url = f"https://new-instance-{len(self.servers) + 1}.example.com"
        self.add_server(new_server_id, new_server_url)
        logging.info("Additional capacity added: %s (%s)", new_server_id, new_server_url)

    def display_servers(self):
        """
        Display the list of servers and their health statuses.
        """
        logging.info("Current servers:")
        for server in self.servers:
            logging.info("ID: %s, URL: %s, Status: %s", server["id"], server["url"], server["status"])

# Example Usage
if __name__ == "__main__":
    lb = LoadBalancerConfig()
    lb.add_server("server1", "https://server1.example.com")
    lb.add_server("server2", "https://server2.example.com")
    lb.check_server_health()
    lb.route_request({"path": "/api/data"})
    lb.auto_scale([
        {"id": "server1", "cpu_usage": 85, "memory_usage": 70},
        {"id": "server2", "cpu_usage": 65, "memory_usage": 60}
    ])
    lb.display_servers()

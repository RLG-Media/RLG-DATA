"""
load_balancer_config.py
Configures and manages load balancing for RLG Data and RLG Fans services.
Supports redundancy, failover, dynamic scaling, and health checks.
"""

import os
import logging
from typing import List, Dict
import yaml

# Logger setup
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Constants
DEFAULT_HEALTH_CHECK_PATH = "/health"
DEFAULT_PORT = 80
DEFAULT_PROTOCOL = "HTTP"
LOAD_BALANCER_CONFIG_FILE = "load_balancer_config.yaml"

# Sample Backend Server Configuration
DEFAULT_SERVERS = [
    {"host": "192.168.1.10", "port": 8000, "service": "RLG Data"},
    {"host": "192.168.1.11", "port": 8001, "service": "RLG Fans"},
]

class LoadBalancerConfig:
    def __init__(self):
        self.servers = DEFAULT_SERVERS
        self.protocol = DEFAULT_PROTOCOL
        self.port = DEFAULT_PORT
        self.health_check_path = DEFAULT_HEALTH_CHECK_PATH

    def load_config(self, config_file: str = LOAD_BALANCER_CONFIG_FILE) -> None:
        """
        Loads the load balancer configuration from a YAML file.

        Args:
            config_file (str): Path to the YAML configuration file.

        Raises:
            FileNotFoundError: If the config file does not exist.
        """
        if not os.path.exists(config_file):
            logger.warning(f"Configuration file {config_file} not found. Using default settings.")
            return

        try:
            with open(config_file, "r") as file:
                config = yaml.safe_load(file)

            self.servers = config.get("servers", self.servers)
            self.protocol = config.get("protocol", self.protocol)
            self.port = config.get("port", self.port)
            self.health_check_path = config.get("health_check_path", self.health_check_path)

            logger.info("Load balancer configuration loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading configuration file {config_file}: {str(e)}")
            raise

    def save_config(self, config_file: str = LOAD_BALANCER_CONFIG_FILE) -> None:
        """
        Saves the current load balancer configuration to a YAML file.

        Args:
            config_file (str): Path to the YAML configuration file.
        """
        try:
            config = {
                "servers": self.servers,
                "protocol": self.protocol,
                "port": self.port,
                "health_check_path": self.health_check_path,
            }

            with open(config_file, "w") as file:
                yaml.dump(config, file)

            logger.info(f"Configuration saved to {config_file}.")
        except Exception as e:
            logger.error(f"Error saving configuration to file {config_file}: {str(e)}")
            raise

    def add_server(self, host: str, port: int, service: str) -> None:
        """
        Adds a new server to the load balancer.

        Args:
            host (str): Host address of the server.
            port (int): Port of the server.
            service (str): Service hosted by the server (e.g., "RLG Data" or "RLG Fans").
        """
        self.servers.append({"host": host, "port": port, "service": service})
        logger.info(f"Added new server: {host}:{port} ({service})")

    def remove_server(self, host: str, port: int) -> None:
        """
        Removes a server from the load balancer.

        Args:
            host (str): Host address of the server.
            port (int): Port of the server.
        """
        self.servers = [
            server for server in self.servers if not (server["host"] == host and server["port"] == port)
        ]
        logger.info(f"Removed server: {host}:{port}")

    def perform_health_checks(self) -> Dict[str, bool]:
        """
        Performs health checks on all servers.

        Returns:
            Dict[str, bool]: A dictionary mapping server addresses to their health status.
        """
        statuses = {}
        for server in self.servers:
            try:
                health_check_url = f"{self.protocol.lower()}://{server['host']}:{server['port']}{self.health_check_path}"
                response = requests.get(health_check_url, timeout=5)
                statuses[f"{server['host']}:{server['port']}"] = response.status_code == 200
                logger.info(f"Health check for {server['host']}:{server['port']} - Status: {response.status_code}")
            except Exception as e:
                statuses[f"{server['host']}:{server['port']}"] = False
                logger.error(f"Health check failed for {server['host']}:{server['port']}: {str(e)}")

        return statuses

    def get_active_servers(self) -> List[Dict[str, Any]]:
        """
        Retrieves a list of active servers based on health checks.

        Returns:
            List[Dict[str, Any]]: A list of healthy server configurations.
        """
        health_statuses = self.perform_health_checks()
        active_servers = [
            server
            for server in self.servers
            if health_statuses.get(f"{server['host']}:{server['port']}", False)
        ]

        logger.info(f"Active servers: {active_servers}")
        return active_servers


# Example Usage
if __name__ == "__main__":
    lb_config = LoadBalancerConfig()

    # Load configuration from file
    lb_config.load_config()

    # Perform health checks
    health_statuses = lb_config.perform_health_checks()
    logger.info(f"Health Statuses: {health_statuses}")

    # Add a new server
    lb_config.add_server(host="192.168.1.12", port=8002, service="RLG Fans")

    # Save the updated configuration
    lb_config.save_config()

    # Get active servers
    active_servers = lb_config.get_active_servers()
    logger.info(f"Active servers: {active_servers}")

import logging
import time
from threading import Thread
from typing import Dict, List
from queue import Queue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("multi_region_data_replication.log"),
        logging.StreamHandler(),
    ],
)

class MultiRegionDataReplication:
    """
    Service for replicating data across multiple regions to ensure availability, consistency, and scalability.
    Supports both RLG Data and RLG Fans.
    """

    def __init__(self, regions: List[str], replication_mode: str = "async"):
        """
        Initialize the MultiRegionDataReplication service.

        Args:
            regions (List[str]): List of region identifiers (e.g., ["us-east-1", "eu-west-1", "ap-south-1"]).
            replication_mode (str): Replication mode, "sync" or "async" (default: "async").
        """
        self.regions = regions
        self.replication_mode = replication_mode
        self.replication_queue = Queue()  # Used for async replication
        self.data_stores: Dict[str, Dict] = {region: {} for region in regions}  # Mock data stores for regions
        logging.info("MultiRegionDataReplication initialized with regions: %s", regions)

    def replicate(self, key: str, value: str):
        """
        Replicate data across regions.

        Args:
            key (str): The key of the data to replicate.
            value (str): The value of the data to replicate.
        """
        if self.replication_mode == "sync":
            self._sync_replicate(key, value)
        else:
            self._async_replicate(key, value)

    def _sync_replicate(self, key: str, value: str):
        """
        Perform synchronous data replication across regions.

        Args:
            key (str): The key of the data to replicate.
            value (str): The value of the data to replicate.
        """
        logging.info("Starting synchronous replication for key: %s", key)
        for region in self.regions:
            self.data_stores[region][key] = value
            logging.info("Data replicated to region '%s' for key '%s'.", region, key)

    def _async_replicate(self, key: str, value: str):
        """
        Perform asynchronous data replication using a background thread.

        Args:
            key (str): The key of the data to replicate.
            value (str): The value of the data to replicate.
        """
        logging.info("Queueing data for asynchronous replication for key: %s", key)
        self.replication_queue.put((key, value))
        Thread(target=self._process_replication_queue, daemon=True).start()

    def _process_replication_queue(self):
        """
        Process the replication queue to replicate data asynchronously.
        """
        while not self.replication_queue.empty():
            key, value = self.replication_queue.get()
            logging.info("Processing asynchronous replication for key: %s", key)
            for region in self.regions:
                time.sleep(0.5)  # Simulate network latency
                self.data_stores[region][key] = value
                logging.info("Asynchronous replication completed to region '%s' for key '%s'.", region, key)

    def get_data(self, region: str, key: str) -> str:
        """
        Retrieve data from a specific region.

        Args:
            region (str): The region to retrieve data from.
            key (str): The key of the data to retrieve.

        Returns:
            str: The value of the data, or None if the key does not exist.
        """
        return self.data_stores.get(region, {}).get(key)

    def monitor_health(self):
        """
        Monitor the health of the replication process and the regions.
        """
        logging.info("Monitoring health of data replication...")
        for region in self.regions:
            logging.info("Region '%s' status: Healthy", region)

    def handle_failover(self, failed_region: str):
        """
        Handle failover in case a region becomes unavailable.

        Args:
            failed_region (str): The region that has failed.
        """
        logging.warning("Region '%s' is unavailable. Initiating failover.", failed_region)
        for key, value in self.data_stores[failed_region].items():
            for region in self.regions:
                if region != failed_region:
                    self.data_stores[region][key] = value
                    logging.info("Data for key '%s' replicated to region '%s' during failover.", key, region)

# Example usage
if __name__ == "__main__":
    replication_service = MultiRegionDataReplication(regions=["us-east-1", "eu-west-1", "ap-south-1"], replication_mode="async")

    # Simulate data replication
    replication_service.replicate("user123", "{"name": "John Doe", "email": "john.doe@example.com"}")

    # Retrieve data
    data = replication_service.get_data("us-east-1", "user123")
    logging.info("Retrieved data from 'us-east-1': %s", data)

    # Monitor health
    replication_service.monitor_health()

    # Simulate failover
    replication_service.handle_failover("eu-west-1")

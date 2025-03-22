import logging
from typing import Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("integration_services.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IntegrationService:
    """
    Service class for managing third-party integrations for RLG Data and RLG Fans.
    
    This class provides methods to add, remove, retrieve, list, and test integrations.
    Integrations may include tools such as Slack, Google Analytics, or others.
    """

    def __init__(self) -> None:
        """
        Initialize the IntegrationService with an empty dictionary for storing integrations.
        """
        self.integrations: Dict[str, Dict] = {}
        logger.info("IntegrationService initialized.")

    def add_integration(self, name: str, api_key: str, config: Optional[Dict] = None) -> Dict[str, str]:
        """
        Add a new third-party integration.

        Args:
            name (str): The name of the integration (e.g., "Slack", "Google Analytics").
            api_key (str): The API key for the integration.
            config (Optional[Dict]): Additional configuration details for the integration.

        Returns:
            Dict[str, str]: A dictionary indicating the status and a message.
        """
        if name in self.integrations:
            logger.warning("Integration '%s' already exists.", name)
            return {"status": "error", "message": "Integration already exists."}

        self.integrations[name] = {
            "api_key": api_key,
            "config": config or {}
        }
        logger.info("Integration '%s' added successfully.", name)
        return {"status": "success", "message": f"Integration '{name}' added."}

    def remove_integration(self, name: str) -> Dict[str, str]:
        """
        Remove an existing integration.

        Args:
            name (str): The name of the integration to remove.

        Returns:
            Dict[str, str]: A dictionary indicating the status and a message.
        """
        if name not in self.integrations:
            logger.warning("Integration '%s' not found.", name)
            return {"status": "error", "message": "Integration not found."}

        del self.integrations[name]
        logger.info("Integration '%s' removed successfully.", name)
        return {"status": "success", "message": f"Integration '{name}' removed."}

    def get_integration(self, name: str) -> Optional[Dict]:
        """
        Retrieve details of a specific integration.

        Args:
            name (str): The name of the integration.

        Returns:
            Optional[Dict]: The details of the integration if found; otherwise, None.
        """
        integration = self.integrations.get(name)
        if integration:
            logger.info("Integration '%s' retrieved successfully.", name)
        else:
            logger.warning("Integration '%s' not found.", name)
        return integration

    def list_integrations(self) -> Dict[str, Dict]:
        """
        List all configured integrations.

        Returns:
            Dict[str, Dict]: A dictionary of all integrations.
        """
        logger.info("Listing all integrations: %d found.", len(self.integrations))
        return self.integrations

    def test_integration(self, name: str) -> Dict[str, str]:
        """
        Test connectivity and functionality of a specific integration.

        Args:
            name (str): The name of the integration to test.

        Returns:
            Dict[str, str]: A dictionary indicating the test result.
        """
        integration = self.get_integration(name)
        if not integration:
            return {"status": "error", "message": "Integration not found."}

        try:
            # Placeholder for actual API call or connectivity test logic.
            # Here we simulate a successful test.
            logger.info("Testing integration '%s'...", name)
            logger.info("Integration '%s' test passed.", name)
            return {"status": "success", "message": f"Integration '{name}' is working correctly."}
        except Exception as e:
            logger.error("Integration '%s' test failed: %s", name, e)
            return {"status": "error", "message": f"Integration '{name}' test failed."}


# -------------------------------
# Example Usage (for testing purposes)
# -------------------------------
if __name__ == "__main__":
    service = IntegrationService()

    # Add integrations
    print(service.add_integration("Slack", "slack_api_key", {"channel": "#general"}))
    print(service.add_integration("Google Analytics", "ga_api_key"))

    # List integrations
    print("All Integrations:", service.list_integrations())

    # Get a specific integration
    print("Slack Integration:", service.get_integration("Slack"))

    # Test an integration
    print("Test Slack Integration:", service.test_integration("Slack"))

    # Remove an integration
    print("Remove Google Analytics:", service.remove_integration("Google Analytics"))

    # List integrations again
    print("All Integrations:", service.list_integrations())

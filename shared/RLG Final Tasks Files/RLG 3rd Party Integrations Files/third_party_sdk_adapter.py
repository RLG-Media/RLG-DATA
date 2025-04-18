import logging
from typing import Any, Dict, List, Optional
from shared.utils import log_info, log_error, validate_response
from shared.config import SUPPORTED_PLATFORMS, THIRD_PARTY_API_KEYS, SDK_CONFIGS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/third_party_sdk_adapter.log"),
    ],
)


class ThirdPartySDKAdapter:
    """
    Adapter class for integrating with third-party SDKs across multiple platforms.
    """

    def __init__(self):
        """
        Initialize the adapter with platform configurations.
        """
        self.platform_configs = SDK_CONFIGS
        self.api_keys = THIRD_PARTY_API_KEYS
        log_info(f"ThirdPartySDKAdapter initialized with platforms: {list(SUPPORTED_PLATFORMS)}")

    def initialize_sdk(self, platform: str) -> Any:
        """
        Initialize the SDK for a specific platform.

        Args:
            platform: Name of the platform (e.g., Facebook, Twitter).

        Returns:
            The initialized SDK client or raises an exception.
        """
        if platform not in SUPPORTED_PLATFORMS:
            raise ValueError(f"Platform '{platform}' is not supported.")

        try:
            config = self.platform_configs.get(platform, {})
            sdk_class = config.get("sdk_class")
            api_key = self.api_keys.get(platform)
            if not sdk_class or not api_key:
                raise ValueError(f"Missing SDK class or API key for platform '{platform}'.")

            sdk_instance = sdk_class(api_key=api_key, **config.get("sdk_options", {}))
            log_info(f"Initialized SDK for platform: {platform}")
            return sdk_instance
        except Exception as e:
            log_error(f"Failed to initialize SDK for platform '{platform}': {e}")
            raise

    def fetch_data(self, platform: str, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Fetch data from a specific platform using its SDK.

        Args:
            platform: Name of the platform (e.g., Instagram, TikTok).
            endpoint: API endpoint or function to fetch data.
            params: Optional parameters for the request.

        Returns:
            The response data as a dictionary.
        """
        try:
            sdk = self.initialize_sdk(platform)
            if not hasattr(sdk, endpoint):
                raise AttributeError(f"SDK for '{platform}' does not have endpoint '{endpoint}'.")

            response = getattr(sdk, endpoint)(**(params or {}))
            if validate_response(response):
                log_info(f"Data fetched successfully from '{platform}' endpoint '{endpoint}'.")
                return response
            else:
                log_error(f"Invalid response from '{platform}' endpoint '{endpoint}': {response}")
                return {"error": "Invalid response received."}
        except Exception as e:
            log_error(f"Error fetching data from '{platform}': {e}")
            return {"error": str(e)}

    def post_data(self, platform: str, endpoint: str, payload: Dict) -> Dict:
        """
        Post data to a specific platform using its SDK.

        Args:
            platform: Name of the platform (e.g., LinkedIn, Threads).
            endpoint: API endpoint or function to post data.
            payload: The data to be posted.

        Returns:
            The response data as a dictionary.
        """
        try:
            sdk = self.initialize_sdk(platform)
            if not hasattr(sdk, endpoint):
                raise AttributeError(f"SDK for '{platform}' does not have endpoint '{endpoint}'.")

            response = getattr(sdk, endpoint)(**payload)
            if validate_response(response):
                log_info(f"Data posted successfully to '{platform}' endpoint '{endpoint}'.")
                return response
            else:
                log_error(f"Invalid response from '{platform}' endpoint '{endpoint}': {response}")
                return {"error": "Invalid response received."}
        except Exception as e:
            log_error(f"Error posting data to '{platform}': {e}")
            return {"error": str(e)}

    def list_supported_platforms(self) -> List[str]:
        """
        List all supported platforms for integration.

        Returns:
            A list of supported platform names.
        """
        return list(SUPPORTED_PLATFORMS)

    def health_check(self) -> Dict:
        """
        Perform a health check on all initialized SDKs.

        Returns:
            A dictionary summarizing the health status of each platform.
        """
        health_status = {}
        for platform in SUPPORTED_PLATFORMS:
            try:
                sdk = self.initialize_sdk(platform)
                health_status[platform] = {"status": "healthy"}
                log_info(f"Health check passed for platform '{platform}'.")
            except Exception as e:
                health_status[platform] = {"status": "unhealthy", "error": str(e)}
                log_error(f"Health check failed for platform '{platform}': {e}")
        return health_status


# Example Usage
if __name__ == "__main__":
    adapter = ThirdPartySDKAdapter()

    # Fetch data from Facebook
    fb_data = adapter.fetch_data(platform="Facebook", endpoint="get_posts", params={"limit": 10})
    print(fb_data)

    # Post data to LinkedIn
    linkedin_post = adapter.post_data(
        platform="LinkedIn",
        endpoint="create_post",
        payload={"content": "Hello from RLG Data & Fans!", "visibility": "public"},
    )
    print(linkedin_post)

    # List supported platforms
    platforms = adapter.list_supported_platforms()
    print("Supported Platforms:", platforms)

    # Perform a health check
    health_status = adapter.health_check()
    print("SDK Health Status:", health_status)

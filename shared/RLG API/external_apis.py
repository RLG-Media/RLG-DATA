# external_apis.py - External API Integration Utility for RLG Data and RLG Fans

import requests
import logging
from requests.exceptions import HTTPError, Timeout, RequestException
from backend.error_handlers import APIIntegrationError

# Logger configuration
logger = logging.getLogger("external_apis")
logger.setLevel(logging.INFO)

# Global timeout for API requests (in seconds)
DEFAULT_TIMEOUT = 10

# Example API keys (replace with actual values or fetch dynamically)
API_KEYS = {
    "facebook": "your_facebook_api_key",
    "twitter": "your_twitter_api_key",
    "google_analytics": "your_google_analytics_api_key",
    "onlyfans": "your_onlyfans_api_key",
}

# Base URLs for APIs
API_BASE_URLS = {
    "facebook": "https://graph.facebook.com",
    "twitter": "https://api.twitter.com",
    "google_analytics": "https://analytics.googleapis.com",
    "onlyfans": "https://onlyfans.com/api",
}

# User agents for requests
DEFAULT_HEADERS = {
    "User-Agent": "RLGPlatform/1.0 (+https://rlgplatform.com)",
}


def make_request(
    api_name, endpoint, method="GET", params=None, data=None, headers=None, timeout=DEFAULT_TIMEOUT
):
    """
    Make a request to an external API.

    Args:
        api_name (str): Name of the API (e.g., 'facebook', 'twitter').
        endpoint (str): Endpoint to call (e.g., '/v1/resource').
        method (str): HTTP method (GET, POST, PUT, DELETE).
        params (dict): Query parameters for the request.
        data (dict): Request payload for POST/PUT requests.
        headers (dict): Additional headers for the request.
        timeout (int): Request timeout in seconds.

    Returns:
        dict: JSON response from the API.

    Raises:
        APIIntegrationError: If the request fails or the API responds with an error.
    """
    try:
        base_url = API_BASE_URLS.get(api_name)
        if not base_url:
            raise ValueError(f"Base URL for API '{api_name}' is not configured.")

        url = f"{base_url}{endpoint}"
        api_key = API_KEYS.get(api_name)
        headers = headers or {}
        headers.update({"Authorization": f"Bearer {api_key}"})
        headers.update(DEFAULT_HEADERS)

        logger.info(f"Making {method} request to {url}")

        if method.upper() == "GET":
            response = requests.get(url, params=params, headers=headers, timeout=timeout)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=timeout)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=timeout)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=timeout)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()  # Raise an error for bad HTTP responses
        logger.info(f"Received response from {api_name}: {response.status_code}")
        return response.json()
    except HTTPError as e:
        logger.error(f"HTTP error occurred while accessing {api_name}: {e}")
        raise APIIntegrationError(f"HTTP error: {e}")
    except Timeout:
        logger.error(f"Request to {api_name} timed out.")
        raise APIIntegrationError("Request timed out.")
    except RequestException as e:
        logger.error(f"Request error occurred while accessing {api_name}: {e}")
        raise APIIntegrationError(f"Request error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise APIIntegrationError("Unexpected error occurred.")


def fetch_facebook_insights(page_id, access_token):
    """
    Fetch Facebook Insights for a specific page.

    Args:
        page_id (str): ID of the Facebook page.
        access_token (str): Access token for authentication.

    Returns:
        dict: Insights data.

    Raises:
        APIIntegrationError: If the request fails.
    """
    try:
        endpoint = f"/{page_id}/insights"
        params = {"access_token": access_token}
        return make_request("facebook", endpoint, params=params)
    except Exception as e:
        logger.error(f"Failed to fetch Facebook insights for page {page_id}: {e}")
        raise


def fetch_twitter_analytics(user_id):
    """
    Fetch Twitter analytics for a specific user.

    Args:
        user_id (str): Twitter user ID.

    Returns:
        dict: Analytics data.

    Raises:
        APIIntegrationError: If the request fails.
    """
    try:
        endpoint = f"/2/users/{user_id}/analytics"
        return make_request("twitter", endpoint)
    except Exception as e:
        logger.error(f"Failed to fetch Twitter analytics for user {user_id}: {e}")
        raise


def fetch_google_analytics_data(view_id, start_date, end_date, metrics):
    """
    Fetch Google Analytics data for a specific view.

    Args:
        view_id (str): Google Analytics view ID.
        start_date (str): Start date for the data (YYYY-MM-DD).
        end_date (str): End date for the data (YYYY-MM-DD).
        metrics (list): List of metrics to retrieve.

    Returns:
        dict: Analytics data.

    Raises:
        APIIntegrationError: If the request fails.
    """
    try:
        endpoint = "/v3/data/ga"
        params = {
            "ids": f"ga:{view_id}",
            "start-date": start_date,
            "end-date": end_date,
            "metrics": ",".join(metrics),
        }
        return make_request("google_analytics", endpoint, params=params)
    except Exception as e:
        logger.error(f"Failed to fetch Google Analytics data: {e}")
        raise


def fetch_onlyfans_data(account_id):
    """
    Fetch data from OnlyFans for a specific account.

    Args:
        account_id (str): OnlyFans account ID.

    Returns:
        dict: Account data.

    Raises:
        APIIntegrationError: If the request fails.
    """
    try:
        endpoint = f"/accounts/{account_id}"
        return make_request("onlyfans", endpoint)
    except Exception as e:
        logger.error(f"Failed to fetch OnlyFans data for account {account_id}: {e}")
        raise


# Health Check
def check_api_health(api_name):
    """
    Check the health of an external API.

    Args:
        api_name (str): Name of the API.

    Returns:
        bool: True if the API is healthy, False otherwise.
    """
    try:
        # Example: Make a simple GET request to the base URL or a health endpoint
        response = make_request(api_name, "/health")
        if response.get("status") == "healthy":
            logger.info(f"{api_name} API is healthy.")
            return True
        logger.warning(f"{api_name} API health check failed.")
        return False
    except APIIntegrationError:
        return False

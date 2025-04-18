# api_helpers.py

import requests
from flask import jsonify, current_app
from requests.exceptions import HTTPError, Timeout, RequestException


# API response handler
def handle_api_response(response):
    """Handle and process the API response."""
    try:
        response.raise_for_status()
        return response.json()
    except HTTPError as http_err:
        current_app.logger.error(f"HTTP error occurred: {http_err}")
        return {"error": "API request failed", "status_code": response.status_code}
    except Timeout as timeout_err:
        current_app.logger.error(f"Timeout error occurred: {timeout_err}")
        return {"error": "API request timed out", "status_code": 504}
    except RequestException as req_err:
        current_app.logger.error(f"Request exception occurred: {req_err}")
        return {"error": "An error occurred with the API request", "status_code": 500}


# Generic GET request
def get_request(url, headers=None, params=None):
    """Perform a GET request with specified headers and parameters."""
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        return handle_api_response(response)
    except Exception as e:
        current_app.logger.error(f"Error in GET request: {e}")
        return {"error": "Failed to fetch data from external API"}


# Generic POST request
def post_request(url, headers=None, data=None, json_data=None):
    """Perform a POST request with specified headers and data."""
    try:
        response = requests.post(url, headers=headers, data=data, json=json_data, timeout=10)
        return handle_api_response(response)
    except Exception as e:
        current_app.logger.error(f"Error in POST request: {e}")
        return {"error": "Failed to post data to external API"}


# Helper for fetching service data
def fetch_service_data(service_name, url, headers=None, params=None):
    """Fetch data from an external service by name, logging errors with the service name."""
    current_app.logger.info(f"Fetching data from {service_name} service")
    response = get_request(url, headers=headers, params=params)
    if "error" in response:
        current_app.logger.error(f"Error fetching data from {service_name}: {response['error']}")
    return response


# Error handler for API endpoints
def api_error_response(message, status_code=400):
    """Return a JSON error response for API failures."""
    return jsonify({"error": message}), status_code


# Helper for unified logging and response structure
def log_and_respond(data=None, error=None, status_code=200):
    """Unified logging and response handling for API endpoints."""
    if error:
        current_app.logger.error(error)
        return jsonify({"error": error}), status_code
    else:
        return jsonify(data), status_code


# API call for RLG Data metrics
def fetch_rlg_data_metrics(endpoint, headers=None, params=None):
    """Fetch metrics specific to RLG Data."""
    url = f"{current_app.config['RLG_DATA_BASE_URL']}/{endpoint}"
    return fetch_service_data("RLG Data", url, headers=headers, params=params)


# API call for RLG Fans analytics
def fetch_rlg_fans_analytics(endpoint, headers=None, params=None):
    """Fetch analytics specific to RLG Fans."""
    url = f"{current_app.config['RLG_FANS_BASE_URL']}/{endpoint}"
    return fetch_service_data("RLG Fans", url, headers=headers, params=params)


# API call for third-party platforms
def fetch_third_party_data(platform_name, url, headers=None, params=None):
    """Fetch data from a third-party platform."""
    current_app.logger.info(f"Fetching data from {platform_name} platform")
    return fetch_service_data(platform_name, url, headers=headers, params=params)


# Example integration for a newly added service
def fetch_youtube_analytics(endpoint, headers=None, params=None):
    """Fetch analytics from YouTube via RLG Fans."""
    url = f"{current_app.config['YOUTUBE_API_BASE_URL']}/{endpoint}"
    return fetch_third_party_data("YouTube", url, headers=headers, params=params)


def fetch_zapier_automation(task_id, headers=None):
    """Fetch automation details from Zapier."""
    url = f"{current_app.config['ZAPIER_API_BASE_URL']}/tasks/{task_id}"
    return fetch_third_party_data("Zapier", url, headers=headers)

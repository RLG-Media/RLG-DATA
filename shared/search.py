from flask import Blueprint, request, jsonify
from backend.api_integration import fetch_data_from_api
from shared.error_handling import APIError, validate_request_data

# Create a Blueprint for search functionality
search = Blueprint("search", __name__)

@search.route("/search", methods=["GET"])
def search_data():
    """
    Handles search functionality for the application.
    Supports searching across multiple services or platforms.

    Query Parameters:
    - query (str): The search term entered by the user.
    - platform (str): Optional. The specific platform to filter the search (e.g., 'facebook', 'twitter').
    - limit (int): Optional. Maximum number of results to return. Default is 10.
    """
    try:
        # Extract query parameters
        query = request.args.get("query", "").strip()
        platform = request.args.get("platform", "").strip()
        limit = int(request.args.get("limit", 10))

        # Validate input
        if not query:
            raise ValueError("The 'query' parameter is required.")

        # Prepare API endpoint and parameters
        endpoint = "/search"
        params = {"query": query, "platform": platform, "limit": limit}

        # Fetch search results from the API
        search_results = fetch_data_from_api(endpoint, params=params)

        # Return results as JSON
        return jsonify({"success": True, "results": search_results}), 200

    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"success": False, "error": "An unexpected error occurred. Please try again later."}), 500


@search.route("/autocomplete", methods=["GET"])
def autocomplete():
    """
    Provides autocomplete suggestions for search queries.

    Query Parameters:
    - term (str): The partial term for which suggestions are needed.
    - platform (str): Optional. The specific platform to filter suggestions.
    """
    try:
        # Extract query parameters
        term = request.args.get("term", "").strip()
        platform = request.args.get("platform", "").strip()

        # Validate input
        if not term:
            raise ValueError("The 'term' parameter is required.")

        # Prepare API endpoint and parameters
        endpoint = "/autocomplete"
        params = {"term": term, "platform": platform}

        # Fetch autocomplete suggestions
        suggestions = fetch_data_from_api(endpoint, params=params)

        # Return suggestions as JSON
        return jsonify({"success": True, "suggestions": suggestions}), 200

    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"success": False, "error": "An unexpected error occurred. Please try again later."}), 500


@search.route("/filters", methods=["GET"])
def search_filters():
    """
    Retrieves available filters for search functionality.

    This endpoint provides a list of supported platforms or filter criteria.
    """
    try:
        # Fetch filter options from the API
        filter_options = fetch_data_from_api("/search/filters")

        # Return filters as JSON
        return jsonify({"success": True, "filters": filter_options}), 200

    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"success": False, "error": "An unexpected error occurred. Please try again later."}), 500

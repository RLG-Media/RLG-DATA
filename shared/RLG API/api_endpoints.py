"""
api_endpoints.py

This module sets up a Flask application that exposes RESTful API endpoints for both RLG Data and RLG Fans.
It leverages the APIConnector to interact with external services and provides endpoints for health checks,
data retrieval, and data posting.
"""

from flask import Flask, Blueprint, jsonify, request
import logging
from api_connector import APIConnector

# Configure logging for the API endpoints
logger = logging.getLogger("APIEndpoints")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

# Sample configuration for API endpoints
# In a real-world deployment, load these from secure environment variables or a config file.
config = {
    "endpoints": {
        "rlg_data": {
            "url": "https://api.rlgdata.example.com/v1/data",
            "api_key": "YOUR_RLG_DATA_API_KEY",  # Replace with secure API key retrieval
            "headers": {"Content-Type": "application/json"}
        },
        "rlg_fans": {
            "url": "https://api.rlgfans.example.com/v1/fans",
            "api_key": "YOUR_RLG_FANS_API_KEY",  # Replace with secure API key retrieval
            "headers": {"Content-Type": "application/json"}
        }
    }
}

# Create an instance of APIConnector with the above configuration.
api_connector = APIConnector(config)

# Create a Flask app
app = Flask(__name__)

# ---------------------------------------------------------------
# Blueprint for RLG Data endpoints
# ---------------------------------------------------------------
data_bp = Blueprint('data_bp', __name__, url_prefix='/data')

@data_bp.route('/health', methods=['GET'])
def data_health_check():
    """
    Health check endpoint for RLG Data.
    Returns a JSON response indicating whether the external RLG Data API is accessible.
    """
    healthy = api_connector.health_check("rlg_data")
    status = "healthy" if healthy else "down"
    return jsonify({"service": "RLG Data", "status": status}), (200 if healthy else 503)

@data_bp.route('/', methods=['GET'])
def get_data():
    """
    Retrieve data from the external RLG Data API.
    Accepts query parameters which are passed along to the external API.
    """
    params = request.args.to_dict()
    try:
        data = api_connector.get("rlg_data", params=params)
        return jsonify(data), 200
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return jsonify({"error": str(e)}), 500

@data_bp.route('/', methods=['POST'])
def post_data():
    """
    Post new data to the external RLG Data API.
    Expects a JSON payload in the request body.
    """
    payload = request.get_json()
    try:
        response = api_connector.post("rlg_data", json_data=payload)
        return jsonify(response), 201
    except Exception as e:
        logger.error(f"Error posting data: {e}")
        return jsonify({"error": str(e)}), 500

# ---------------------------------------------------------------
# Blueprint for RLG Fans endpoints
# ---------------------------------------------------------------
fans_bp = Blueprint('fans_bp', __name__, url_prefix='/fans')

@fans_bp.route('/health', methods=['GET'])
def fans_health_check():
    """
    Health check endpoint for RLG Fans.
    Returns a JSON response indicating whether the external RLG Fans API is accessible.
    """
    healthy = api_connector.health_check("rlg_fans")
    status = "healthy" if healthy else "down"
    return jsonify({"service": "RLG Fans", "status": status}), (200 if healthy else 503)

@fans_bp.route('/', methods=['GET'])
def get_fans():
    """
    Retrieve data from the external RLG Fans API.
    Accepts query parameters which are passed along to the external API.
    """
    params = request.args.to_dict()
    try:
        fans = api_connector.get("rlg_fans", params=params)
        return jsonify(fans), 200
    except Exception as e:
        logger.error(f"Error fetching fans data: {e}")
        return jsonify({"error": str(e)}), 500

@fans_bp.route('/', methods=['POST'])
def post_fan():
    """
    Post new data to the external RLG Fans API.
    Expects a JSON payload in the request body.
    """
    payload = request.get_json()
    try:
        response = api_connector.post("rlg_fans", json_data=payload)
        return jsonify(response), 201
    except Exception as e:
        logger.error(f"Error posting fans data: {e}")
        return jsonify({"error": str(e)}), 500

# ---------------------------------------------------------------
# Register Blueprints with the Flask application
# ---------------------------------------------------------------
app.register_blueprint(data_bp)
app.register_blueprint(fans_bp)

# ---------------------------------------------------------------
# Additional Recommendations:
# ---------------------------------------------------------------
# 1. **Authentication & Authorization:** Add security layers (e.g., JWT, OAuth) to protect your endpoints.
# 2. **Validation:** Implement request data validation (e.g., using Marshmallow or pydantic) to ensure
#    incoming data meets expected formats.
# 3. **Asynchronous Processing:** For higher scalability, consider migrating to an asynchronous framework
#    like FastAPI or using async libraries with Flask.
# 4. **Caching:** Introduce caching (e.g., Redis) for frequently requested data to improve performance.
# 5. **Monitoring:** Integrate logging and monitoring (e.g., Prometheus, ELK Stack) to track endpoint performance.
#
# The current code is designed for clarity and robustness during initial development and testing.

# ---------------------------------------------------------------
# Run the Flask application (for development/testing)
# ---------------------------------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

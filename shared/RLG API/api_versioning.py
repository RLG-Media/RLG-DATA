from flask import Flask, jsonify, Blueprint, request
from werkzeug.exceptions import HTTPException

app = Flask(__name__)

# Define blueprints for versioned APIs
v1 = Blueprint('v1', __name__)
v2 = Blueprint('v2', __name__)

# Global versioning configuration
DEFAULT_API_VERSION = "v1"
SUPPORTED_VERSIONS = ["v1", "v2"]

# Error handler for unsupported versions
@app.errorhandler(HTTPException)
def handle_http_exception(error):
    """
    Global error handler for API exceptions.
    """
    response = error.get_response()
    response.data = jsonify({
        "error": error.description,
        "code": error.code,
    }).get_data(as_text=True)
    response.content_type = "application/json"
    return response


@app.errorhandler(404)
def handle_404(error):
    """
    Handle 404 errors with a version-specific response.
    """
    return jsonify({"error": "Endpoint not found", "code": 404}), 404


# API version-specific routes
@v1.route('/status', methods=['GET'])
def v1_status():
    """
    API Status for v1.
    """
    return jsonify({
        "api_version": "v1",
        "status": "Operational",
        "message": "Welcome to RLG Data API v1!"
    })


@v2.route('/status', methods=['GET'])
def v2_status():
    """
    API Status for v2.
    """
    return jsonify({
        "api_version": "v2",
        "status": "Operational",
        "message": "Welcome to RLG Data API v2! Enhanced and faster."
    })


@v1.route('/users', methods=['GET'])
def v1_users():
    """
    Fetch users in v1 format.
    """
    # Mock data for demonstration
    return jsonify({
        "api_version": "v1",
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ]
    })


@v2.route('/users', methods=['GET'])
def v2_users():
    """
    Fetch users in v2 format with enhanced details.
    """
    # Mock data for demonstration
    return jsonify({
        "api_version": "v2",
        "users": [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"}
        ]
    })


# Middleware to handle versioning
@app.before_request
def check_api_version():
    """
    Middleware to validate and route API requests based on version.
    """
    path = request.path.lstrip("/")
    parts = path.split("/", 1)

    if len(parts) > 0 and parts[0] in SUPPORTED_VERSIONS:
        version = parts[0]
        request.environ["api.version"] = version
        app.url_map.default_subdomain = None
        request.url_rule = None  # Reset rule for versioned endpoints
    else:
        request.environ["api.version"] = DEFAULT_API_VERSION


# Register blueprints
app.register_blueprint(v1, url_prefix='/api/v1')
app.register_blueprint(v2, url_prefix='/api/v2')

# Default fallback for non-versioned routes
@app.route('/api/status', methods=['GET'])
def default_status():
    """
    Fallback route for default API version.
    """
    return jsonify({
        "api_version": DEFAULT_API_VERSION,
        "status": "Operational",
        "message": f"Welcome to RLG Data API {DEFAULT_API_VERSION}!"
    })


# Utility function for compatibility handling
def version_check(required_version):
    """
    Utility decorator for checking API version compatibility.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            current_version = request.environ.get("api.version", DEFAULT_API_VERSION)
            if current_version != required_version:
                return jsonify({
                    "error": "Version mismatch",
                    "required_version": required_version,
                    "current_version": current_version
                }), 400
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Example route using version check
@v2.route('/advanced-feature', methods=['GET'])
@version_check("v2")
def advanced_feature():
    """
    Example of a version-specific feature.
    """
    return jsonify({
        "api_version": "v2",
        "feature": "This is an advanced feature available only in v2."
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)

import logging
import traceback
from flask import jsonify, request
from sentry_sdk import capture_exception
from notifications import send_error_notification  # For notifying via email or other channels if needed

logger = logging.getLogger(__name__)

def log_error(error):
    """
    Log the error details and capture with Sentry if configured.
    Optionally, notify administrators if a critical error occurs.
    """
    # Format error details
    error_message = f"Error: {error}"
    error_traceback = traceback.format_exc()

    # Log error locally
    logger.error(error_message)
    logger.error("Traceback: %s", error_traceback)

    # Capture error with Sentry for monitoring
    capture_exception(error)

    # Optional: Send an error notification if configured
    send_error_notification(error_message, error_traceback)


def handle_http_error(status_code, message=None):
    """
    Custom handler for HTTP errors (e.g., 404, 500).
    """
    # Default message based on status code if none provided
    default_messages = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        500: "Internal Server Error"
    }
    message = message or default_messages.get(status_code, "An error occurred")

    # Log the error if it's a server-side error (5xx)
    if status_code >= 500:
        log_error(f"HTTP {status_code}: {message}")

    # Respond with a JSON error message
    response = jsonify({
        "error": message,
        "status_code": status_code
    })
    response.status_code = status_code
    return response


def handle_exception(error):
    """
    General exception handler for all uncaught errors.
    """
    log_error(error)  # Log the error details
    response = jsonify({
        "error": "An unexpected error occurred. Please try again later.",
        "status_code": 500
    })
    response.status_code = 500
    return response


def setup_error_handlers(app):
    """
    Register error handlers for the Flask app.
    """
    @app.errorhandler(400)
    def handle_400_error(error):
        return handle_http_error(400, str(error))

    @app.errorhandler(401)
    def handle_401_error(error):
        return handle_http_error(401, str(error))

    @app.errorhandler(403)
    def handle_403_error(error):
        return handle_http_error(403, str(error))

    @app.errorhandler(404)
    def handle_404_error(error):
        return handle_http_error(404, str(error))

    @app.errorhandler(500)
    def handle_500_error(error):
        return handle_http_error(500, str(error))

    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        return handle_exception(error)

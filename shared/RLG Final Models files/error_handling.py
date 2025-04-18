"""
error_handling.py
Centralized error handling module for RLG Data and RLG Fans.
Provides structured exception management, logging, and standardized error responses.
"""

import logging
from flask import jsonify, request
from typing import Any, Dict, Optional
from werkzeug.exceptions import HTTPException

# Logger setup
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Custom error codes and messages
ERROR_MESSAGES = {
    "ValidationError": "Invalid input data.",
    "DatabaseError": "A database error occurred. Please try again later.",
    "AuthenticationError": "Authentication failed. Please check your credentials.",
    "AuthorizationError": "You do not have permission to access this resource.",
    "NotFoundError": "The requested resource could not be found.",
    "ServiceUnavailableError": "The service is temporarily unavailable. Please try again later.",
    "GenericError": "An unexpected error occurred. Please try again later.",
}


class CustomError(Exception):
    """
    Base class for custom exceptions in RLG applications.
    """

    def __init__(self, message: Optional[str] = None, status_code: int = 500, extra: Optional[Dict[str, Any]] = None):
        """
        Initialize a custom error.

        Args:
            message (str): Error message.
            status_code (int): HTTP status code.
            extra (dict, optional): Additional context or data for the error.
        """
        self.message = message or ERROR_MESSAGES.get("GenericError", "An error occurred.")
        self.status_code = status_code
        self.extra = extra or {}

        # Log the error
        logger.error(f"{self.__class__.__name__}: {self.message}. Extra: {self.extra}")


class ValidationError(CustomError):
    def __init__(self, message: Optional[str] = None, extra: Optional[Dict[str, Any]] = None):
        super().__init__(message or ERROR_MESSAGES["ValidationError"], status_code=400, extra=extra)


class DatabaseError(CustomError):
    def __init__(self, message: Optional[str] = None, extra: Optional[Dict[str, Any]] = None):
        super().__init__(message or ERROR_MESSAGES["DatabaseError"], status_code=500, extra=extra)


class AuthenticationError(CustomError):
    def __init__(self, message: Optional[str] = None, extra: Optional[Dict[str, Any]] = None):
        super().__init__(message or ERROR_MESSAGES["AuthenticationError"], status_code=401, extra=extra)


class AuthorizationError(CustomError):
    def __init__(self, message: Optional[str] = None, extra: Optional[Dict[str, Any]] = None):
        super().__init__(message or ERROR_MESSAGES["AuthorizationError"], status_code=403, extra=extra)


class NotFoundError(CustomError):
    def __init__(self, message: Optional[str] = None, extra: Optional[Dict[str, Any]] = None):
        super().__init__(message or ERROR_MESSAGES["NotFoundError"], status_code=404, extra=extra)


class ServiceUnavailableError(CustomError):
    def __init__(self, message: Optional[str] = None, extra: Optional[Dict[str, Any]] = None):
        super().__init__(message or ERROR_MESSAGES["ServiceUnavailableError"], status_code=503, extra=extra)


# Utility functions
def handle_exception(e: Exception):
    """
    Generic exception handler for Flask applications.

    Args:
        e (Exception): The exception to handle.

    Returns:
        Response: A JSON response with error details.
    """
    if isinstance(e, HTTPException):
        response = {
            "error": e.name,
            "message": e.description,
            "status_code": e.code,
        }
        logger.warning(f"HTTPException: {response}")
        return jsonify(response), e.code

    if isinstance(e, CustomError):
        response = {
            "error": e.__class__.__name__,
            "message": e.message,
            "status_code": e.status_code,
            "extra": e.extra,
        }
        logger.error(f"CustomError: {response}")
        return jsonify(response), e.status_code

    # Generic fallback for unexpected errors
    logger.critical(f"Unhandled exception: {str(e)}")
    response = {
        "error": "InternalServerError",
        "message": ERROR_MESSAGES["GenericError"],
        "status_code": 500,
    }
    return jsonify(response), 500


def register_error_handlers(app):
    """
    Registers error handlers to the Flask application.

    Args:
        app (Flask): The Flask application instance.
    """
    @app.errorhandler(Exception)
    def global_error_handler(e):
        return handle_exception(e)


def generate_error_context() -> Dict[str, Any]:
    """
    Generates a detailed error context for logging.

    Returns:
        Dict[str, Any]: Error context including method, URL, and headers.
    """
    return {
        "method": request.method,
        "url": request.url,
        "headers": dict(request.headers),
    }


# Example usage
if __name__ == "__main__":
    # Example application for testing purposes
    from flask import Flask

    app = Flask(__name__)
    register_error_handlers(app)

    @app.route("/test")
    def test_route():
        # Example route to trigger custom error
        raise ValidationError(extra=generate_error_context())

    @app.route("/generic")
    def generic_error():
        # Example route to trigger a generic error
        raise Exception("This is an unexpected error.")

    # Run the Flask app
    app.run(debug=True)

import logging
from typing import Any, Dict, Optional
from flask import jsonify, Response

# Configure logging
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("error_handling.log"),
        logging.StreamHandler()
    ]
)

class APIError(Exception):
    """
    Custom exception for API-related errors.
    """
    def __init__(self, message: str, status_code: int = 400, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the APIError instance.
        :param message: Error message to be displayed.
        :param status_code: HTTP status code for the error.
        :param details: Optional dictionary with additional error details.
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the error into a dictionary for response serialization.
        :return: Dictionary representation of the error.
        """
        error_response = {
            "error": {
                "message": self.message,
                "status_code": self.status_code
            }
        }
        if self.details:
            error_response["error"]["details"] = self.details
        return error_response


def handle_api_error(error: APIError) -> Response:
    """
    Flask error handler for APIError.
    :param error: Instance of APIError.
    :return: JSON response with the error details.
    """
    logging.error(f"APIError: {error.message} | Status Code: {error.status_code} | Details: {error.details}")
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def handle_generic_error(error: Exception) -> Response:
    """
    Generic error handler for unexpected exceptions.
    :param error: Instance of Exception.
    :return: JSON response with a generic error message.
    """
    logging.exception(f"Unexpected Error: {str(error)}")
    response = jsonify({
        "error": {
            "message": "An unexpected error occurred. Please try again later.",
            "status_code": 500
        }
    })
    response.status_code = 500
    return response


def validate_request_data(data: Dict[str, Any], required_fields: list) -> None:
    """
    Validates the presence of required fields in the request data.
    :param data: Request data as a dictionary.
    :param required_fields: List of required field names.
    :raises APIError: If validation fails.
    """
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise APIError(
            message="Validation error: Missing required fields.",
            status_code=422,
            details={"missing_fields": missing_fields}
        )


# Example Usage in Flask App
# --------------------------
# from flask import Flask, request
# app = Flask(__name__)
#
# # Register error handlers
# app.register_error_handler(APIError, handle_api_error)
# app.register_error_handler(Exception, handle_generic_error)
#
# @app.route('/example', methods=['POST'])
# def example_route():
#     data = request.get_json()
#     validate_request_data(data, ["name", "email"])
#     return jsonify({"message": "Request data is valid."}), 200
#
# if __name__ == "__main__":
#     app.run(debug=True)

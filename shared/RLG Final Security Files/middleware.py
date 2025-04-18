import logging
from flask import request, jsonify
from functools import wraps

# Configure logging for middleware
logger = logging.getLogger("middleware")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

class Middleware:
    """
    Middleware class for shared functionalities for RLG Data and RLG Fans.
    Includes request logging, authentication, rate limiting, and error handling.
    """

    @staticmethod
    def log_requests(func):
        """
        Middleware to log incoming requests.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info("Incoming request: %s %s", request.method, request.url)
            return func(*args, **kwargs)
        return wrapper

    @staticmethod
    def require_authentication(func):
        """
        Middleware to enforce authentication.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization")
            if not auth_header or not Middleware.validate_token(auth_header):
                logger.warning("Unauthorized access attempt.")
                return jsonify({"error": "Unauthorized"}), 401
            return func(*args, **kwargs)
        return wrapper

    @staticmethod
    def validate_token(token: str) -> bool:
        """
        Validate the provided authentication token.

        Args:
            token: The authentication token from the request header.

        Returns:
            bool: True if valid, False otherwise.
        """
        # Replace with actual token validation logic (e.g., JWT decoding)
        valid_tokens = ["valid_token_example"]
        return token in valid_tokens

    @staticmethod
    def rate_limit(limit: int):
        """
        Middleware to enforce rate limiting.

        Args:
            limit: The number of requests allowed per minute.
        """
        def decorator(func):
            from flask_limiter import Limiter
            from flask_limiter.util import get_remote_address

            limiter = Limiter(get_remote_address)

            @limiter.limit(f"{limit}/minute")
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def handle_errors(func):
        """
        Middleware to handle and log errors gracefully.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error("An error occurred: %s", str(e))
                return jsonify({"error": "An internal server error occurred."}), 500
        return wrapper

# Example usage in a Flask route
from flask import Flask

app = Flask(__name__)

@app.route("/protected-resource")
@Middleware.log_requests
@Middleware.require_authentication
@Middleware.rate_limit(10)  # 10 requests per minute
@Middleware.handle_errors
def protected_resource():
    return jsonify({"message": "This is a protected resource."})

if __name__ == "__main__":
    app.run(debug=True)

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import current_app, request
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def configure_limiter(app):
    """
    Configure Flask-Limiter for the application.
    
    :param app: The Flask application instance.
    """
    try:
        # Initialize the limiter with the app
        limiter = Limiter(
            key_func=get_remote_address,  # Use the IP address as the rate-limiting key
            default_limits=["200 per day", "50 per hour"],  # Default rate limits
            storage_uri="redis://localhost:6379",  # Store rate limiting data in Redis
        )

        # Attach the limiter to the app
        limiter.init_app(app)
        logging.info("Rate limiter initialized successfully.")

        # Custom route-specific limits can be applied using decorators in routes.py
        apply_custom_limits(limiter)

        return limiter

    except Exception as e:
        logging.error(f"Error initializing rate limiter: {e}")
        raise


def apply_custom_limits(limiter):
    """
    Apply custom rate limits to specific routes in the application.
    
    :param limiter: The Limiter instance.
    """
    try:
        # Example: Custom limit for login attempts (5 per minute)
        limiter.limit("5 per minute")(current_app.view_functions['auth.login'])

        # Example: Custom limit for API scraping (10 per hour)
        limiter.limit("10 per hour")(current_app.view_functions['scrape'])

        # Add any additional custom limits as needed
        logging.info("Custom rate limits applied successfully.")
    
    except Exception as e:
        logging.error(f"Error applying custom rate limits: {e}")
        raise


def exempt_route_from_limit(route_name):
    """
    Exempt specific routes from rate limiting.
    
    :param route_name: The name of the route function to exempt.
    """
    try:
        # Exempt the specified route from all rate limits
        Limiter.exempt(current_app.view_functions[route_name])
        logging.info(f"Route {route_name} exempted from rate limiting.")
    
    except Exception as e:
        logging.error(f"Error exempting route {route_name} from rate limits: {e}")
        raise


"""
main.py

Entry point for the RLG Data and RLG Fans application.
This file initializes the Flask application, loads configuration settings,
registers blueprints for various functionalities (API endpoints, chatbot, dashboard, etc.),
initializes extensions (like the database), and sets up error handlers.
"""

import os
import logging
from flask import Flask
from config import Config  # Your configuration settings (e.g., environment variables)
from database_manager import db  # SQLAlchemy instance
from api_endpoints import api_bp  # Blueprint for API endpoints
from chatbot import chatbot_bp  # Blueprint for chatbot routes
from dashboard import dashboard_bp  # Blueprint for dashboard routes
from error_handlers import register_error_handlers  # Function to register custom error handlers

# Optional: Import additional blueprints or extensions here
# from client_portal import client_portal_bp
# from rate_limiting import rate_limiting_bp

def create_app() -> Flask:
    """
    Application factory for creating and configuring the Flask application.

    Returns:
        app (Flask): The configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    # Optionally initialize other extensions here (e.g., caching, Celery)

    # Register blueprints
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(chatbot_bp, url_prefix="/chat")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    # app.register_blueprint(client_portal_bp, url_prefix="/portal")
    # app.register_blueprint(rate_limiting_bp, url_prefix="/rate")

    # Register custom error handlers
    register_error_handlers(app)

    # Log that the application was created successfully
    app.logger.info("Application created successfully with configuration: %s", app.config)

    return app

if __name__ == "__main__":
    # Create the app using the factory function
    app = create_app()

    # Determine port from environment variable or default to 5000
    port = int(os.environ.get("PORT", 5000))
    debug_mode = app.config.get("DEBUG", False)

    # Start the Flask development server (disable debug mode in production)
    app.run(host="0.0.0.0", port=port, debug=debug_mode)

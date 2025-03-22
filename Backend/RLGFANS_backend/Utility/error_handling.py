# error_handling.py - Utility for error handling and logging in RLG Fans

import logging
import traceback
from flask import jsonify, current_app
from datetime import datetime
from flask_mail import Message
from smtplib import SMTPException
from extensions import mail

class ErrorHandler:
    """
    Provides error handling, logging, and optional error notification functionality.
    """

    @staticmethod
    def log_error(error, context=""):
        """
        Logs error details including traceback and optional context.
        """
        error_details = {
            "type": type(error).__name__,
            "message": str(error),
            "context": context,
            "traceback": traceback.format_exc(),
            "timestamp": datetime.utcnow()
        }
        logging.error(f"Error occurred: {error_details}")
        return error_details

    @staticmethod
    def notify_admin(error_details):
        """
        Sends an email notification to the admin with error details.
        """
        try:
            msg = Message(
                subject="RLG Fans Error Notification",
                sender=current_app.config.get("MAIL_DEFAULT_SENDER"),
                recipients=[current_app.config.get("ADMIN_EMAIL")],
            )
            msg.body = (
                f"An error occurred:\n\n"
                f"Type: {error_details['type']}\n"
                f"Message: {error_details['message']}\n"
                f"Context: {error_details['context']}\n\n"
                f"Traceback:\n{error_details['traceback']}\n\n"
                f"Timestamp: {error_details['timestamp']}"
            )
            mail.send(msg)
            logging.info("Admin notified about the error.")
        except SMTPException as e:
            logging.error(f"Failed to send error notification email: {e}")

    @staticmethod
    def handle_error(error, context=""):
        """
        General handler that logs, optionally notifies, and returns a JSON response.
        """
        error_details = ErrorHandler.log_error(error, context)

        if current_app.config.get("NOTIFY_ADMIN_ON_ERROR"):
            ErrorHandler.notify_admin(error_details)

        response = {
            "error": "An unexpected error occurred. Please try again later.",
            "details": {
                "type": error_details["type"],
                "message": "An internal error occurred.",
                "timestamp": error_details["timestamp"],
            },
        }
        return jsonify(response), 500

def register_error_handlers(app):
    """
    Registers global error handlers for Flask application.
    """
    @app.errorhandler(Exception)
    def handle_exception(error):
        """
        Handle general exceptions and return JSON response.
        """
        return ErrorHandler.handle_error(error)

    @app.errorhandler(404)
    def handle_404(error):
        """
        Handle 404 Not Found error and return JSON response.
        """
        logging.warning(f"404 Not Found: {error}")
        return jsonify({"error": "The requested resource was not found."}), 404

    @app.errorhandler(400)
    def handle_400(error):
        """
        Handle 400 Bad Request error and return JSON response.
        """
        logging.warning(f"400 Bad Request: {error}")
        return jsonify({"error": "Bad request. Please check the input data."}), 400

# End of error_handling.py

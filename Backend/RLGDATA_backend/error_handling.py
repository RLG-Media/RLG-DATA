import logging
from flask import jsonify, render_template, request
from app import app
from flask_mail import Message
from email_utils import send_critical_error_email

# Configure logging
logging.basicConfig(level=logging.INFO)

### CUSTOM ERROR HANDLERS ###

@app.errorhandler(404)
def not_found_error(error):
    """
    Handle 404 Not Found errors.
    """
    logging.error(f"404 Error: {request.url} not found.")
    return jsonify({'error': 'The requested resource could not be found.'}), 404


@app.errorhandler(500)
def internal_error(error):
    """
    Handle 500 Internal Server errors.
    """
    logging.error(f"500 Error: Internal server error at {request.url}. Error details: {error}")
    
    # Optional: Send critical error notification
    send_critical_error_email('admin@yourdomain.com', error)

    return jsonify({'error': 'An internal server error occurred. Please try again later.'}), 500


@app.errorhandler(Exception)
def global_exception_handler(error):
    """
    Catch-all handler for any uncaught exceptions.
    """
    logging.error(f"Unhandled Exception: {error}. Request URL: {request.url}.")
    
    # Optional: Send critical error notification
    send_critical_error_email('admin@yourdomain.com', error)

    return jsonify({'error': 'An unexpected error occurred. Our team has been notified.'}), 500


### ERROR LOGGING FUNCTION ###

def log_error(error):
    """
    Log error details, including request information, if available.
    """
    logging.error(f"Error occurred: {error}")
    if request:
        logging.error(f"Request URL: {request.url}")
        logging.error(f"Request Headers: {request.headers}")
        logging.error(f"Request Body: {request.data}")


### OPTIONAL ERROR NOTIFICATION ###

def send_critical_error_email(recipient, error):
    """
    Send a critical error notification via email.
    
    :param recipient: Email address of the recipient (e.g., system admin)
    :param error: Error details to include in the email body
    """
    try:
        msg = Message("Critical Error in RLG DATA", sender="your_email@domain.com", recipients=[recipient])
        msg.body = f"A critical error occurred:\n\nError: {error}\n\nPlease investigate the issue."
        mail.send(msg)
        logging.info(f"Critical error notification sent to {recipient}.")

    except Exception as e:
        logging.error(f"Failed to send error notification: {e}")


### CUSTOM EXCEPTIONS ###

class APIError(Exception):
    """
    Custom exception for API-related errors.
    """
    def __init__(self, message, status_code=500):
        super().__init__(message)
        self.status_code = status_code

    def to_dict(self):
        return {'error': self.message}


@app.errorhandler(APIError)
def handle_api_error(error):
    """
    Handle custom API errors.
    """
    logging.error(f"API Error: {error.message}. Status code: {error.status_code}")
    return jsonify(error.to_dict()), error.status_code

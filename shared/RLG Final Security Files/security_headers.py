from flask import Flask, request, jsonify
from werkzeug.exceptions import Forbidden

# List of secure HTTP headers to be applied
SECURITY_HEADERS = {
    'Content-Security-Policy': "default-src 'self'; img-src 'self' data:; script-src 'self'; style-src 'self';",
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Feature-Policy': "geolocation 'self'; microphone 'none'; camera 'none'",
    'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0'
}

def apply_security_headers(response):
    """
    Function to apply security headers to each response.
    Args:
        response (flask.Response): The response object from Flask.
    Returns:
        flask.Response: The response with security headers.
    """
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    return response

def setup_security_headers(app):
    """
    Apply security headers globally for the Flask app.
    Args:
        app (Flask): The Flask application instance.
    """
    app.after_request(apply_security_headers)

# Example Flask application setup
app = Flask(__name__)

@app.route('/data')
def get_data():
    """
    A sample endpoint to fetch data, demonstrating the usage of security headers.
    """
    # Simulate data fetching
    data = {"message": "This is secure data."}
    return jsonify(data)

@app.route('/admin')
def admin_dashboard():
    """
    Admin-only route with strict security headers.
    """
    return jsonify({"message": "Welcome to the Admin Dashboard!"})

if __name__ == '__main__':
    setup_security_headers(app)
    app.run(debug=True, host='0.0.0.0', port=5000)

# security_checks.py

import re
import logging
from flask import request, jsonify, g, current_app
from functools import wraps
from app.shared.external_api_connections import validate_api_request  # Import to validate API integrations

# Logger setup for security monitoring
logger = logging.getLogger("security_checks")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def prevent_sql_injection(input_string):
    """Check for potential SQL injection patterns."""
    sql_injection_patterns = re.compile(r"(?:--|\b(ALTER|DROP|INSERT|DELETE|UPDATE|SELECT|UNION|OR|AND)\b)", re.IGNORECASE)
    if sql_injection_patterns.search(input_string):
        logger.warning(f"SQL Injection attempt detected: {input_string}")
        return False
    return True

def input_sanitization_required(f):
    """Decorator to sanitize and validate input data for routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        data = request.json or request.form or {}
        for key, value in data.items():
            if isinstance(value, str) and not prevent_sql_injection(value):
                return jsonify({"error": "Invalid input detected"}), 400
        return f(*args, **kwargs)
    return decorated

def suspicious_activity_monitor(f):
    """Decorator to log and respond to suspicious activity."""
    @wraps(f)
    def decorated(*args, **kwargs):
        ip_address = request.remote_addr
        user_agent = request.headers.get("User-Agent", "")
        
        # Check for empty user-agent (commonly associated with bots)
        if not user_agent:
            logger.warning(f"Suspicious activity detected from IP {ip_address}: Empty User-Agent")
            return jsonify({"error": "Suspicious activity detected"}), 403

        # Additional monitoring for excessive requests
        # Could integrate rate-limiting or abuse detection here
        logger.info(f"Request from IP {ip_address}, User-Agent: {user_agent}")
        return f(*args, **kwargs)
    return decorated

def enforce_content_security(f):
    """Decorator to enforce Content Security Policy headers."""
    @wraps(f)
    def decorated(*args, **kwargs):
        response = f(*args, **kwargs)
        csp = (
            "default-src 'self'; "
            "script-src 'self' https://trusted-scripts.com; "
            "style-src 'self' https://trusted-styles.com; "
            "img-src 'self' data:; "
            "connect-src 'self' https://trusted-api.com https://additional-trusted-api.com;"
        )
        response.headers['Content-Security-Policy'] = csp
        return response
    return decorated

def secure_headers(f):
    """Decorator to add HTTP headers for security best practices."""
    @wraps(f)
    def decorated(*args, **kwargs):
        response = f(*args, **kwargs)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        return response
    return decorated

def validate_external_api(f):
    """Decorator to validate and sanitize external API requests."""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_name = request.headers.get('API-Name', '')
        if not validate_api_request(api_name):
            logger.warning(f"Unauthorized API access attempt: {api_name}")
            return jsonify({"error": "Unauthorized API access"}), 403
        return f(*args, **kwargs)
    return decorated

# Example usage of these decorators
@input_sanitization_required
@suspicious_activity_monitor
@enforce_content_security
@secure_headers
@validate_external_api
def protected_route():
    """A protected route example with comprehensive security checks."""
    return jsonify({"message": "This route is protected with security checks."})

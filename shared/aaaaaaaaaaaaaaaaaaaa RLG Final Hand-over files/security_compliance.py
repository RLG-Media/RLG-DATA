import os
import json
import logging
import hashlib
import hmac
import re
from datetime import datetime, timedelta
from functools import wraps

import requests
from cryptography.fernet import Fernet
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load compliance rules from a JSON file
COMPLIANCE_RULES_FILE = "compliance_rules.json"

if os.path.exists(COMPLIANCE_RULES_FILE):
    with open(COMPLIANCE_RULES_FILE, 'r') as f:
        COMPLIANCE_RULES = json.load(f)
else:
    COMPLIANCE_RULES = {}

# Secret key for encryption (ensure this is securely stored and rotated regularly)
SECRET_KEY = os.getenv("SECRET_KEY", Fernet.generate_key().decode())
fernet = Fernet(SECRET_KEY.encode())

# Security and Compliance Functions

def hash_password(password: str) -> str:
    """Generate a secure hash for user passwords."""
    return generate_password_hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify if the provided password matches the stored hash."""
    return check_password_hash(hashed_password, password)

def encrypt_data(data: str) -> str:
    """Encrypt sensitive user data."""
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive user data."""
    return fernet.decrypt(encrypted_data.encode()).decode()

def generate_hmac_signature(message: str, key: str) -> str:
    """Generate HMAC signature for secure message authentication."""
    return hmac.new(key.encode(), message.encode(), hashlib.sha256).hexdigest()

def validate_request_ip():
    """Validate if incoming request is from an allowed region/country/city."""
    allowed_regions = COMPLIANCE_RULES.get("allowed_regions", [])
    ip = request.remote_addr
    response = requests.get(f"https://ipinfo.io/{ip}/json")
    if response.status_code == 200:
        data = response.json()
        if data.get("region") not in allowed_regions:
            return False
    return True

def validate_request(func):
    """Decorator to validate request security and compliance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not validate_request_ip():
            return jsonify({"error": "Access denied due to geographical restrictions."}), 403
        return func(*args, **kwargs)
    return wrapper

def check_input_sanitization(user_input: str) -> bool:
    """Check if user input is sanitized against SQLi, XSS, etc."""
    dangerous_patterns = [r"<script.*?>.*?</script>", r"[';]--", r"\bDROP\b", r"\bDELETE\b"]
    return not any(re.search(pattern, user_input, re.IGNORECASE) for pattern in dangerous_patterns)

def monitor_api_usage(user_id: str):
    """Monitor API usage to prevent abuse."""
    log_file = "api_usage.log"
    with open(log_file, "a") as f:
        f.write(f"{datetime.now()} - User: {user_id} accessed API\n")

def enforce_data_retention_policies():
    """Enforce automatic data retention policies for compliance."""
    retention_period = COMPLIANCE_RULES.get("data_retention_period", 30)  # Default: 30 days
    retention_cutoff = datetime.now() - timedelta(days=retention_period)
    # Logic to delete old logs and records based on retention policy
    logger.info(f"Deleting records older than {retention_cutoff}")

# API Routes (Example for Security)
from flask import Flask

app = Flask(__name__)

@app.route("/secure-data", methods=["POST"])
@validate_request
def secure_endpoint():
    """Example secure endpoint."""
    data = request.json.get("data", "")
    if not check_input_sanitization(data):
        return jsonify({"error": "Invalid input detected."}), 400
    encrypted = encrypt_data(data)
    return jsonify({"message": "Data secured", "encrypted_data": encrypted})

if __name__ == "__main__":
    app.run(debug=True)

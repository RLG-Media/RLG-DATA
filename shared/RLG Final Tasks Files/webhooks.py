"""
webhooks.py

This module defines webhook endpoints for both RLG Data and RLG Fans. It uses Flask's Blueprint
to create modular endpoints that can receive JSON payloads from external systems. The module includes
optional HMAC-SHA256 signature verification to ensure that only authorized payloads are processed.
"""

import os
import hmac
import hashlib
import logging
from flask import Blueprint, request, jsonify

# Configure logging
logger = logging.getLogger("Webhooks")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Create a Flask Blueprint for webhook endpoints.
webhooks_bp = Blueprint("webhooks", __name__, url_prefix="/webhooks")

# Webhook secret for verifying payload signatures.
# In production, store this securely in an environment variable.
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "your_webhook_secret")

def verify_signature(payload: bytes, signature: str) -> bool:
    """
    Verifies the HMAC-SHA256 signature of the payload.

    Parameters:
        payload (bytes): The raw request payload.
        signature (str): The signature provided in the request header (hex string).

    Returns:
        bool: True if the computed signature matches the provided signature; False otherwise.
    """
    computed_hmac = hmac.new(WEBHOOK_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    valid = hmac.compare_digest(computed_hmac, signature)
    if not valid:
        logger.debug("Computed HMAC: %s; Provided signature: %s", computed_hmac, signature)
    return valid

@webhooks_bp.route("/rlg_data", methods=["POST"])
def rlg_data_webhook():
    """
    Endpoint to receive webhook payloads for RLG Data (media articles).

    Expects:
        - JSON payload in the request body.
        - Optional header "X-Hub-Signature-256" containing the HMAC-SHA256 signature.
    
    Returns:
        JSON response indicating success or error.
    """
    payload = request.get_data()
    signature_header = request.headers.get("X-Hub-Signature-256", "")
    
    if signature_header:
        # Expected format: "sha256=<signature_value>".
        try:
            provided_signature = signature_header.split("=")[-1]
        except Exception as e:
            logger.error("Error parsing signature header: %s", e)
            return jsonify({"error": "Invalid signature header format"}), 400

        if not verify_signature(payload, provided_signature):
            logger.warning("Invalid webhook signature for RLG Data.")
            return jsonify({"error": "Invalid signature"}), 403

    try:
        data = request.get_json()
        logger.info("Received RLG Data webhook payload: %s", data)
        # TODO: Insert processing logic here.
        # For example, update the database, trigger a background job, etc.
        return jsonify({"status": "RLG Data webhook received successfully"}), 200
    except Exception as e:
        logger.error("Error processing RLG Data webhook: %s", e)
        return jsonify({"error": "Internal server error"}), 500

@webhooks_bp.route("/rlg_fans", methods=["POST"])
def rlg_fans_webhook():
    """
    Endpoint to receive webhook payloads for RLG Fans (social posts).

    Expects:
        - JSON payload in the request body.
        - Optional header "X-Hub-Signature-256" containing the HMAC-SHA256 signature.
    
    Returns:
        JSON response indicating success or error.
    """
    payload = request.get_data()
    signature_header = request.headers.get("X-Hub-Signature-256", "")
    
    if signature_header:
        try:
            provided_signature = signature_header.split("=")[-1]
        except Exception as e:
            logger.error("Error parsing signature header: %s", e)
            return jsonify({"error": "Invalid signature header format"}), 400

        if not verify_signature(payload, provided_signature):
            logger.warning("Invalid webhook signature for RLG Fans.")
            return jsonify({"error": "Invalid signature"}), 403

    try:
        data = request.get_json()
        logger.info("Received RLG Fans webhook payload: %s", data)
        # TODO: Insert processing logic here.
        # For example, update fan engagement statistics or trigger a background task.
        return jsonify({"status": "RLG Fans webhook received successfully"}), 200
    except Exception as e:
        logger.error("Error processing RLG Fans webhook: %s", e)
        return jsonify({"error": "Internal server error"}), 500

# -------------------------------
# Additional Recommendations:
# -------------------------------
# 1. **Authentication & Authorization:** Enhance security by integrating additional authentication
#    measures if necessary (e.g., IP whitelisting, OAuth tokens).
# 2. **Payload Validation:** Validate incoming JSON payloads against a schema to ensure required fields are present.
# 3. **Asynchronous Processing:** For heavy processing tasks, consider offloading work to an asynchronous task queue (e.g., Celery).
# 4. **Logging & Monitoring:** Persist logs to a file or external logging system, and integrate with monitoring tools.
# 5. **Region-Specific Routing:** If webhooks include region-specific information, add logic to route processing accordingly.

# -------------------------------
# Standalone Testing
# -------------------------------
if __name__ == "__main__":
    from flask import Flask

    app = Flask(__name__)
    app.register_blueprint(webhooks_bp)

    # For standalone testing, run the Flask development server.
    app.run(host="0.0.0.0", port=5004, debug=True)

import json
from flask import Flask, request, jsonify, abort
from functools import wraps
import logging
import hmac
import hashlib
from config import WEBHOOK_SECRET_KEY

app = Flask(__name__)

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Webhook verification decorator
def verify_signature(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        signature = request.headers.get("X-Signature")
        if not signature:
            logger.error("Missing webhook signature.")
            abort(400, description="Missing signature header.")

        payload = request.get_data()
        calculated_signature = hmac.new(
            WEBHOOK_SECRET_KEY.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(calculated_signature, signature):
            logger.error("Invalid webhook signature.")
            abort(400, description="Invalid signature.")

        return func(*args, **kwargs)
    return wrapper

@app.route('/webhooks', methods=['POST'])
@verify_signature
def handle_webhook():
    try:
        # Parse incoming JSON payload
        event = request.get_json()
        if not event:
            logger.error("Invalid JSON payload.")
            abort(400, description="Invalid JSON payload.")

        event_type = event.get('event_type')
        event_data = event.get('data', {})

        logger.info(f"Received webhook event: {event_type}")

        # Route event to the appropriate handler
        if event_type == "platform_update":
            handle_platform_update(event_data)
        elif event_type == "user_subscription":
            handle_user_subscription(event_data)
        elif event_type == "content_posted":
            handle_content_posted(event_data)
        else:
            logger.warning(f"Unhandled webhook event type: {event_type}")

        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}", exc_info=True)
        abort(500, description="Internal Server Error")

# Example webhook handlers
def handle_platform_update(data):
    logger.info(f"Handling platform update: {data}")
    # Add logic for platform updates here
    # Example: Sync platform data, notify users, etc.

def handle_user_subscription(data):
    logger.info(f"Handling user subscription: {data}")
    # Add logic for user subscription events
    # Example: Update database, send confirmation email, etc.

def handle_content_posted(data):
    logger.info(f"Handling new content posted: {data}")
    # Add logic for content posted events
    # Example: Update content feed, notify followers, etc.

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

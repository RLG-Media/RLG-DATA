import json
import logging
from flask import Blueprint, request, jsonify
from werkzeug.exceptions import BadRequest

# Initialize Blueprint
webhook_handlers = Blueprint("webhook_handlers", __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Webhook endpoint routes
@webhook_handlers.route("/webhook/<service>", methods=["POST"])
def handle_webhook(service):
    """
    Handle incoming webhook events for various services.
    :param service: The name of the service sending the webhook.
    """
    try:
        # Log the service receiving the webhook
        logger.info(f"Received webhook from service: {service}")

        # Validate request content type
        if request.content_type != "application/json":
            logger.warning("Invalid content type.")
            raise BadRequest("Invalid content type. Expected application/json.")

        # Parse incoming JSON payload
        payload = request.get_json()
        logger.debug(f"Payload received: {json.dumps(payload, indent=2)}")

        # Dispatch based on service
        if service == "payment_gateway":
            return handle_payment_gateway_event(payload)
        elif service == "messaging_platform":
            return handle_messaging_platform_event(payload)
        elif service == "analytics":
            return handle_analytics_event(payload)
        else:
            logger.warning(f"Unhandled service: {service}")
            return jsonify({"error": f"Unhandled service: {service}"}), 400

    except BadRequest as e:
        logger.error(f"BadRequest: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500


# Handlers for specific services
def handle_payment_gateway_event(payload):
    """
    Process events from a payment gateway.
    """
    event_type = payload.get("event_type")
    logger.info(f"Processing payment gateway event: {event_type}")

    if event_type == "payment_success":
        process_payment_success(payload)
    elif event_type == "payment_failure":
        process_payment_failure(payload)
    else:
        logger.warning(f"Unhandled event type: {event_type}")
        return jsonify({"status": "unhandled event"}), 200

    return jsonify({"status": "success"}), 200


def handle_messaging_platform_event(payload):
    """
    Process events from a messaging platform.
    """
    message_type = payload.get("message_type")
    logger.info(f"Processing messaging platform event: {message_type}")

    if message_type == "new_message":
        process_new_message(payload)
    elif message_type == "user_typing":
        process_user_typing(payload)
    else:
        logger.warning(f"Unhandled message type: {message_type}")
        return jsonify({"status": "unhandled event"}), 200

    return jsonify({"status": "success"}), 200


def handle_analytics_event(payload):
    """
    Process events related to analytics updates.
    """
    event_type = payload.get("event_type")
    logger.info(f"Processing analytics event: {event_type}")

    if event_type == "data_update":
        process_data_update(payload)
    else:
        logger.warning(f"Unhandled analytics event type: {event_type}")
        return jsonify({"status": "unhandled event"}), 200

    return jsonify({"status": "success"}), 200


# Utility Functions
def process_payment_success(payload):
    """
    Handle a successful payment event.
    """
    logger.info("Processing payment success.")
    user_id = payload.get("user_id")
    amount = payload.get("amount")
    # Add business logic for handling successful payments
    logger.info(f"User {user_id} paid {amount}.")


def process_payment_failure(payload):
    """
    Handle a failed payment event.
    """
    logger.info("Processing payment failure.")
    user_id = payload.get("user_id")
    error_message = payload.get("error_message")
    # Add business logic for handling failed payments
    logger.error(f"Payment failed for user {user_id}: {error_message}")


def process_new_message(payload):
    """
    Handle a new message event from a messaging platform.
    """
    logger.info("Processing new message.")
    sender_id = payload.get("sender_id")
    message_content = payload.get("content")
    # Add business logic for handling new messages
    logger.info(f"Message from {sender_id}: {message_content}")


def process_user_typing(payload):
    """
    Handle a user typing event.
    """
    logger.info("Processing user typing event.")
    user_id = payload.get("user_id")
    # Add business logic for handling typing events
    logger.info(f"User {user_id} is typing...")


def process_data_update(payload):
    """
    Handle a data update event from an analytics service.
    """
    logger.info("Processing data update event.")
    update_details = payload.get("update_details")
    # Add business logic for handling data updates
    logger.info(f"Data update received: {update_details}")


# Error Handlers
@webhook_handlers.errorhandler(400)
def bad_request_error(e):
    """
    Handle 400 Bad Request errors.
    """
    logger.error(f"400 Bad Request: {e}")
    return jsonify({"error": "Bad request."}), 400


@webhook_handlers.errorhandler(500)
def internal_server_error(e):
    """
    Handle 500 Internal Server errors.
    """
    logger.error(f"500 Internal Server Error: {e}")
    return jsonify({"error": "Internal server error."}), 500

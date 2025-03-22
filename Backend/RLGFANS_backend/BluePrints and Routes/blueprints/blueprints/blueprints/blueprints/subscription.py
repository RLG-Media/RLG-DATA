# subscription.py - Subscription management for RLG Fans

from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import jwt_required, get_jwt_identity
import stripe
import logging
from config import Config
from models import User, Subscription
from app import db

# Initialize Blueprint
subscription_bp = Blueprint('subscription', __name__)
stripe.api_key = Config.STRIPE_SECRET_KEY

# Set up logging
logging.basicConfig(filename='subscription.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')

@subscription_bp.route('/create', methods=['POST'])
@jwt_required()
def create_subscription():
    """
    Endpoint to create a new subscription.
    Requires Stripe price_id in request body.
    """
    try:
        user_id = get_jwt_identity()
        price_id = request.json.get('price_id')

        if not price_id:
            return jsonify({"error": "Price ID is required"}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Create Stripe Checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=user.stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{'price': price_id, 'quantity': 1}],
            mode='subscription',
            success_url=Config.SUCCESS_URL,
            cancel_url=Config.CANCEL_URL,
        )

        # Log successful creation
        logging.info(f"Subscription created for user {user_id} with session {checkout_session['id']}")

        return jsonify({"checkout_url": checkout_session.url}), 200

    except Exception as e:
        logging.error(f"Failed to create subscription: {str(e)}")
        return jsonify({"error": "Failed to create subscription"}), 500


@subscription_bp.route('/status', methods=['GET'])
@jwt_required()
def get_subscription_status():
    """
    Endpoint to retrieve the subscription status of the current user.
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or not user.stripe_subscription_id:
            return jsonify({"status": "inactive"}), 200

        subscription = stripe.Subscription.retrieve(user.stripe_subscription_id)
        logging.info(f"Retrieved subscription status for user {user_id}")

        return jsonify({"status": subscription.status}), 200

    except Exception as e:
        logging.error(f"Failed to retrieve subscription status: {str(e)}")
        return jsonify({"error": "Failed to retrieve subscription status"}), 500


@subscription_bp.route('/cancel', methods=['DELETE'])
@jwt_required()
def cancel_subscription():
    """
    Endpoint to cancel the subscription of the current user.
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or not user.stripe_subscription_id:
            return jsonify({"error": "No active subscription found"}), 404

        # Cancel the Stripe subscription
        stripe.Subscription.modify(
            user.stripe_subscription_id,
            cancel_at_period_end=True
        )

        # Update the local subscription status
        user.subscription_status = 'canceled'
        db.session.commit()

        logging.info(f"Subscription canceled for user {user_id}")
        return jsonify({"message": "Subscription canceled"}), 200

    except Exception as e:
        logging.error(f"Failed to cancel subscription: {str(e)}")
        return jsonify({"error": "Failed to cancel subscription"}), 500


@subscription_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """
    Stripe webhook to handle events related to subscription lifecycle.
    """
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, Config.STRIPE_WEBHOOK_SECRET)

        if event['type'] == 'invoice.payment_succeeded':
            handle_payment_success(event['data']['object'])
        elif event['type'] == 'customer.subscription.deleted':
            handle_subscription_canceled(event['data']['object'])

        logging.info(f"Webhook event received: {event['type']}")
        return jsonify({"status": "success"}), 200

    except Exception as e:
        logging.error(f"Webhook signature verification failed: {str(e)}")
        return jsonify({"error": "Webhook verification failed"}), 400


def handle_payment_success(invoice):
    """
    Handle successful payment by updating the user's subscription status.
    """
    try:
        user = User.query.filter_by(stripe_customer_id=invoice['customer']).first()
        if user:
            user.subscription_status = 'active'
            db.session.commit()
            logging.info(f"Subscription activated for user {user.id}")
    except Exception as e:
        logging.error(f"Failed to handle payment success: {str(e)}")


def handle_subscription_canceled(subscription):
    """
    Handle subscription cancellation event by updating the user's subscription status.
    """
    try:
        user = User.query.filter_by(stripe_customer_id=subscription['customer']).first()
        if user:
            user.subscription_status = 'canceled'
            db.session.commit()
            logging.info(f"Subscription canceled for user {user.id}")
    except Exception as e:
        logging.error(f"Failed to handle subscription cancellation: {str(e)}")

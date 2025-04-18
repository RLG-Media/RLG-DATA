# stripe.py

import stripe
import logging
from flask import current_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StripeService:
    """
    A service class for managing Stripe integrations, including subscriptions, payments, and invoices.
    """

    def __init__(self, api_key):
        """
        Initialize the StripeService with the provided API key.
        :param api_key: Stripe Secret Key
        """
        stripe.api_key = api_key
        logger.info("StripeService initialized.")

    def create_customer(self, email, payment_method_id):
        """
        Creates a new customer in Stripe.
        :param email: Customer email address.
        :param payment_method_id: Stripe payment method ID.
        :return: Stripe Customer object.
        """
        try:
            logger.info(f"Creating customer with email: {email}")
            customer = stripe.Customer.create(
                email=email,
                payment_method=payment_method_id,
                invoice_settings={"default_payment_method": payment_method_id},
            )
            logger.info(f"Customer created successfully: {customer['id']}")
            return customer
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error while creating customer: {str(e)}")
            raise

    def create_subscription(self, customer_id, price_id):
        """
        Creates a subscription for a customer.
        :param customer_id: Stripe Customer ID.
        :param price_id: Stripe Price ID for the subscription plan.
        :return: Stripe Subscription object.
        """
        try:
            logger.info(f"Creating subscription for customer {customer_id} with price {price_id}")
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                expand=["latest_invoice.payment_intent"],
            )
            logger.info(f"Subscription created successfully: {subscription['id']}")
            return subscription
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error while creating subscription: {str(e)}")
            raise

    def cancel_subscription(self, subscription_id):
        """
        Cancels an active subscription.
        :param subscription_id: Stripe Subscription ID.
        :return: Stripe Subscription object after cancellation.
        """
        try:
            logger.info(f"Cancelling subscription: {subscription_id}")
            subscription = stripe.Subscription.delete(subscription_id)
            logger.info(f"Subscription cancelled successfully: {subscription['id']}")
            return subscription
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error while cancelling subscription: {str(e)}")
            raise

    def retrieve_customer(self, customer_id):
        """
        Retrieves customer information from Stripe.
        :param customer_id: Stripe Customer ID.
        :return: Stripe Customer object.
        """
        try:
            logger.info(f"Retrieving customer: {customer_id}")
            customer = stripe.Customer.retrieve(customer_id)
            logger.info(f"Customer retrieved successfully: {customer['id']}")
            return customer
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error while retrieving customer: {str(e)}")
            raise

    def retrieve_subscription(self, subscription_id):
        """
        Retrieves subscription information from Stripe.
        :param subscription_id: Stripe Subscription ID.
        :return: Stripe Subscription object.
        """
        try:
            logger.info(f"Retrieving subscription: {subscription_id}")
            subscription = stripe.Subscription.retrieve(subscription_id)
            logger.info(f"Subscription retrieved successfully: {subscription['id']}")
            return subscription
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error while retrieving subscription: {str(e)}")
            raise

    def handle_webhook(self, payload, sig_header, endpoint_secret):
        """
        Handles Stripe webhook events.
        :param payload: Webhook payload as JSON string.
        :param sig_header: Stripe signature header.
        :param endpoint_secret: Webhook endpoint secret.
        :return: Stripe Event object.
        """
        try:
            logger.info("Verifying Stripe webhook signature.")
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
            logger.info(f"Webhook verified. Event type: {event['type']}")
            return event
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Webhook signature verification failed: {str(e)}")
            raise
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error while handling webhook: {str(e)}")
            raise


# Example Usage (if needed for debugging or testing)
if __name__ == "__main__":
    stripe_service = StripeService(api_key="your_stripe_secret_key")

    # Example: Create a customer
    try:
        customer = stripe_service.create_customer(
            email="example@example.com",
            payment_method_id="pm_card_visa"
        )
        print(customer)
    except Exception as e:
        print(f"Error: {str(e)}")

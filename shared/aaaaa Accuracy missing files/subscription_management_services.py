import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("subscription_management_services.log"),
        logging.StreamHandler()
    ]
)

class SubscriptionManagementService:
    """
    Service for managing subscriptions for RLG Data and RLG Fans.
    Includes features for creating, updating, canceling, and monitoring subscriptions.
    """

    def __init__(self):
        self.subscriptions = {}  # Mock database of subscriptions
        logging.info("SubscriptionManagementService initialized.")

    def create_subscription(self, user_id: str, plan: str, start_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Create a new subscription for a user.

        Args:
            user_id (str): The ID of the user.
            plan (str): The subscription plan (e.g., "Creator", "Pro", "Enterprise").
            start_date (Optional[datetime]): The start date of the subscription (default: today).

        Returns:
            Dict[str, Any]: Details of the created subscription.
        """
        start_date = start_date or datetime.now()
        subscription_id = f"sub_{len(self.subscriptions) + 1}"

        subscription = {
            "subscription_id": subscription_id,
            "user_id": user_id,
            "plan": plan,
            "start_date": start_date,
            "end_date": start_date + timedelta(days=30),
            "status": "active",
            "created_at": datetime.now()
        }
        self.subscriptions[subscription_id] = subscription
        logging.info("Created subscription: %s", subscription)
        return subscription

    def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """
        Cancel an active subscription.

        Args:
            subscription_id (str): The ID of the subscription to cancel.

        Returns:
            Dict[str, Any]: Details of the canceled subscription.
        """
        if subscription_id not in self.subscriptions:
            logging.error("Subscription ID %s not found.", subscription_id)
            raise ValueError("Subscription not found.")

        subscription = self.subscriptions[subscription_id]
        subscription["status"] = "canceled"
        subscription["canceled_at"] = datetime.now()
        logging.info("Canceled subscription: %s", subscription)
        return subscription

    def renew_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """
        Renew an expired subscription.

        Args:
            subscription_id (str): The ID of the subscription to renew.

        Returns:
            Dict[str, Any]: Details of the renewed subscription.
        """
        if subscription_id not in self.subscriptions:
            logging.error("Subscription ID %s not found.", subscription_id)
            raise ValueError("Subscription not found.")

        subscription = self.subscriptions[subscription_id]
        if subscription["status"] != "expired":
            logging.error("Subscription ID %s is not expired.", subscription_id)
            raise ValueError("Only expired subscriptions can be renewed.")

        subscription["status"] = "active"
        subscription["start_date"] = datetime.now()
        subscription["end_date"] = datetime.now() + timedelta(days=30)
        logging.info("Renewed subscription: %s", subscription)
        return subscription

    def monitor_subscriptions(self) -> List[Dict[str, Any]]:
        """
        Monitor all subscriptions and update statuses (e.g., expired).

        Returns:
            List[Dict[str, Any]]: List of updated subscriptions.
        """
        now = datetime.now()
        updated_subscriptions = []

        for subscription in self.subscriptions.values():
            if subscription["status"] == "active" and subscription["end_date"] < now:
                subscription["status"] = "expired"
                updated_subscriptions.append(subscription)

        logging.info("Monitored subscriptions: %d updated.", len(updated_subscriptions))
        return updated_subscriptions

    def get_subscription_details(self, subscription_id: str) -> Dict[str, Any]:
        """
        Retrieve details of a specific subscription.

        Args:
            subscription_id (str): The ID of the subscription.

        Returns:
            Dict[str, Any]: Subscription details.
        """
        if subscription_id not in self.subscriptions:
            logging.error("Subscription ID %s not found.", subscription_id)
            raise ValueError("Subscription not found.")

        subscription = self.subscriptions[subscription_id]
        logging.info("Retrieved subscription details: %s", subscription)
        return subscription

    def generate_subscription_report(self) -> List[Dict[str, Any]]:
        """
        Generate a report of all subscriptions.

        Returns:
            List[Dict[str, Any]]: List of all subscriptions with details.
        """
        report = list(self.subscriptions.values())
        logging.info("Generated subscription report: %d subscriptions.", len(report))
        return report

# Example usage
if __name__ == "__main__":
    subscription_service = SubscriptionManagementService()

    # Create subscriptions
    sub1 = subscription_service.create_subscription(user_id="user_123", plan="Pro")
    sub2 = subscription_service.create_subscription(user_id="user_456", plan="Creator")

    # Cancel a subscription
    subscription_service.cancel_subscription(sub1["subscription_id"])

    # Renew a subscription
    sub2["status"] = "expired"  # Simulate expiration
    subscription_service.renew_subscription(sub2["subscription_id"])

    # Monitor subscriptions
    subscription_service.monitor_subscriptions()

    # Generate subscription report
    report = subscription_service.generate_subscription_report()
    print("Subscription Report:", report)

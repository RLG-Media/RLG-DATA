from datetime import datetime, timedelta
from typing import Optional

class SubscriptionService:
    """
    Manages subscription plans, pricing, and user subscriptions for RLG Data and RLG Fans.
    """

    def __init__(self):
        self.subscription_plans = {
            "global": {
                "monthly": 59.00,
                "weekly": 15.00,
            },
            "israel": {
                "monthly": 99.00,
                "weekly": 35.00,
            },
        }
        self.subscriptions = {}  # Format: {user_id: {'plan': str, 'expires_at': datetime}}
        self.discount_coupons = {}  # Format: {coupon_code: {'discount': float, 'expires_at': datetime}}

    def get_pricing(self, region: str) -> dict:
        """
        Retrieve subscription pricing for a specific region.

        Args:
            region (str): The user's region (e.g., 'global', 'israel').

        Returns:
            dict: Pricing information for the specified region.
        """
        pricing = self.subscription_plans.get(region.lower(), self.subscription_plans["global"])
        print(f"[{datetime.now()}] Retrieved pricing for region: {region}.")
        return pricing

    def create_subscription(self, user_id: str, plan: str, region: str, duration: str = "monthly", coupon_code: Optional[str] = None) -> bool:
        """
        Create a subscription for a user.

        Args:
            user_id (str): The ID of the user.
            plan (str): The subscription plan name (e.g., 'basic', 'pro').
            region (str): The user's region.
            duration (str): The duration of the subscription ('monthly' or 'weekly').
            coupon_code (Optional[str]): A discount coupon code (if available).

        Returns:
            bool: True if the subscription was successfully created, False otherwise.
        """
        pricing = self.get_pricing(region)
        if duration not in pricing:
            print(f"[{datetime.now()}] Invalid subscription duration: {duration}.")
            return False

        price = pricing[duration]
        if coupon_code:
            price = self.apply_coupon(coupon_code, price)

        # Simulate subscription creation
        expires_at = datetime.now() + (timedelta(days=30) if duration == "monthly" else timedelta(days=7))
        self.subscriptions[user_id] = {
            "plan": plan,
            "price": price,
            "region": region,
            "expires_at": expires_at,
        }
        print(f"[{datetime.now()}] Created subscription for user {user_id}: {plan}, {duration}, ${price}. Expires at {expires_at}.")
        return True

    def apply_coupon(self, coupon_code: str, price: float) -> float:
        """
        Apply a discount coupon to the subscription price.

        Args:
            coupon_code (str): The discount coupon code.
            price (float): The original price.

        Returns:
            float: The discounted price.
        """
        coupon = self.discount_coupons.get(coupon_code)
        if not coupon:
            print(f"[{datetime.now()}] Invalid coupon code: {coupon_code}.")
            return price

        if datetime.now() > coupon["expires_at"]:
            print(f"[{datetime.now()}] Coupon code {coupon_code} has expired.")
            return price

        discount = coupon["discount"]
        discounted_price = max(price - discount, 0)  # Ensure price doesn't go below 0
        print(f"[{datetime.now()}] Applied coupon {coupon_code}: Original price ${price}, Discounted price ${discounted_price}.")
        return discounted_price

    def check_subscription_status(self, user_id: str) -> Optional[dict]:
        """
        Check the status of a user's subscription.

        Args:
            user_id (str): The ID of the user.

        Returns:
            Optional[dict]: Subscription details if active, None if no active subscription.
        """
        subscription = self.subscriptions.get(user_id)
        if not subscription or datetime.now() > subscription["expires_at"]:
            print(f"[{datetime.now()}] No active subscription found for user {user_id}.")
            return None

        print(f"[{datetime.now()}] Active subscription found for user {user_id}: {subscription}.")
        return subscription

    def cancel_subscription(self, user_id: str) -> bool:
        """
        Cancel a user's subscription.

        Args:
            user_id (str): The ID of the user.

        Returns:
            bool: True if the subscription was successfully canceled, False otherwise.
        """
        if user_id not in self.subscriptions:
            print(f"[{datetime.now()}] No subscription to cancel for user {user_id}.")
            return False

        del self.subscriptions[user_id]
        print(f"[{datetime.now()}] Subscription canceled for user {user_id}.")
        return True

    def add_discount_coupon(self, coupon_code: str, discount: float, expires_in_days: int):
        """
        Add a discount coupon.

        Args:
            coupon_code (str): The coupon code.
            discount (float): The discount amount.
            expires_in_days (int): The number of days until the coupon expires.
        """
        expires_at = datetime.now() + timedelta(days=expires_in_days)
        self.discount_coupons[coupon_code] = {
            "discount": discount,
            "expires_at": expires_at,
        }
        print(f"[{datetime.now()}] Added discount coupon {coupon_code}: ${discount} off, expires at {expires_at}.")

# Example Usage
if __name__ == "__main__":
    subscription_service = SubscriptionService()

    # Add a discount coupon
    subscription_service.add_discount_coupon("WELCOME10", 10.00, expires_in_days=30)

    # Create a subscription
    subscription_service.create_subscription(user_id="user123", plan="pro", region="global", duration="monthly", coupon_code="WELCOME10")

    # Check subscription status
    subscription_service.check_subscription_status("user123")

    # Cancel subscription
    subscription_service.cancel_subscription("user123")

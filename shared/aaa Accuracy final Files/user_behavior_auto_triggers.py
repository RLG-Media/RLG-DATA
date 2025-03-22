import logging
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("user_behavior_auto_triggers.log"),
        logging.StreamHandler(),
    ],
)

class UserBehaviorAutoTriggers:
    """
    A service for automating triggers based on user behavior across RLG Data and RLG Fans.
    """

    def __init__(self):
        self.triggers: Dict[str, Callable] = {}
        self.user_activity_log: List[Dict] = []
        logging.info("UserBehaviorAutoTriggers initialized.")

    def register_trigger(self, name: str, trigger_function: Callable):
        """
        Register a new behavior-based trigger.

        Args:
            name: The name of the trigger.
            trigger_function: A callable that executes the trigger.
        """
        self.triggers[name] = trigger_function
        logging.info("Trigger '%s' registered.", name)

    def log_user_activity(self, user_id: str, activity_type: str, timestamp: Optional[datetime] = None):
        """
        Log a user activity.

        Args:
            user_id: The unique ID of the user.
            activity_type: The type of activity performed (e.g., "login", "content_view").
            timestamp: The timestamp of the activity (default is now).
        """
        activity = {
            "user_id": user_id,
            "activity_type": activity_type,
            "timestamp": timestamp or datetime.now(),
        }
        self.user_activity_log.append(activity)
        logging.info("Logged activity: %s", activity)

    def evaluate_triggers(self, user_id: str):
        """
        Evaluate all triggers for a specific user based on their recent activity.

        Args:
            user_id: The unique ID of the user.
        """
        recent_activities = [
            activity for activity in self.user_activity_log
            if activity["user_id"] == user_id and activity["timestamp"] >= datetime.now() - timedelta(days=7)
        ]
        logging.info("Evaluating triggers for user '%s' with %d recent activities.", user_id, len(recent_activities))

        for name, trigger_function in self.triggers.items():
            try:
                trigger_function(user_id, recent_activities)
                logging.info("Trigger '%s' executed for user '%s'.", name, user_id)
            except Exception as e:
                logging.error("Error executing trigger '%s' for user '%s': %s", name, user_id, e)

    def automated_engagement_email(self, user_id: str, recent_activities: List[Dict]):
        """
        Example trigger: Send an engagement email if the user is inactive for 3+ days.
        """
        last_activity = max(recent_activities, key=lambda x: x["timestamp"], default=None)
        if last_activity and (datetime.now() - last_activity["timestamp"]).days >= 3:
            logging.info("Sending engagement email to user '%s'.", user_id)
            # Simulate sending an email (implement actual email logic here)

    def recommend_relevant_content(self, user_id: str, recent_activities: List[Dict]):
        """
        Example trigger: Recommend content based on user behavior.
        """
        activity_types = [activity["activity_type"] for activity in recent_activities]
        if "content_view" in activity_types:
            logging.info("Recommending relevant content to user '%s'.", user_id)
            # Simulate recommending content (implement actual recommendation logic here)

    def promote_social_media_activity(self, user_id: str, recent_activities: List[Dict]):
        """
        Example trigger: Promote activity on social media platforms.
        """
        if not any(activity["activity_type"] == "social_share" for activity in recent_activities):
            logging.info("Promoting social media activity for user '%s'.", user_id)
            # Simulate promoting social media activity (implement actual logic here)

# Example usage
if __name__ == "__main__":
    triggers = UserBehaviorAutoTriggers()

    # Register example triggers
    triggers.register_trigger("Engagement Email", triggers.automated_engagement_email)
    triggers.register_trigger("Content Recommendation", triggers.recommend_relevant_content)
    triggers.register_trigger("Social Media Promotion", triggers.promote_social_media_activity)

    # Log some user activities
    triggers.log_user_activity(user_id="user123", activity_type="login")
    triggers.log_user_activity(user_id="user123", activity_type="content_view")
    triggers.log_user_activity(user_id="user123", activity_type="social_share", timestamp=datetime.now() - timedelta(days=4))

    # Evaluate triggers for the user
    triggers.evaluate_triggers(user_id="user123")

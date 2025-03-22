import logging
from datetime import datetime
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("user_activity_tracking.log"),
        logging.StreamHandler()
    ]
)

class UserActivityTrackingService:
    """
    Service for tracking user activities in RLG Data and RLG Fans.
    Tracks page visits, feature usage, social media interactions, and more.
    """

    def __init__(self):
        self.activities = []  # Mock database of activities
        logging.info("UserActivityTrackingService initialized.")

    def log_activity(self, user_id: str, activity_type: str, details: Optional[Dict[str, Any]] = None):
        """
        Log a user activity.

        Args:
            user_id (str): The ID of the user.
            activity_type (str): The type of activity (e.g., "page_visit", "file_download").
            details (Optional[Dict[str, Any]]): Additional details about the activity.

        Returns:
            None
        """
        activity = {
            "activity_id": len(self.activities) + 1,
            "user_id": user_id,
            "activity_type": activity_type,
            "details": details or {},
            "timestamp": datetime.now()
        }
        self.activities.append(activity)
        logging.info("Logged activity: %s", activity)

    def get_user_activities(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve activities for a specific user.

        Args:
            user_id (str): The ID of the user.

        Returns:
            List[Dict[str, Any]]: List of activities for the user.
        """
        user_activities = [activity for activity in self.activities if activity["user_id"] == user_id]
        logging.info("Retrieved %d activities for user %s.", len(user_activities), user_id)
        return user_activities

    def get_all_activities(self) -> List[Dict[str, Any]]:
        """
        Retrieve all logged activities.

        Returns:
            List[Dict[str, Any]]: List of all activities.
        """
        logging.info("Retrieved all activities: %d total.", len(self.activities))
        return self.activities

    def generate_activity_report(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a user activity report.

        Args:
            user_id (Optional[str]): The ID of the user to generate the report for. If None, generate a report for all users.

        Returns:
            Dict[str, Any]: Activity report including total counts and categorized activities.
        """
        activities = self.get_user_activities(user_id) if user_id else self.activities

        activity_summary = {}
        for activity in activities:
            activity_type = activity["activity_type"]
            activity_summary[activity_type] = activity_summary.get(activity_type, 0) + 1

        report = {
            "user_id": user_id,
            "total_activities": len(activities),
            "activity_summary": activity_summary,
            "generated_at": datetime.now().isoformat()
        }
        logging.info("Generated activity report: %s", report)
        return report

# Example usage
if __name__ == "__main__":
    tracking_service = UserActivityTrackingService()

    # Log some activities
    tracking_service.log_activity(user_id="user_123", activity_type="page_visit", details={"page": "dashboard"})
    tracking_service.log_activity(user_id="user_123", activity_type="file_download", details={"file_name": "report.pdf"})
    tracking_service.log_activity(user_id="user_456", activity_type="social_media_post", details={"platform": "Twitter", "post_id": "12345"})

    # Retrieve activities for a user
    user_activities = tracking_service.get_user_activities("user_123")
    print("User Activities:", user_activities)

    # Generate a report for all users
    report = tracking_service.generate_activity_report()
    print("Activity Report:", report)

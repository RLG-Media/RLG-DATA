import logging
from typing import Dict, List, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("content_flagging_services.log"),
        logging.StreamHandler()
    ]
)

class ContentFlaggingService:
    """
    Service for flagging, reviewing, and managing inappropriate or harmful content.
    Supports automated and manual flagging across multiple platforms.
    """

    def __init__(self, platforms: Optional[List[str]] = None):
        """
        Initialize the content flagging service.

        Args:
            platforms: List of supported platforms (e.g., ["Facebook", "Twitter", "Instagram"]).
        """
        self.platforms = platforms or [
            "Facebook", "Twitter", "Instagram", "TikTok", "LinkedIn", "Pinterest",
            "Reddit", "Snapchat", "Threads"
        ]
        self.flagged_content = []  # In-memory storage for flagged content
        logging.info("ContentFlaggingService initialized for platforms: %s", self.platforms)

    def flag_content(self, platform: str, content_id: str, reason: str, flagged_by: Optional[str] = None) -> Dict:
        """
        Flag content for review.

        Args:
            platform: Platform where the content exists.
            content_id: ID of the content being flagged.
            reason: Reason for flagging the content.
            flagged_by: Optional user who flagged the content.

        Returns:
            A dictionary containing the flagging details.
        """
        if platform not in self.platforms:
            logging.error("Platform '%s' is not supported.", platform)
            return {"error": f"Platform '{platform}' is not supported."}

        flag_details = {
            "platform": platform,
            "content_id": content_id,
            "reason": reason,
            "flagged_by": flagged_by or "System",
            "flagged_at": datetime.utcnow().isoformat()
        }

        self.flagged_content.append(flag_details)
        logging.info("Content flagged: %s", flag_details)
        return flag_details

    def review_flagged_content(self, content_id: str) -> Optional[Dict]:
        """
        Review flagged content by content ID.

        Args:
            content_id: ID of the content to review.

        Returns:
            The flagged content details if found, or None.
        """
        for content in self.flagged_content:
            if content["content_id"] == content_id:
                logging.info("Flagged content reviewed: %s", content)
                return content

        logging.warning("Content with ID '%s' not found in flagged content.", content_id)
        return None

    def resolve_flagged_content(self, content_id: str, action: str, resolved_by: Optional[str] = None) -> Dict:
        """
        Resolve flagged content by taking appropriate action.

        Args:
            content_id: ID of the content to resolve.
            action: Action taken (e.g., "Remove", "Ignore", "Escalate").
            resolved_by: Optional user who resolved the content.

        Returns:
            A dictionary containing the resolution details.
        """
        for content in self.flagged_content:
            if content["content_id"] == content_id:
                resolution_details = {
                    "content_id": content_id,
                    "action": action,
                    "resolved_by": resolved_by or "System",
                    "resolved_at": datetime.utcnow().isoformat()
                }

                self.flagged_content.remove(content)
                logging.info("Flagged content resolved: %s", resolution_details)
                return resolution_details

        logging.warning("Content with ID '%s' not found for resolution.", content_id)
        return {"error": "Content not found."}

    def get_flagged_content_summary(self) -> Dict:
        """
        Get a summary of all flagged content.

        Returns:
            A dictionary containing the summary of flagged content by platform and reason.
        """
        summary = {}
        for content in self.flagged_content:
            platform = content["platform"]
            reason = content["reason"]
            summary.setdefault(platform, {}).setdefault(reason, 0)
            summary[platform][reason] += 1

        logging.info("Flagged content summary generated.")
        return summary

# Example usage
if __name__ == "__main__":
    service = ContentFlaggingService()

    # Flag content
    service.flag_content("Twitter", "12345", "Inappropriate language", flagged_by="user1")
    service.flag_content("Facebook", "67890", "Misinformation")

    # Review flagged content
    print(service.review_flagged_content("12345"))

    # Resolve flagged content
    print(service.resolve_flagged_content("12345", "Remove", resolved_by="admin"))

    # Get flagged content summary
    print(service.get_flagged_content_summary())

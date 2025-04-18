import logging
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("inbox.log")],
)

class InboxManager:
    """
    A class to manage inbox functionalities for RLG Data and RLG Fans.
    This includes fetching, organizing, filtering, and managing messages across platforms.
    """

    def __init__(self, integrations: Optional[Dict[str, object]] = None):
        self.integrations = integrations or {}
        logging.info("InboxManager initialized with integrations: %s", list(self.integrations.keys()))

    def fetch_messages(self, platform: str, filters: Optional[Dict] = None) -> List[Dict]:
        if platform not in self.integrations:
            logging.error("Platform %s is not integrated.", platform)
            raise ValueError(f"Platform {platform} is not integrated.")
        logging.info("Fetching messages from platform: %s with filters: %s", platform, filters)

        try:
            api_client = self.integrations[platform]
            messages = api_client.get_messages(filters=filters)
            logging.info("Fetched %d messages from %s", len(messages), platform)
            return messages
        except Exception as e:
            logging.error("Failed to fetch messages from %s: %s", platform, e)
            raise

    def organize_messages(self, messages: List[Dict], sort_key: str = "date", reverse: bool = True) -> List[Dict]:
        try:
            organized_messages = sorted(messages, key=lambda x: x.get(sort_key, ""), reverse=reverse)
            logging.info("Messages organized by %s in %s order.", sort_key, "descending" if reverse else "ascending")
            return organized_messages
        except Exception as e:
            logging.error("Failed to organize messages: %s", e)
            raise

    def filter_messages(self, messages: List[Dict], keyword: str) -> List[Dict]:
        filtered_messages = [msg for msg in messages if keyword.lower() in msg.get("content", "").lower()]
        logging.info("Filtered messages containing keyword '%s': %d found.", keyword, len(filtered_messages))
        return filtered_messages

    def mark_as_read(self, platform: str, message_ids: List[str]) -> Dict:
        if platform not in self.integrations:
            logging.error("Platform %s is not integrated.", platform)
            raise ValueError(f"Platform {platform} is not integrated.")
        logging.info("Marking messages as read on platform: %s", platform)

        try:
            api_client = self.integrations[platform]
            response = api_client.mark_messages_as_read(message_ids)
            logging.info("Marked %d messages as read on %s.", len(message_ids), platform)
            return response
        except Exception as e:
            logging.error("Failed to mark messages as read on %s: %s", platform, e)
            raise

    def delete_messages(self, platform: str, message_ids: List[str]) -> Dict:
        if platform not in self.integrations:
            logging.error("Platform %s is not integrated.", platform)
            raise ValueError(f"Platform {platform} is not integrated.")
        logging.info("Deleting messages on platform: %s", platform)

        try:
            api_client = self.integrations[platform]
            response = api_client.delete_messages(message_ids)
            logging.info("Deleted %d messages on %s.", len(message_ids), platform)
            return response
        except Exception as e:
            logging.error("Failed to delete messages on %s: %s", platform, e)
            raise

    def get_unread_count(self, platform: str) -> int:
        if platform not in self.integrations:
            logging.error("Platform %s is not integrated.", platform)
            raise ValueError(f"Platform {platform} is not integrated.")
        logging.info("Fetching unread message count for platform: %s", platform)

        try:
            api_client = self.integrations[platform]
            unread_count = api_client.get_unread_count()
            logging.info("Unread messages on %s: %d", platform, unread_count)
            return unread_count
        except Exception as e:
            logging.error("Failed to fetch unread message count on %s: %s", platform, e)
            raise

# Example usage
if __name__ == "__main__":
    try:
        example_integrations = {
            "slack": SlackClient(),  # Assume SlackClient is defined elsewhere
            "email": EmailClient(),  # Assume EmailClient is defined elsewhere
            "discord": DiscordClient(),  # Assume DiscordClient is defined elsewhere
        }

        inbox = InboxManager(integrations=example_integrations)

        slack_messages = inbox.fetch_messages("slack", filters={"date_range": "last_week"})

        organized_messages = inbox.organize_messages(slack_messages, sort_key="sender")

        filtered_messages = inbox.filter_messages(organized_messages, keyword="urgent")

        inbox.mark_as_read("slack", [msg["id"] for msg in filtered_messages])

        inbox.delete_messages("slack", [msg["id"] for msg in filtered_messages if msg["date"] < "2025-01-01"])

        unread_count = inbox.get_unread_count("slack")
        print(f"Unread messages on Slack: {unread_count}")

    except Exception as e:
        logging.error("An error occurred: %s", e)

# inbox_manager.py - Unified Inbox Management for RLG Data and RLG Fans

import logging
from datetime import datetime
from typing import List, Dict, Optional
from backend.db_helpers import get_db_session
from backend.models import InboxMessage, User
from backend.error_handlers import InboxError, DatabaseError
from backend.notifications import send_notification
from sqlalchemy.exc import SQLAlchemyError

# Logger configuration
logger = logging.getLogger("inbox_manager")
logger.setLevel(logging.INFO)


class InboxManager:
    """
    A class to manage unified inbox operations for RLG Data and RLG Fans.
    """

    def __init__(self, user_id: int):
        """
        Initialize the InboxManager with a specific user.

        Args:
            user_id (int): The ID of the user managing the inbox.
        """
        self.user_id = user_id
        self.db_session = get_db_session()

    def fetch_messages(
        self, filters: Optional[Dict[str, str]] = None, limit: int = 50, offset: int = 0
    ) -> List[Dict]:
        """
        Fetch messages from the inbox based on filters.

        Args:
            filters (Dict[str, str], optional): Filters such as message type, status, or sender.
            limit (int): Number of messages to fetch.
            offset (int): Offset for pagination.

        Returns:
            List[Dict]: List of messages.
        """
        try:
            query = self.db_session.query(InboxMessage).filter(InboxMessage.user_id == self.user_id)

            if filters:
                if "status" in filters:
                    query = query.filter(InboxMessage.status == filters["status"])
                if "type" in filters:
                    query = query.filter(InboxMessage.message_type == filters["type"])
                if "sender" in filters:
                    query = query.filter(InboxMessage.sender.contains(filters["sender"]))

            messages = query.order_by(InboxMessage.timestamp.desc()).limit(limit).offset(offset).all()

            result = [
                {
                    "id": message.id,
                    "sender": message.sender,
                    "content": message.content,
                    "status": message.status,
                    "type": message.message_type,
                    "timestamp": message.timestamp,
                }
                for message in messages
            ]

            logger.info(f"Fetched {len(result)} messages for user {self.user_id}")
            return result

        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch messages for user {self.user_id}: {e}")
            raise DatabaseError("Error fetching messages from the database.")

    def send_message(self, recipient_id: int, content: str, message_type: str = "text") -> bool:
        """
        Send a message to another user.

        Args:
            recipient_id (int): The ID of the recipient.
            content (str): The message content.
            message_type (str): The type of the message (e.g., text, notification).

        Returns:
            bool: True if the message was sent successfully.
        """
        try:
            message = InboxMessage(
                user_id=recipient_id,
                sender=self.user_id,
                content=content,
                status="unread",
                message_type=message_type,
                timestamp=datetime.utcnow(),
            )
            self.db_session.add(message)
            self.db_session.commit()

            # Send notification to the recipient
            send_notification(recipient_id, f"New message received: {content[:50]}...")

            logger.info(f"Message sent from user {self.user_id} to user {recipient_id}")
            return True

        except SQLAlchemyError as e:
            self.db_session.rollback()
            logger.error(f"Failed to send message from user {self.user_id} to user {recipient_id}: {e}")
            raise DatabaseError("Error sending message.")

    def mark_message_as_read(self, message_id: int) -> bool:
        """
        Mark a message as read.

        Args:
            message_id (int): The ID of the message to mark as read.

        Returns:
            bool: True if the operation succeeded.
        """
        try:
            message = self.db_session.query(InboxMessage).filter(
                InboxMessage.id == message_id, InboxMessage.user_id == self.user_id
            ).first()

            if not message:
                logger.warning(f"Message {message_id} not found for user {self.user_id}")
                raise InboxError("Message not found.")

            message.status = "read"
            self.db_session.commit()

            logger.info(f"Message {message_id} marked as read by user {self.user_id}")
            return True

        except SQLAlchemyError as e:
            self.db_session.rollback()
            logger.error(f"Failed to mark message {message_id} as read: {e}")
            raise DatabaseError("Error marking message as read.")

    def delete_message(self, message_id: int) -> bool:
        """
        Delete a message from the inbox.

        Args:
            message_id (int): The ID of the message to delete.

        Returns:
            bool: True if the message was deleted successfully.
        """
        try:
            message = self.db_session.query(InboxMessage).filter(
                InboxMessage.id == message_id, InboxMessage.user_id == self.user_id
            ).first()

            if not message:
                logger.warning(f"Message {message_id} not found for user {self.user_id}")
                raise InboxError("Message not found.")

            self.db_session.delete(message)
            self.db_session.commit()

            logger.info(f"Message {message_id} deleted by user {self.user_id}")
            return True

        except SQLAlchemyError as e:
            self.db_session.rollback()
            logger.error(f"Failed to delete message {message_id}: {e}")
            raise DatabaseError("Error deleting message.")

    def fetch_unread_count(self) -> int:
        """
        Fetch the count of unread messages.

        Returns:
            int: Count of unread messages.
        """
        try:
            count = (
                self.db_session.query(InboxMessage)
                .filter(InboxMessage.user_id == self.user_id, InboxMessage.status == "unread")
                .count()
            )

            logger.info(f"User {self.user_id} has {count} unread messages")
            return count

        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch unread message count for user {self.user_id}: {e}")
            raise DatabaseError("Error fetching unread message count.")

    def close(self):
        """
        Close the database session.
        """
        try:
            self.db_session.close()
            logger.info(f"Database session closed for user {self.user_id}")
        except Exception as e:
            logger.error(f"Error closing database session for user {self.user_id}: {e}")


# Health Check
def check_inbox_manager_health() -> bool:
    """
    Check the health of the InboxManager.

    Returns:
        bool: True if the InboxManager is operational.
    """
    try:
        test_session = get_db_session()
        test_session.execute("SELECT 1")
        test_session.close()
        logger.info("InboxManager is operational.")
        return True
    except Exception as e:
        logger.error(f"InboxManager health check failed: {e}")
        return False

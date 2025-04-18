import uuid
from datetime import datetime
from typing import List, Dict, Optional


class SupportTicketService:
    """
    Manages support ticket creation, updates, and tracking for RLG Data and RLG Fans.
    """

    def __init__(self):
        self.tickets = {}  # Store tickets in the format {ticket_id: ticket_data}

    def create_ticket(self, user_id: str, subject: str, description: str, priority: str = "medium") -> str:
        """
        Create a new support ticket.

        Args:
            user_id (str): ID of the user creating the ticket.
            subject (str): The subject of the ticket.
            description (str): Detailed description of the issue.
            priority (str): Priority of the ticket ('low', 'medium', 'high').

        Returns:
            str: The ID of the created ticket.
        """
        ticket_id = str(uuid.uuid4())
        ticket_data = {
            "ticket_id": ticket_id,
            "user_id": user_id,
            "subject": subject,
            "description": description,
            "priority": priority.lower(),
            "status": "open",  # Default status is open
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "comments": [],
        }

        self.tickets[ticket_id] = ticket_data
        print(f"[{datetime.now()}] Support ticket created: {ticket_data}")
        return ticket_id

    def update_ticket_status(self, ticket_id: str, status: str) -> bool:
        """
        Update the status of a support ticket.

        Args:
            ticket_id (str): ID of the ticket to update.
            status (str): New status ('open', 'in_progress', 'resolved', 'closed').

        Returns:
            bool: True if the status was updated, False otherwise.
        """
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            print(f"[{datetime.now()}] Ticket ID {ticket_id} not found.")
            return False

        ticket["status"] = status.lower()
        ticket["updated_at"] = datetime.now()
        print(f"[{datetime.now()}] Updated ticket {ticket_id} status to {status}.")
        return True

    def add_comment_to_ticket(self, ticket_id: str, user_id: str, comment: str) -> bool:
        """
        Add a comment to a support ticket.

        Args:
            ticket_id (str): ID of the ticket to comment on.
            user_id (str): ID of the user adding the comment.
            comment (str): The comment text.

        Returns:
            bool: True if the comment was added, False otherwise.
        """
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            print(f"[{datetime.now()}] Ticket ID {ticket_id} not found.")
            return False

        comment_data = {
            "user_id": user_id,
            "comment": comment,
            "timestamp": datetime.now(),
        }
        ticket["comments"].append(comment_data)
        ticket["updated_at"] = datetime.now()
        print(f"[{datetime.now()}] Added comment to ticket {ticket_id}: {comment_data}.")
        return True

    def get_ticket(self, ticket_id: str) -> Optional[Dict]:
        """
        Retrieve details of a support ticket.

        Args:
            ticket_id (str): ID of the ticket to retrieve.

        Returns:
            Optional[Dict]: Ticket details if found, None otherwise.
        """
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            print(f"[{datetime.now()}] Ticket ID {ticket_id} not found.")
            return None

        print(f"[{datetime.now()}] Retrieved ticket details: {ticket}.")
        return ticket

    def list_tickets(self, user_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict]:
        """
        List all tickets, optionally filtered by user ID and/or status.

        Args:
            user_id (Optional[str]): ID of the user to filter tickets.
            status (Optional[str]): Status to filter tickets.

        Returns:
            List[Dict]: A list of matching tickets.
        """
        tickets = list(self.tickets.values())
        if user_id:
            tickets = [ticket for ticket in tickets if ticket["user_id"] == user_id]
        if status:
            tickets = [ticket for ticket in tickets if ticket["status"] == status.lower()]

        print(f"[{datetime.now()}] Listing tickets: {len(tickets)} found.")
        return tickets

    def delete_ticket(self, ticket_id: str) -> bool:
        """
        Delete a support ticket.

        Args:
            ticket_id (str): ID of the ticket to delete.

        Returns:
            bool: True if the ticket was deleted, False otherwise.
        """
        if ticket_id not in self.tickets:
            print(f"[{datetime.now()}] Ticket ID {ticket_id} not found.")
            return False

        del self.tickets[ticket_id]
        print(f"[{datetime.now()}] Deleted ticket {ticket_id}.")
        return True


# Example Usage
if __name__ == "__main__":
    support_service = SupportTicketService()

    # Create a ticket
    ticket_id = support_service.create_ticket(
        user_id="user123",
        subject="Login Issue",
        description="Unable to log in to my account.",
        priority="high",
    )

    # Add a comment
    support_service.add_comment_to_ticket(ticket_id, user_id="admin1", comment="We are investigating the issue.")

    # Update the ticket status
    support_service.update_ticket_status(ticket_id, "in_progress")

    # Retrieve ticket details
    ticket_details = support_service.get_ticket(ticket_id)

    # List all tickets
    all_tickets = support_service.list_tickets()

    # Delete a ticket
    support_service.delete_ticket(ticket_id)

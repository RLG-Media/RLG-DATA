import logging
from typing import List, Dict, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("team_collaboration_services.log"),
        logging.StreamHandler()
    ]
)

class TeamCollaborationService:
    """
    Service for facilitating team collaboration for RLG Data and RLG Fans.
    Includes features for task management, shared workspaces, messaging, and file sharing.
    """

    def __init__(self):
        self.tasks = []  # List to store tasks
        self.messages = []  # List to store messages
        self.shared_files = []  # List to store file metadata
        logging.info("TeamCollaborationService initialized.")

    def create_task(self, title: str, description: str, assigned_to: str, due_date: datetime) -> Dict[str, Any]:
        """
        Create a new task for the team.

        Args:
            title (str): Title of the task.
            description (str): Detailed description of the task.
            assigned_to (str): The user assigned to the task.
            due_date (datetime): Due date of the task.

        Returns:
            Dict[str, Any]: Details of the created task.
        """
        task = {
            "task_id": len(self.tasks) + 1,
            "title": title,
            "description": description,
            "assigned_to": assigned_to,
            "due_date": due_date,
            "status": "pending",
            "created_at": datetime.now()
        }
        self.tasks.append(task)
        logging.info("Created task: %s", task)
        return task

    def update_task_status(self, task_id: int, status: str) -> Dict[str, Any]:
        """
        Update the status of a task.

        Args:
            task_id (int): The ID of the task to update.
            status (str): The new status (e.g., "completed", "in progress").

        Returns:
            Dict[str, Any]: Updated task details.
        """
        task = next((t for t in self.tasks if t["task_id"] == task_id), None)
        if not task:
            logging.error("Task ID %d not found.", task_id)
            raise ValueError("Task not found.")

        task["status"] = status
        logging.info("Updated task: %s", task)
        return task

    def send_message(self, sender: str, recipient: str, content: str) -> Dict[str, Any]:
        """
        Send a message between team members.

        Args:
            sender (str): The sender's username.
            recipient (str): The recipient's username.
            content (str): The message content.

        Returns:
            Dict[str, Any]: Details of the sent message.
        """
        message = {
            "message_id": len(self.messages) + 1,
            "sender": sender,
            "recipient": recipient,
            "content": content,
            "timestamp": datetime.now()
        }
        self.messages.append(message)
        logging.info("Sent message: %s", message)
        return message

    def share_file(self, uploader: str, file_name: str, file_url: str) -> Dict[str, Any]:
        """
        Share a file within the team.

        Args:
            uploader (str): The username of the uploader.
            file_name (str): The name of the file.
            file_url (str): The URL to access the file.

        Returns:
            Dict[str, Any]: Details of the shared file.
        """
        shared_file = {
            "file_id": len(self.shared_files) + 1,
            "uploader": uploader,
            "file_name": file_name,
            "file_url": file_url,
            "uploaded_at": datetime.now()
        }
        self.shared_files.append(shared_file)
        logging.info("Shared file: %s", shared_file)
        return shared_file

    def get_task_list(self) -> List[Dict[str, Any]]:
        """
        Retrieve the list of all tasks.

        Returns:
            List[Dict[str, Any]]: List of tasks.
        """
        logging.info("Retrieved task list: %d tasks found.", len(self.tasks))
        return self.tasks

    def get_messages(self, recipient: str) -> List[Dict[str, Any]]:
        """
        Retrieve messages for a specific recipient.

        Args:
            recipient (str): The username of the recipient.

        Returns:
            List[Dict[str, Any]]: List of messages for the recipient.
        """
        recipient_messages = [msg for msg in self.messages if msg["recipient"] == recipient]
        logging.info("Retrieved messages for %s: %d messages found.", recipient, len(recipient_messages))
        return recipient_messages

    def get_shared_files(self) -> List[Dict[str, Any]]:
        """
        Retrieve the list of shared files.

        Returns:
            List[Dict[str, Any]]: List of shared files.
        """
        logging.info("Retrieved shared files: %d files found.", len(self.shared_files))
        return self.shared_files

# Example usage
if __name__ == "__main__":
    team_service = TeamCollaborationService()

    # Create tasks
    team_service.create_task(
        title="Prepare Social Media Report",
        description="Generate and analyze weekly social media performance metrics.",
        assigned_to="user_123",
        due_date=datetime(2025, 1, 31)
    )

    # Send a message
    team_service.send_message(
        sender="user_123",
        recipient="user_456",
        content="Can you review the latest draft of the media report?"
    )

    # Share a file
    team_service.share_file(
        uploader="user_123",
        file_name="Social_Media_Report.pdf",
        file_url="https://example.com/files/Social_Media_Report.pdf"
    )

    # Get tasks, messages, and shared files
    tasks = team_service.get_task_list()
    messages = team_service.get_messages(recipient="user_456")
    files = team_service.get_shared_files()

    print("Tasks:", tasks)
    print("Messages:", messages)
    print("Shared Files:", files)

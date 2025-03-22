from typing import List, Dict, Optional, Union
from datetime import datetime
import logging
from uuid import uuid4

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class User:
    """Represents a team member."""
    def __init__(self, user_id: str, name: str, email: str, role: str):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.role = role
        self.tasks: List[Dict[str, Union[str, datetime]]] = []

    def assign_task(self, task: Dict[str, Union[str, datetime]]) -> None:
        """Assigns a task to the user."""
        self.tasks.append(task)
        logging.info(f"Task '{task['title']}' assigned to {self.name}.")

    def __repr__(self):
        return f"<User {self.name} - Role: {self.role}>"


class TeamManagement:
    """Manages teams, roles, permissions, and communication tracking."""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.roles_permissions: Dict[str, List[str]] = {
            "Admin": ["add_user", "remove_user", "assign_task", "view_reports"],
            "Manager": ["assign_task", "view_reports"],
            "Member": ["view_tasks"],
        }

    def add_user(self, name: str, email: str, role: str) -> str:
        """
        Adds a new user to the team.
        Args:
            name (str): The name of the user.
            email (str): The email address of the user.
            role (str): The role of the user.
        Returns:
            str: The ID of the newly added user.
        """
        if role not in self.roles_permissions:
            raise ValueError(f"Invalid role: {role}. Available roles: {list(self.roles_permissions.keys())}.")
        
        user_id = str(uuid4())
        self.users[user_id] = User(user_id, name, email, role)
        logging.info(f"User '{name}' added with role '{role}'.")
        return user_id

    def remove_user(self, user_id: str) -> None:
        """
        Removes a user from the team.
        Args:
            user_id (str): The ID of the user to be removed.
        """
        if user_id in self.users:
            removed_user = self.users.pop(user_id)
            logging.info(f"User '{removed_user.name}' removed from the team.")
        else:
            logging.warning(f"User with ID '{user_id}' not found.")

    def list_users(self) -> List[Dict[str, Union[str, List[str]]]]:
        """
        Lists all users in the team.
        Returns:
            List[Dict]: A list of users with their details.
        """
        return [
            {"user_id": user.user_id, "name": user.name, "email": user.email, "role": user.role}
            for user in self.users.values()
        ]

    def assign_task_to_user(self, user_id: str, task_title: str, task_description: str, deadline: datetime) -> None:
        """
        Assigns a task to a specific user.
        Args:
            user_id (str): The ID of the user to assign the task to.
            task_title (str): Title of the task.
            task_description (str): Description of the task.
            deadline (datetime): The deadline for the task.
        """
        if user_id not in self.users:
            raise ValueError(f"User with ID '{user_id}' not found.")

        task = {
            "task_id": str(uuid4()),
            "title": task_title,
            "description": task_description,
            "deadline": deadline,
            "assigned_on": datetime.now(),
        }
        self.users[user_id].assign_task(task)

    def get_user_tasks(self, user_id: str) -> List[Dict[str, Union[str, datetime]]]:
        """
        Retrieves tasks assigned to a specific user.
        Args:
            user_id (str): The ID of the user.
        Returns:
            List[Dict]: A list of tasks assigned to the user.
        """
        if user_id not in self.users:
            raise ValueError(f"User with ID '{user_id}' not found.")
        return self.users[user_id].tasks

    def update_role_permissions(self, role: str, permissions: List[str]) -> None:
        """
        Updates the permissions associated with a role.
        Args:
            role (str): The role to update.
            permissions (List[str]): The new permissions for the role.
        """
        if role not in self.roles_permissions:
            raise ValueError(f"Role '{role}' does not exist.")
        self.roles_permissions[role] = permissions
        logging.info(f"Permissions for role '{role}' updated to: {permissions}.")

    def get_role_permissions(self, role: str) -> List[str]:
        """
        Retrieves the permissions for a specific role.
        Args:
            role (str): The role to retrieve permissions for.
        Returns:
            List[str]: A list of permissions associated with the role.
        """
        if role not in self.roles_permissions:
            raise ValueError(f"Role '{role}' does not exist.")
        return self.roles_permissions[role]

    def broadcast_message(self, message: str, role: Optional[str] = None) -> None:
        """
        Broadcasts a message to all users or users with a specific role.
        Args:
            message (str): The message to broadcast.
            role (Optional[str]): The role of users to send the message to.
        """
        recipients = [
            user for user in self.users.values()
            if role is None or user.role == role
        ]
        for user in recipients:
            self._send_message(user.email, message)
        logging.info(f"Message broadcasted to {len(recipients)} recipients.")

    @staticmethod
    def _send_message(email: str, message: str) -> None:
        """
        Simulates sending a message to a user via email.
        Args:
            email (str): The email address to send the message to.
            message (str): The content of the message.
        """
        logging.info(f"Message sent to {email}: {message}")

# Example Usage
if __name__ == "__main__":
    tm = TeamManagement()

    # Add users
    user_id_1 = tm.add_user(name="Alice", email="alice@example.com", role="Admin")
    user_id_2 = tm.add_user(name="Bob", email="bob@example.com", role="Manager")
    user_id_3 = tm.add_user(name="Charlie", email="charlie@example.com", role="Member")

    # List users
    print("Team Members:", tm.list_users())

    # Assign tasks
    tm.assign_task_to_user(user_id_1, "Prepare Report", "Prepare the quarterly report", datetime(2025, 2, 15))

    # Broadcast message
    tm.broadcast_message("Team meeting at 3 PM.", role="Manager")

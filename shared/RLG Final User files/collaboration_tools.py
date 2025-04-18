import datetime
from typing import List, Dict, Any, Optional


class CollaborationTools:
    """
    Provides tools for collaboration, including shared workspaces, task management, and communication.
    """

    def __init__(self):
        """
        Initializes the collaboration tools with in-memory data storage for simplicity.
        This can be replaced with a database for persistent storage.
        """
        self.workspaces = {}  # {workspace_id: {details}}
        self.users = {}  # {user_id: {details}}
        self.tasks = {}  # {task_id: {details}}
        self.notifications = []  # List of notifications

    # --- Workspace Management ---
    def create_workspace(self, workspace_name: str, owner_id: str) -> Dict[str, Any]:
        """
        Creates a new shared workspace.
        :param workspace_name: Name of the workspace.
        :param owner_id: ID of the user creating the workspace.
        :return: Details of the created workspace.
        """
        workspace_id = f"ws_{len(self.workspaces) + 1}"
        workspace = {
            "id": workspace_id,
            "name": workspace_name,
            "owner_id": owner_id,
            "members": [owner_id],
            "created_at": datetime.datetime.utcnow(),
        }
        self.workspaces[workspace_id] = workspace
        return workspace

    def add_member_to_workspace(self, workspace_id: str, user_id: str) -> Optional[str]:
        """
        Adds a user to a shared workspace.
        :param workspace_id: ID of the workspace.
        :param user_id: ID of the user to add.
        :return: Success message or error message.
        """
        workspace = self.workspaces.get(workspace_id)
        if not workspace:
            return "Workspace not found."
        if user_id in workspace["members"]:
            return "User is already a member of this workspace."
        workspace["members"].append(user_id)
        return f"User {user_id} added to workspace {workspace_id}."

    # --- Task Management ---
    def create_task(
        self, workspace_id: str, creator_id: str, title: str, description: str, deadline: datetime.datetime
    ) -> Dict[str, Any]:
        """
        Creates a new task within a workspace.
        :param workspace_id: ID of the workspace.
        :param creator_id: ID of the task creator.
        :param title: Task title.
        :param description: Task description.
        :param deadline: Task deadline.
        :return: Details of the created task.
        """
        task_id = f"task_{len(self.tasks) + 1}"
        task = {
            "id": task_id,
            "workspace_id": workspace_id,
            "creator_id": creator_id,
            "title": title,
            "description": description,
            "deadline": deadline,
            "assigned_to": None,
            "status": "Pending",
            "created_at": datetime.datetime.utcnow(),
        }
        self.tasks[task_id] = task
        return task

    def assign_task(self, task_id: str, user_id: str) -> Optional[str]:
        """
        Assigns a task to a specific user.
        :param task_id: ID of the task.
        :param user_id: ID of the user to assign.
        :return: Success message or error message.
        """
        task = self.tasks.get(task_id)
        if not task:
            return "Task not found."
        task["assigned_to"] = user_id
        task["status"] = "Assigned"
        return f"Task {task_id} assigned to user {user_id}."

    def update_task_status(self, task_id: str, status: str) -> Optional[str]:
        """
        Updates the status of a task.
        :param task_id: ID of the task.
        :param status: New status (e.g., Pending, In Progress, Completed).
        :return: Success message or error message.
        """
        task = self.tasks.get(task_id)
        if not task:
            return "Task not found."
        task["status"] = status
        return f"Task {task_id} status updated to {status}."

    # --- Communication Tools ---
    def send_notification(self, user_id: str, message: str) -> None:
        """
        Sends a notification to a user.
        :param user_id: ID of the user.
        :param message: Notification message.
        """
        notification = {
            "user_id": user_id,
            "message": message,
            "timestamp": datetime.datetime.utcnow(),
        }
        self.notifications.append(notification)

    def get_notifications(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves notifications for a specific user.
        :param user_id: ID of the user.
        :return: List of notifications.
        """
        return [n for n in self.notifications if n["user_id"] == user_id]

    # --- Role-Based Access Control ---
    def check_access(self, workspace_id: str, user_id: str) -> bool:
        """
        Checks if a user has access to a workspace.
        :param workspace_id: ID of the workspace.
        :param user_id: ID of the user.
        :return: True if the user has access; False otherwise.
        """
        workspace = self.workspaces.get(workspace_id)
        return user_id in workspace["members"] if workspace else False


# Example Usage
if __name__ == "__main__":
    tools = CollaborationTools()

    # Create a workspace
    workspace = tools.create_workspace("Project Alpha", "user_1")
    print("Workspace Created:", workspace)

    # Add a member to the workspace
    print(tools.add_member_to_workspace(workspace["id"], "user_2"))

    # Create a task
    task = tools.create_task(
        workspace["id"], "user_1", "Complete Report", "Prepare the Q1 report", datetime.datetime(2025, 1, 15)
    )
    print("Task Created:", task)

    # Assign a task
    print(tools.assign_task(task["id"], "user_2"))

    # Update task status
    print(tools.update_task_status(task["id"], "In Progress"))

    # Send a notification
    tools.send_notification("user_2", "You have been assigned a new task.")
    print("Notifications for user_2:", tools.get_notifications("user_2"))

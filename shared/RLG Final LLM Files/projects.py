from datetime import datetime
from typing import List, Dict, Union, Optional
from uuid import uuid4

class Project:
    """
    Represents a project for RLG Data and RLG Fans.
    """
    def __init__(self, name: str, description: str, created_by: str, start_date: Optional[str] = None, end_date: Optional[str] = None):
        """
        Initialize a new project instance.

        :param name: The name of the project.
        :param description: A brief description of the project.
        :param created_by: The user who created the project.
        :param start_date: Optional start date in 'YYYY-MM-DD' format.
        :param end_date: Optional end date in 'YYYY-MM-DD' format.
        """
        self.project_id = str(uuid4())
        self.name = name
        self.description = description
        self.created_by = created_by
        self.created_at = datetime.utcnow()
        self.updated_at = self.created_at
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        self.members = []
        self.status = "Active"  # Active, Completed, Archived

    def to_dict(self) -> Dict:
        """
        Converts the project instance to a dictionary.

        :return: A dictionary representation of the project.
        """
        return {
            "project_id": self.project_id,
            "name": self.name,
            "description": self.description,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "members": self.members,
            "status": self.status,
        }

    def add_member(self, user_id: str):
        """
        Adds a member to the project.

        :param user_id: The ID of the user to add.
        """
        if user_id not in self.members:
            self.members.append(user_id)
            self.updated_at = datetime.utcnow()

    def remove_member(self, user_id: str):
        """
        Removes a member from the project.

        :param user_id: The ID of the user to remove.
        """
        if user_id in self.members:
            self.members.remove(user_id)
            self.updated_at = datetime.utcnow()

    def update_status(self, status: str):
        """
        Updates the status of the project.

        :param status: The new status (e.g., Active, Completed, Archived).
        """
        allowed_statuses = {"Active", "Completed", "Archived"}
        if status in allowed_statuses:
            self.status = status
            self.updated_at = datetime.utcnow()
        else:
            raise ValueError(f"Invalid status. Allowed statuses: {', '.join(allowed_statuses)}")


class ProjectManager:
    """
    Manages a collection of projects.
    """
    def __init__(self):
        self.projects: Dict[str, Project] = {}

    def create_project(self, name: str, description: str, created_by: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Project:
        """
        Creates a new project.

        :param name: The name of the project.
        :param description: A brief description of the project.
        :param created_by: The user who created the project.
        :param start_date: Optional start date in 'YYYY-MM-DD' format.
        :param end_date: Optional end date in 'YYYY-MM-DD' format.
        :return: The created Project instance.
        """
        project = Project(name, description, created_by, start_date, end_date)
        self.projects[project.project_id] = project
        return project

    def get_project(self, project_id: str) -> Optional[Project]:
        """
        Retrieves a project by its ID.

        :param project_id: The ID of the project.
        :return: The Project instance, or None if not found.
        """
        return self.projects.get(project_id)

    def update_project(self, project_id: str, updates: Dict[str, Union[str, List[str]]]) -> Optional[Project]:
        """
        Updates an existing project.

        :param project_id: The ID of the project to update.
        :param updates: A dictionary of updates.
        :return: The updated Project instance, or None if not found.
        """
        project = self.get_project(project_id)
        if not project:
            return None

        for key, value in updates.items():
            if key == "name":
                project.name = value
            elif key == "description":
                project.description = value
            elif key == "start_date":
                project.start_date = datetime.strptime(value, '%Y-%m-%d')
            elif key == "end_date":
                project.end_date = datetime.strptime(value, '%Y-%m-%d')
            elif key == "status":
                project.update_status(value)
            elif key == "members":
                project.members = value
            else:
                raise ValueError(f"Unknown field: {key}")

        project.updated_at = datetime.utcnow()
        return project

    def delete_project(self, project_id: str) -> bool:
        """
        Deletes a project by its ID.

        :param project_id: The ID of the project to delete.
        :return: True if the project was deleted, False if not found.
        """
        if project_id in self.projects:
            del self.projects[project_id]
            return True
        return False

    def list_projects(self) -> List[Dict]:
        """
        Lists all projects.

        :return: A list of all projects as dictionaries.
        """
        return [project.to_dict() for project in self.projects.values()]

    def archive_project(self, project_id: str) -> bool:
        """
        Archives a project.

        :param project_id: The ID of the project to archive.
        :return: True if the project was archived, False if not found.
        """
        project = self.get_project(project_id)
        if project:
            project.update_status("Archived")
            return True
        return False

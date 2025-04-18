"""
permissions.py
Centralized permission management for RLG Data and RLG Fans.
Handles roles, permissions, access control, and integration with authentication.
"""

from typing import List, Dict, Any, Optional, Union
from enum import Enum
from functools import wraps
from flask import request, jsonify
from authentication import get_current_user

# Logging configuration
from logging_config import get_logger

logger = get_logger("Permissions")

class PermissionLevel(Enum):
    """
    Enum for defining permission levels.
    """
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"

class Roles(Enum):
    """
    Enum for defining roles.
    """
    VIEWER = "viewer"
    EDITOR = "editor"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

# Role-based permission definitions
ROLE_PERMISSIONS = {
    Roles.VIEWER: [PermissionLevel.READ],
    Roles.EDITOR: [PermissionLevel.READ, PermissionLevel.WRITE],
    Roles.MODERATOR: [PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.EXECUTE],
    Roles.ADMIN: [PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.EXECUTE, PermissionLevel.ADMIN],
    Roles.SUPER_ADMIN: [PermissionLevel.ADMIN],  # Full unrestricted access
}

# Default role assigned to new users
DEFAULT_ROLE = Roles.VIEWER

class PermissionError(Exception):
    """
    Custom exception for permission errors.
    """
    def __init__(self, message: str, code: int = 403):
        self.message = message
        self.code = code
        super().__init__(message)

def check_permission(user_roles: List[Roles], required_permission: PermissionLevel) -> bool:
    """
    Check if a user has the required permission.

    Args:
        user_roles (List[Roles]): List of roles assigned to the user.
        required_permission (PermissionLevel): The permission level required.

    Returns:
        bool: True if the user has the required permission, False otherwise.
    """
    for role in user_roles:
        if required_permission in ROLE_PERMISSIONS.get(role, []):
            return True
    return False

def permission_required(permission: PermissionLevel):
    """
    Decorator for enforcing permissions on endpoints.

    Args:
        permission (PermissionLevel): The required permission level.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if not user:
                logger.warning("Access denied: No user context found.")
                return jsonify({"error": "Access denied"}), 401

            user_roles = user.get("roles", [])
            if check_permission(user_roles, permission):
                return func(*args, **kwargs)

            logger.warning(f"Access denied for user {user['id']} - insufficient permissions.")
            return jsonify({"error": "Forbidden"}), 403

        return wrapper
    return decorator

def assign_role(user_id: str, role: Roles) -> None:
    """
    Assign a role to a user.

    Args:
        user_id (str): The user's ID.
        role (Roles): The role to assign.
    """
    logger.info(f"Assigning role {role.value} to user {user_id}")
    # Update the database or cache to assign the role
    # Example: db.update_user_role(user_id, role.value)

def get_user_permissions(user_roles: List[Roles]) -> List[PermissionLevel]:
    """
    Retrieve the cumulative permissions for a user based on their roles.

    Args:
        user_roles (List[Roles]): List of roles assigned to the user.

    Returns:
        List[PermissionLevel]: The user's permissions.
    """
    permissions = set()
    for role in user_roles:
        permissions.update(ROLE_PERMISSIONS.get(role, []))
    return list(permissions)

def role_hierarchy() -> Dict[str, Any]:
    """
    Return the role hierarchy.

    Returns:
        Dict[str, Any]: A dictionary describing role inheritance and permissions.
    """
    return {role.name: [perm.value for perm in perms] for role, perms in ROLE_PERMISSIONS.items()}

def is_super_admin(user_roles: List[Roles]) -> bool:
    """
    Check if a user is a super admin.

    Args:
        user_roles (List[Roles]): List of roles assigned to the user.

    Returns:
        bool: True if the user is a super admin, False otherwise.
    """
    return Roles.SUPER_ADMIN in user_roles

# Example usage of permission_required decorator
@permission_required(PermissionLevel.ADMIN)
def admin_only_endpoint():
    return jsonify({"message": "Welcome, Admin!"})

if __name__ == "__main__":
    # Example testing and logging
    logger.info("Initializing permissions system...")

    # Mock data
    mock_user_roles = [Roles.EDITOR, Roles.MODERATOR]
    logger.info(f"User roles: {mock_user_roles}")
    logger.info(f"User permissions: {get_user_permissions(mock_user_roles)}")

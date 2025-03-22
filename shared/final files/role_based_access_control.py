from functools import wraps
from flask import request, jsonify
from werkzeug.exceptions import Forbidden

# Mocked user roles and permissions data
USER_ROLES = {
    'admin': {'permissions': ['view_all', 'edit_all', 'delete_all', 'manage_users']},
    'editor': {'permissions': ['view_all', 'edit_all']},
    'viewer': {'permissions': ['view_all']}
}

# Mocked database of users with roles
USER_DATABASE = {
    'user_1': {'role': 'admin'},
    'user_2': {'role': 'editor'},
    'user_3': {'role': 'viewer'}
}

def get_user_role(user_id):
    """
    Simulate fetching a user's role from a database.
    Args:
        user_id (str): User's unique identifier.
    Returns:
        str: User's role ('admin', 'editor', 'viewer').
    """
    user = USER_DATABASE.get(user_id)
    if user:
        return user.get('role')
    return None

def has_permission(role, permission):
    """
    Check if the given role has the required permission.
    Args:
        role (str): User's role.
        permission (str): Permission to check.
    Returns:
        bool: True if the role has the permission, False otherwise.
    """
    if role in USER_ROLES:
        return permission in USER_ROLES[role]['permissions']
    return False

def role_required(permissions):
    """
    Decorator to check if the user has the necessary role and permissions.
    Args:
        permissions (list): A list of required permissions.
    Returns:
        function: The wrapped function that checks permissions.
    """
    def wrapper(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            # Get user from request (e.g., user_id passed in headers or session)
            user_id = request.headers.get('X-User-Id')  # This can be from a session or token
            
            if not user_id:
                raise Forbidden("User ID missing from request.")

            user_role = get_user_role(user_id)

            if not user_role:
                raise Forbidden("User role not found.")
            
            # Check if the user has all required permissions
            for permission in permissions:
                if not has_permission(user_role, permission):
                    raise Forbidden(f"User does not have '{permission}' permission.")

            return fn(*args, **kwargs)

        return wrapped
    return wrapper


# Example of applying role-based access control to routes

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/admin_dashboard')
@role_required(['view_all', 'edit_all', 'manage_users'])
def admin_dashboard():
    """
    Admin route that requires view, edit, and manage_users permissions.
    """
    return jsonify(message="Welcome to the Admin Dashboard!")

@app.route('/edit_content')
@role_required(['view_all', 'edit_all'])
def edit_content():
    """
    Editor route that requires view and edit permissions.
    """
    return jsonify(message="Welcome to the Content Edit Page!")

@app.route('/view_content')
@role_required(['view_all'])
def view_content():
    """
    Viewer route that only requires view permission.
    """
    return jsonify(message="Welcome to the Content View Page!")

@app.route('/user_info')
def user_info():
    """
    Route that shows user information (public).
    """
    return jsonify(message="This page is accessible by anyone.")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from models import User, Role, Project
from werkzeug.security import generate_password_hash
import logging
from flask_login import login_required, current_user

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create a Blueprint for admin-related routes
admin_blueprint = Blueprint('admin', __name__, url_prefix='/admin')

# Helper function to check if the user is an admin
def is_admin():
    return current_user.is_authenticated and 'admin' in [role.name for role in current_user.roles]

@admin_blueprint.before_request
@login_required
def restrict_to_admins():
    """
    This middleware checks if the logged-in user is an admin.
    If not, they are redirected to the login page with an error message.
    """
    if not is_admin():
        flash("You do not have permission to access this page.", 'danger')
        return redirect(url_for('auth.login'))

@admin_blueprint.route('/users', methods=['GET'])
def manage_users():
    """
    Display a list of all users for the admin.
    """
    try:
        users = User.query.all()
        return render_template('admin/manage_users.html', users=users)

    except Exception as e:
        logging.error(f"Error fetching users: {e}")
        flash('An error occurred while fetching users.', 'danger')
        return redirect(url_for('dashboard'))

@admin_blueprint.route('/users/create', methods=['GET', 'POST'])
def create_user():
    """
    Admin can create a new user.
    """
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            role_name = request.form['role']

            # Check if the username is already taken
            if User.query.filter_by(username=username).first():
                flash(f"Username '{username}' is already taken.", 'danger')
                return redirect(url_for('admin.create_user'))

            # Hash the user's password
            password_hash = generate_password_hash(password)

            # Check if the role exists
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                flash(f"Role '{role_name}' does not exist.", 'danger')
                return redirect(url_for('admin.create_user'))

            # Create a new user and assign the role
            new_user = User(username=username, password_hash=password_hash)
            new_user.roles.append(role)
            db.session.add(new_user)
            db.session.commit()

            logging.info(f"Created new user: {username}")
            flash('User created successfully!', 'success')
            return redirect(url_for('admin.manage_users'))

        except Exception as e:
            logging.error(f"Error creating user: {e}")
            flash('An error occurred while creating the user.', 'danger')

    roles = Role.query.all()
    return render_template('admin/create_user.html', roles=roles)

@admin_blueprint.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    """
    Admin can edit an existing user.
    """
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        try:
            user.username = request.form['username']
            role_name = request.form['role']

            # Update role if necessary
            role = Role.query.filter_by(name=role_name).first()
            if role and role not in user.roles:
                user.roles = [role]

            db.session.commit()
            logging.info(f"Updated user: {user.username}")
            flash('User updated successfully!', 'success')
            return redirect(url_for('admin.manage_users'))

        except Exception as e:
            logging.error(f"Error updating user {user_id}: {e}")
            flash('An error occurred while updating the user.', 'danger')

    roles = Role.query.all()
    return render_template('admin/edit_user.html', user=user, roles=roles)

@admin_blueprint.route('/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    """
    Admin can delete a user.
    """
    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()

        logging.info(f"Deleted user: {user.username}")
        flash('User deleted successfully!', 'success')
        return redirect(url_for('admin.manage_users'))

    except Exception as e:
        logging.error(f"Error deleting user {user_id}: {e}")
        flash('An error occurred while deleting the user.', 'danger')
        return redirect(url_for('admin.manage_users'))

@admin_blueprint.route('/projects', methods=['GET'])
def manage_projects():
    """
    Admin can view and manage all user projects.
    """
    try:
        projects = Project.query.all()
        return render_template('admin/manage_projects.html', projects=projects)

    except Exception as e:
        logging.error(f"Error fetching projects: {e}")
        flash('An error occurred while fetching projects.', 'danger')
        return redirect(url_for('dashboard'))

@admin_blueprint.route('/projects/delete/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    """
    Admin can delete a project.
    """
    try:
        project = Project.query.get_or_404(project_id)
        db.session.delete(project)
        db.session.commit()

        logging.info(f"Deleted project: {project.name}")
        flash('Project deleted successfully!', 'success')
        return redirect(url_for('admin.manage_projects'))

    except Exception as e:
        logging.error(f"Error deleting project {project_id}: {e}")
        flash('An error occurred while deleting the project.', 'danger')
        return redirect(url_for('admin.manage_projects'))

@admin_blueprint.route('/tasks', methods=['GET'])
def monitor_tasks():
    """
    Admin can monitor all tasks (e.g., scraping tasks, API data fetches).
    This could be enhanced with Celery task monitoring.
    """
    try:
        # Placeholder, in practice, link this to task monitoring (e.g., Celery)
        tasks = []  # Example task list, to be replaced with actual task data
        return render_template('admin/monitor_tasks.html', tasks=tasks)

    except Exception as e:
        logging.error(f"Error monitoring tasks: {e}")
        flash('An error occurred while monitoring tasks.', 'danger')
        return redirect(url_for('dashboard'))

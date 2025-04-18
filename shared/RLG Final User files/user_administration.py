"""
user_administration.py

This module provides a set of administrative endpoints and functions to manage user accounts
for both RLG Data and RLG Fans. It leverages Flask, Flask-Login, and Flask SQLAlchemy to allow
an administrator to list, view, update, and delete user accounts.

For production, it is recommended to replace the simple admin-check (currently based on username)
with a full role-based access control (RBAC) system.

Additional recommendations include input validation, secure logging, and audit trail creation.
"""

import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

# Import the User model and database instance from the user_authentication module.
# (Assuming that the User model and SQLAlchemy db have been defined there.)
from user_authentication import User, db

# Configure logging
logger = logging.getLogger("UserAdministration")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

# Create a Flask blueprint for user administration.
admin_bp = Blueprint("admin", __name__, template_folder="templates", url_prefix="/admin")

# ----------------------------------------
# Helper: Admin-only decorator
# ----------------------------------------
def admin_required(f):
    """
    Decorator to ensure the current user is an administrator.
    For demonstration, we assume that only a user with username "admin" is allowed.
    In production, implement a proper role check (e.g., using a roles field or RBAC system).
    """
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.username.lower() != "admin":
            flash("Administrator access required.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function

# ----------------------------------------
# Routes for User Administration
# ----------------------------------------

@admin_bp.route("/users", methods=["GET"])
@login_required
@admin_required
def list_users():
    """
    List all users with optional filtering by region.
    URL query parameters:
      - region (optional): Filter users by region.
    """
    region = request.args.get("region")
    try:
        if region:
            users = User.query.filter_by(region=region).all()
        else:
            users = User.query.all()
        # Convert users to a list of dictionaries for JSON response or rendering.
        user_list = [
            {"id": user.id, "username": user.username, "email": user.email, "region": user.region}
            for user in users
        ]
        logger.info("Admin listed %d users (filtered by region: %s).", len(user_list), region)
        # Here you can render a template (e.g., admin_users.html) or return JSON.
        return render_template("admin_users.html", users=user_list, region=region)
    except Exception as e:
        logger.error("Error listing users: %s", e)
        flash("Error retrieving user list.", "danger")
        return redirect(url_for("admin.dashboard"))

@admin_bp.route("/users/<int:user_id>", methods=["GET"])
@login_required
@admin_required
def view_user(user_id):
    """
    View detailed information about a specific user.
    """
    try:
        user = User.query.get_or_404(user_id)
        logger.info("Admin viewing details for user ID: %d", user_id)
        return render_template("admin_user_detail.html", user=user)
    except Exception as e:
        logger.error("Error viewing user details: %s", e)
        flash("Error retrieving user details.", "danger")
        return redirect(url_for("admin.list_users"))

@admin_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_user(user_id):
    """
    Edit user details. Supports GET for displaying the edit form and POST for processing updates.
    Updatable fields: email, region, and (optionally) password.
    """
    try:
        user = User.query.get_or_404(user_id)
    except Exception as e:
        logger.error("Error retrieving user for editing: %s", e)
        flash("User not found.", "danger")
        return redirect(url_for("admin.list_users"))

    if request.method == "POST":
        # Retrieve updated fields from the form.
        new_email = request.form.get("email", "").strip()
        new_region = request.form.get("region", "").strip()
        new_password = request.form.get("password", "").strip()  # Optional: update if provided.

        if not new_email or not new_region:
            flash("Email and region are required.", "danger")
            return redirect(url_for("admin.edit_user", user_id=user_id))

        try:
            user.email = new_email
            user.region = new_region
            if new_password:
                user.password = generate_password_hash(new_password, method="sha256")
            db.session.commit()
            logger.info("Updated user ID %d details.", user_id)
            flash("User details updated successfully.", "success")
            return redirect(url_for("admin.view_user", user_id=user_id))
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating user: %s", e)
            flash("Error updating user details.", "danger")
            return redirect(url_for("admin.edit_user", user_id=user_id))
    else:
        # Render the edit form with current user data.
        return render_template("admin_edit_user.html", user=user)

@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    """
    Delete a user account.
    """
    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        logger.info("Deleted user ID %d.", user_id)
        flash("User deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        logger.error("Error deleting user: %s", e)
        flash("Error deleting user.", "danger")
    return redirect(url_for("admin.list_users"))

@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    """
    Admin dashboard overview. This page can display summary statistics, recent activity, etc.
    """
    try:
        total_users = User.query.count()
        logger.info("Admin dashboard accessed. Total users: %d", total_users)
        return render_template("admin_dashboard.html", total_users=total_users)
    except Exception as e:
        logger.error("Error accessing admin dashboard: %s", e)
        flash("Error loading dashboard.", "danger")
        return redirect(url_for("auth.profile"))

# ----------------------------------------
# Additional Recommendations:
# ----------------------------------------
# 1. **Role-Based Access Control (RBAC):** Replace the simple admin check with a proper RBAC mechanism.
# 2. **Input Validation:** Use WTForms or another library for more robust form validation.
# 3. **Audit Logging:** Consider adding audit logs for every admin action to track changes for compliance.
# 4. **Pagination & Search:** For large user bases, implement pagination and search filters.
# 5. **REST API Endpoints:** In addition to HTML pages, consider exposing REST API endpoints secured by tokens
#    for administrative tasks.
# 6. **HTTPS & Security Headers:** Ensure that the administration interface is served over HTTPS and includes
#    proper security headers.

# ----------------------------------------
# Standalone Testing
# ----------------------------------------
if __name__ == "__main__":
    # For standalone testing, create a minimal Flask app instance and register the blueprint.
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI", "sqlite:///rlg_users.db")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "your_super_secret_key")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize SQLAlchemy and Flask-Login.
    from flask_sqlalchemy import SQLAlchemy
    from flask_login import LoginManager

    db.init_app(app)
    login_manager = LoginManager(app)
    login_manager.login_view = "auth.login"

    # Register the admin blueprint.
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # Minimal inline templates for testing purposes.
    @app.route("/")
    def index():
        return "User Administration Module - Standalone Testing"

    # Run the Flask development server.
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5003, debug=True)

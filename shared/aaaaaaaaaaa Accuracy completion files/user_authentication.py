"""
user_authentication.py

This module implements a secure user authentication system for both RLG Data and RLG Fans.
It uses Flask, Flask-Login, and Flask SQLAlchemy to handle user registration, login, logout,
and session management. Passwords are securely hashed using Werkzeug’s security utilities.
"""

import os
import logging
from flask import Flask, render_template, redirect, url_for, request, flash, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash

# Configure logging
logger = logging.getLogger("UserAuthentication")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

# ----------------------------
# Configuration and App Setup
# ----------------------------

# For production, load configuration from environment variables or a secure config file.
DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///rlg_users.db")
SECRET_KEY = os.getenv("SECRET_KEY", "your_super_secret_key")

# Initialize Flask app and configuration.
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy and Flask-Login.
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "auth.login"  # Redirect unauthorized users to login page.

# ----------------------------
# User Model
# ----------------------------

class User(UserMixin, db.Model):
    """
    User model for authentication.
    
    Attributes:
        id (int): Primary key.
        username (str): Unique username.
        email (str): User's email address.
        password (str): Hashed password.
        region (str): Region identifier for the user (for region-specific features).
    """
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    region = db.Column(db.String(50), nullable=False, default="default")

    def __repr__(self):
        return f"<User {self.username}, Region: {self.region}>"

# Create tables if they don't exist.
with app.app_context():
    db.create_all()
    logger.info("User table created or already exists.")

# ----------------------------
# Flask-Login User Loader
# ----------------------------

@login_manager.user_loader
def load_user(user_id):
    """
    Loads a user given a user ID.
    
    Parameters:
        user_id (str): The user ID.
        
    Returns:
        User: The User object or None if not found.
    """
    return User.query.get(int(user_id))

# ----------------------------
# Authentication Blueprint
# ----------------------------

auth = Blueprint("auth", __name__, template_folder="templates")

@auth.route("/register", methods=["GET", "POST"])
def register():
    """
    Handles user registration.
    
    GET: Renders the registration form.
    POST: Processes the registration form, creates a new user, and logs the user in.
    """
    if request.method == "POST":
        username = request.form.get("username").strip()
        email = request.form.get("email").strip()
        password = request.form.get("password")
        region = request.form.get("region", "default").strip()

        # Basic validation.
        if not username or not email or not password:
            flash("Please fill out all fields.", "danger")
            return redirect(url_for("auth.register"))

        # Check if user already exists.
        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            flash("Username or email already exists.", "danger")
            return redirect(url_for("auth.register"))

        # Create new user.
        hashed_password = generate_password_hash(password, method="sha256")
        new_user = User(username=username, email=email, password=hashed_password, region=region)
        try:
            db.session.add(new_user)
            db.session.commit()
            logger.info("New user registered: %s", new_user)
            login_user(new_user)
            flash("Registration successful!", "success")
            return redirect(url_for("auth.profile"))
        except Exception as e:
            db.session.rollback()
            logger.error("Error during registration: %s", e)
            flash("Registration failed due to an error.", "danger")
            return redirect(url_for("auth.register"))
    # Render registration template.
    return render_template("register.html")

@auth.route("/login", methods=["GET", "POST"])
def login():
    """
    Handles user login.
    
    GET: Renders the login form.
    POST: Processes the login credentials, and logs the user in if credentials are valid.
    """
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            flash("Invalid username or password.", "danger")
            logger.warning("Failed login attempt for username: %s", username)
            return redirect(url_for("auth.login"))

        login_user(user)
        flash("Logged in successfully!", "success")
        logger.info("User logged in: %s", user)
        return redirect(url_for("auth.profile"))
    return render_template("login.html")

@auth.route("/logout")
@login_required
def logout():
    """
    Logs out the current user.
    """
    logger.info("User logged out: %s", current_user)
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))

@auth.route("/profile")
@login_required
def profile():
    """
    A protected profile page for logged-in users.
    """
    return render_template("profile.html", user=current_user)

# ----------------------------
# Register Blueprint with the App
# ----------------------------
app.register_blueprint(auth, url_prefix="/auth")

# ----------------------------
# Additional Recommendations:
# ----------------------------
# 1. **Templates:** Move your HTML templates (login.html, register.html, profile.html) into the 'templates' folder.
#    Customize them to match your application's branding.
# 2. **Input Validation:** Consider using WTForms for better form validation and error handling.
# 3. **Security Enhancements:** Add account lockout mechanisms after multiple failed login attempts.
# 4. **Email Verification:** Integrate email verification during registration to ensure the validity of user emails.
# 5. **HTTPS & Session Security:** Ensure your app is served over HTTPS in production and use secure cookies.
# 6. **Scalability:** For larger deployments, consider integrating with an OAuth provider or a dedicated identity provider.

# ----------------------------
# Standalone Testing
# ----------------------------
if __name__ == "__main__":
    # For standalone testing, run the Flask development server.
    # Create minimal inline templates if templates are not provided.
    @app.route("/")
    def index():
        return redirect(url_for("auth.login"))

    # Minimal inline template for login (for testing purposes only).
    @app.route("/auth/login.html")
    def login_template():
        return """
        <html>
        <head><title>Login</title></head>
        <body>
            <h2>Login</h2>
            <form method="post" action="/auth/login">
                Username: <input type="text" name="username"><br>
                Password: <input type="password" name="password"><br>
                <input type="submit" value="Login">
            </form>
            <p>Don't have an account? <a href="/auth/register">Register here</a>.</p>
        </body>
        </html>
        """

    @app.route("/auth/register.html")
    def register_template():
        return """
        <html>
        <head><title>Register</title></head>
        <body>
            <h2>Register</h2>
            <form method="post" action="/auth/register">
                Username: <input type="text" name="username"><br>
                Email: <input type="email" name="email"><br>
                Password: <input type="password" name="password"><br>
                Region: <input type="text" name="region" value="default"><br>
                <input type="submit" value="Register">
            </form>
            <p>Already have an account? <a href="/auth/login">Login here</a>.</p>
        </body>
        </html>
        """

    @app.route("/auth/profile.html")
    def profile_template():
        return f"""
        <html>
        <head><title>Profile</title></head>
        <body>
            <h2>Welcome, {{% raw %}}{{{{ user.username }}}}{{% endraw %}}</h2>
            <p>Email: {{% raw %}}{{{{ user.email }}}}{{% endraw %}}</p>
            <p>Region: {{% raw %}}{{{{ user.region }}}}{{% endraw %}}</p>
            <a href="/auth/logout">Logout</a>
        </body>
        </html>
        """

    app.run(host="0.0.0.0", port=5002, debug=True)

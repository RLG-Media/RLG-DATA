"""
client_portal.py

This module provides a secure, password-protected client portal for both RLG Data and RLG Fans.
It uses Flask to manage user authentication, session management, and routing for a dashboard that 
displays monitoring results and reports. In a production system, user credentials and sensitive data 
must be stored securely (e.g., in a database with hashed passwords).
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
import logging
from functools import wraps

# Set up logging for the client portal
logger = logging.getLogger("ClientPortal")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

# Create a Flask blueprint for the client portal
client_portal = Blueprint("client_portal", __name__, template_folder="templates", url_prefix="/portal")

# Dummy user credentials for demonstration.
# In production, use a database and secure password hashing.
USERS = {
    "admin": "password123",  # Replace with secure passwords and proper user management
    "user": "userpass"
}

def login_required(f):
    """
    Decorator to protect routes that require a logged-in user.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            flash("Please log in to access the portal.", "warning")
            return redirect(url_for("client_portal.login"))
        return f(*args, **kwargs)
    return decorated_function

@client_portal.route("/login", methods=["GET", "POST"])
def login():
    """
    Handles user login.
    GET: Displays the login form.
    POST: Authenticates the user.
    """
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in USERS and USERS[username] == password:
            session["username"] = username
            flash("Login successful!", "success")
            logger.info(f"User {username} logged in.")
            return redirect(url_for("client_portal.dashboard"))
        else:
            flash("Invalid username or password.", "danger")
            logger.warning(f"Failed login attempt for user {username}.")
    return render_template("login.html")

@client_portal.route("/logout")
@login_required
def logout():
    """
    Logs out the current user.
    """
    username = session.pop("username", None)
    flash("Logged out successfully.", "info")
    logger.info(f"User {username} logged out.")
    return redirect(url_for("client_portal.login"))

@client_portal.route("/dashboard")
@login_required
def dashboard():
    """
    Main dashboard displaying monitoring summaries and reports for both RLG Data and RLG Fans.
    In production, this data should be dynamically retrieved from your databases or API endpoints.
    """
    # Sample data for demonstration purposes.
    rlg_data_summary = {
        "total_mentions": 1250,
        "positive": 850,
        "neutral": 300,
        "negative": 100,
        "latest_report": "Summary of RLG Data report..."
    }
    
    rlg_fans_summary = {
        "total_fans": 50000,
        "active_today": 1200,
        "growth_rate": "2.5%",
        "latest_report": "Summary of RLG Fans report..."
    }
    
    return render_template(
        "dashboard.html", 
        rlg_data=rlg_data_summary, 
        rlg_fans=rlg_fans_summary, 
        user=session.get("username")
    )

@client_portal.route("/api/data")
@login_required
def api_data():
    """
    Internal API endpoint to fetch detailed RLG Data.
    Returns JSON data. In production, replace with actual dynamic data retrieval.
    """
    dummy_data = {
        "data": [
            {"id": 1, "mention": "Sample mention 1", "sentiment": "positive"},
            {"id": 2, "mention": "Sample mention 2", "sentiment": "neutral"}
        ]
    }
    return jsonify(dummy_data)

@client_portal.route("/api/fans")
@login_required
def api_fans():
    """
    Internal API endpoint to fetch detailed RLG Fans data.
    Returns JSON data. In production, replace with actual dynamic data retrieval.
    """
    dummy_fans = {
        "fans": [
            {"id": 101, "name": "Fan 1", "engagement": 75},
            {"id": 102, "name": "Fan 2", "engagement": 60}
        ]
    }
    return jsonify(dummy_fans)

# -------------------------------
# Additional Recommendations:
# -------------------------------
# 1. **Authentication & Security:** Replace the dummy authentication with a secure, database-backed 
#    system (consider Flask-Login) and enforce HTTPS.
# 2. **Template Separation:** Move HTML files (login.html, dashboard.html, etc.) to a 'templates' 
#    directory and use a templating engine (Jinja2) for better maintainability.
# 3. **Input Validation:** Validate all form inputs and sanitize outputs to prevent injection attacks.
# 4. **Error Handling:** Implement robust error handling and logging for production use.
# 5. **Scalability:** Consider caching frequently requested data and using a reverse proxy (e.g., Nginx) 
#    for improved performance.
# 6. **Session Security:** Use secure session management practices (e.g., setting a strong secret key, 
#    using secure cookies, and proper session timeout settings).

# -------------------------------
# For standalone testing purposes, you can run this module directly.
# In production, register the blueprint with your main Flask app.
if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    app.secret_key = "supersecretkey"  # Replace with a secure key in production.
    app.register_blueprint(client_portal)
    
    # Dummy route for testing template rendering if templates are not available.
    @app.route("/portal/login.html")
    def login_template():
        return """
        <html>
        <head><title>Login</title></head>
        <body>
            <h2>Login</h2>
            <form method="post" action="/portal/login">
                <label>Username:</label> <input type="text" name="username"><br>
                <label>Password:</label> <input type="password" name="password"><br>
                <input type="submit" value="Login">
            </form>
        </body>
        </html>
        """
    
    @app.route("/portal/dashboard.html")
    def dashboard_template():
        # In production, use proper templating and data binding.
        return """
        <html>
        <head><title>Dashboard</title></head>
        <body>
            <h2>Dashboard</h2>
            <p>Welcome, {{ user }}!</p>
            <h3>RLG Data Summary</h3>
            <p>Total Mentions: {{ rlg_data.total_mentions }}</p>
            <p>Positive: {{ rlg_data.positive }}</p>
            <p>Neutral: {{ rlg_data.neutral }}</p>
            <p>Negative: {{ rlg_data.negative }}</p>
            <p>Latest Report: {{ rlg_data.latest_report }}</p>
            <h3>RLG Fans Summary</h3>
            <p>Total Fans: {{ rlg_fans.total_fans }}</p>
            <p>Active Today: {{ rlg_fans.active_today }}</p>
            <p>Growth Rate: {{ rlg_fans.growth_rate }}</p>
            <p>Latest Report: {{ rlg_fans.latest_report }}</p>
            <br><a href="/portal/logout">Logout</a>
        </body>
        </html>
        """
    
    app.run(host="0.0.0.0", port=5001, debug=True)

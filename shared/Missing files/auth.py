import bcrypt
import jwt
from flask import Flask, request, jsonify, g
from functools import wraps
from datetime import datetime, timedelta
import os

# Flask application setup
app = Flask(__name__)

# JWT Secret Key and Config
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRY = 15  # Access token validity in minutes
REFRESH_TOKEN_EXPIRY = 7  # Refresh token validity in days

# Mock database
users_db = {}  # Example: {"user1": {"password_hash": "hashed_password", "role": "admin"}}
refresh_tokens = {}  # Example: {"user1": "refresh_token"}

# Utilities
def hash_password(password):
    """Hashes a plain text password."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password, hashed_password):
    """Verifies a plain text password against a hashed password."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def generate_tokens(username):
    """Generates JWT access and refresh tokens."""
    access_payload = {
        "username": username,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRY),
        "iat": datetime.utcnow(),
    }
    refresh_payload = {
        "username": username,
        "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRY),
        "iat": datetime.utcnow(),
    }
    access_token = jwt.encode(access_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    refresh_token = jwt.encode(refresh_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return access_token, refresh_token


def decode_token(token):
    """Decodes a JWT token."""
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}


# Authentication & Authorization Decorators
def login_required(f):
    """Decorator to protect routes that require authentication."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            return jsonify({"error": "Authorization token missing or invalid"}), 401
        token = token.split(" ")[1]
        payload = decode_token(token)
        if "error" in payload:
            return jsonify({"error": payload["error"]}), 401
        g.user = payload["username"]
        return f(*args, **kwargs)
    return wrapper


def role_required(role):
    """Decorator for role-based access control."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not hasattr(g, "user"):
                return jsonify({"error": "User not authenticated"}), 403
            user_data = users_db.get(g.user)
            if not user_data or user_data.get("role") != role:
                return jsonify({"error": "Unauthorized"}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator


# Routes
@app.route("/auth/register", methods=["POST"])
def register():
    """Registers a new user."""
    data = request.json
    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "user")

    if username in users_db:
        return jsonify({"error": "User already exists"}), 400
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    hashed_password = hash_password(password)
    users_db[username] = {"password_hash": hashed_password, "role": role}
    return jsonify({"message": "User registered successfully"}), 201


@app.route("/auth/login", methods=["POST"])
def login():
    """Logs in a user and returns access and refresh tokens."""
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = users_db.get(username)
    if not user or not verify_password(password, user["password_hash"]):
        return jsonify({"error": "Invalid username or password"}), 401

    access_token, refresh_token = generate_tokens(username)
    refresh_tokens[username] = refresh_token
    return jsonify({"access_token": access_token, "refresh_token": refresh_token})


@app.route("/auth/refresh", methods=["POST"])
def refresh():
    """Refreshes the access token using a valid refresh token."""
    data = request.json
    refresh_token = data.get("refresh_token")

    payload = decode_token(refresh_token)
    if "error" in payload:
        return jsonify({"error": payload["error"]}), 401

    username = payload.get("username")
    stored_refresh_token = refresh_tokens.get(username)
    if not stored_refresh_token or stored_refresh_token != refresh_token:
        return jsonify({"error": "Invalid refresh token"}), 403

    access_token, new_refresh_token = generate_tokens(username)
    refresh_tokens[username] = new_refresh_token
    return jsonify({"access_token": access_token, "refresh_token": new_refresh_token})


@app.route("/auth/logout", methods=["POST"])
@login_required
def logout():
    """Logs out a user by invalidating their refresh token."""
    username = g.user
    refresh_tokens.pop(username, None)
    return jsonify({"message": "Logged out successfully"})


@app.route("/protected/admin", methods=["GET"])
@login_required
@role_required("admin")
def admin_only():
    """Example of a protected route for admin users."""
    return jsonify({"message": f"Welcome, {g.user}. You are an admin!"})


@app.route("/protected/user", methods=["GET"])
@login_required
def user_only():
    """Example of a protected route for authenticated users."""
    return jsonify({"message": f"Welcome, {g.user}. You are authenticated!"})


# Main app runner
if __name__ == "__main__":
    app.run(debug=True)

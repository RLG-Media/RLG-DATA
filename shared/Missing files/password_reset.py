import os
import uuid
from flask import Blueprint, request, jsonify, url_for
from werkzeug.security import generate_password_hash
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from backend.models import User, db
from backend.utils import send_email
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Blueprint setup
password_reset_bp = Blueprint("password_reset", __name__)

# Serializer for secure token generation
serializer = URLSafeTimedSerializer(os.getenv("SECRET_KEY"))

# Expiry time for reset tokens (in seconds)
RESET_TOKEN_EXPIRY = 3600  # 1 hour


@password_reset_bp.route("/request-reset", methods=["POST"])
def request_password_reset():
    """
    Handle password reset requests by sending a reset email with a secure token.
    """
    data = request.get_json()
    email = data.get("email")
    
    if not email:
        logger.warning("Password reset request received without email.")
        return jsonify({"error": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        logger.warning(f"Password reset request received for non-existent email: {email}.")
        return jsonify({"error": "User not found"}), 404

    # Generate reset token
    reset_token = serializer.dumps(email, salt="password-reset-salt")

    # Generate reset URL
    reset_url = url_for("password_reset.reset_password", token=reset_token, _external=True)

    # Send email
    subject = "Password Reset Request"
    body = f"""
    Hi {user.username},

    You requested to reset your password. Please use the link below to reset it:
    {reset_url}

    This link will expire in 1 hour. If you did not request this, please ignore this email.
    """
    try:
        send_email(email, subject, body)
    except Exception as e:
        logger.error(f"Failed to send password reset email to {email}: {str(e)}")
        return jsonify({"error": "Failed to send email. Please try again later."}), 500

    logger.info(f"Password reset email sent to {email}")
    return jsonify({"message": "Password reset email sent successfully"}), 200


@password_reset_bp.route("/reset-password/<token>", methods=["POST"])
def reset_password(token):
    """
    Reset the password using the provided token and new password.
    """
    try:
        # Validate token
        email = serializer.loads(token, salt="password-reset-salt", max_age=RESET_TOKEN_EXPIRY)
    except SignatureExpired:
        logger.warning(f"Expired token used for password reset: {token}")
        return jsonify({"error": "Token has expired"}), 400
    except BadSignature:
        logger.warning(f"Invalid token used for password reset: {token}")
        return jsonify({"error": "Invalid token"}), 400

    # Get new password from request
    data = request.get_json()
    new_password = data.get("new_password")

    if not new_password:
        logger.warning(f"Password reset attempt without providing new password. Token: {token}")
        return jsonify({"error": "New password is required"}), 400

    # Find the user and update their password
    user = User.query.filter_by(email=email).first()
    if not user:
        logger.warning(f"Password reset attempt for non-existent email: {email}")
        return jsonify({"error": "User not found"}), 404

    try:
        user.password = generate_password_hash(new_password)
        db.session.commit()
    except Exception as e:
        logger.error(f"Error updating password for email {email}: {str(e)}")
        return jsonify({"error": "Failed to reset password. Please try again later."}), 500

    logger.info(f"Password reset successfully for email {email}")
    return jsonify({"message": "Password reset successfully"}), 200


@password_reset_bp.route("/validate-token/<token>", methods=["GET"])
def validate_token(token):
    """
    Validate a reset token without resetting the password (optional endpoint for front-end validation).
    """
    try:
        # Validate token
        email = serializer.loads(token, salt="password-reset-salt", max_age=RESET_TOKEN_EXPIRY)
        return jsonify({"message": "Token is valid", "email": email}), 200
    except SignatureExpired:
        logger.warning(f"Expired token validation attempt: {token}")
        return jsonify({"error": "Token has expired"}), 400
    except BadSignature:
        logger.warning(f"Invalid token validation attempt: {token}")
        return jsonify({"error": "Invalid token"}), 400

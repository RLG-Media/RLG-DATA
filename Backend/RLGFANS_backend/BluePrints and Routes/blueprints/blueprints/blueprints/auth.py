# auth.py - Authentication and Authorization for RLG Fans

from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    jwt_required, create_access_token, create_refresh_token, get_jwt_identity, jwt_refresh_token_required
)
from flask_mail import Message
from app import db, mail
from models import User
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from config import Config
import logging

# Initialize Blueprint
auth_bp = Blueprint('auth', __name__)

# Initialize timed serializer for secure token handling
serializer = URLSafeTimedSerializer(Config.SECRET_KEY)

# Set up logging
logging.basicConfig(filename='auth.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Endpoint to register a new user.
    Expects JSON with username, email, and password.
    """
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not (username and email and password):
            return jsonify({"error": "Username, email, and password are required"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already registered"}), 409

        user = User(username=username, email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()

        logging.info(f"User registered successfully: {email}")
        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        logging.error(f"Failed to register user: {str(e)}")
        return jsonify({"error": "Failed to register user"}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Endpoint for user login.
    Expects JSON with email and password.
    """
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)

            session['user_id'] = user.id
            logging.info(f"User logged in: {email}")
            return jsonify({"access_token": access_token, "refresh_token": refresh_token}), 200

        logging.warning(f"Failed login attempt for: {email}")
        return jsonify({"error": "Invalid email or password"}), 401

    except Exception as e:
        logging.error(f"Failed to log in user: {str(e)}")
        return jsonify({"error": "Failed to log in user"}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    """
    Endpoint to refresh JWT access token.
    Requires a valid refresh token.
    """
    try:
        user_id = get_jwt_identity()
        access_token = create_access_token(identity=user_id)
        logging.info(f"Access token refreshed for user {user_id}")
        return jsonify({"access_token": access_token}), 200

    except Exception as e:
        logging.error(f"Failed to refresh token: {str(e)}")
        return jsonify({"error": "Failed to refresh token"}), 500


@auth_bp.route('/forgot_password', methods=['POST'])
def forgot_password():
    """
    Endpoint to initiate password reset.
    Sends a reset email with a tokenized link.
    """
    try:
        email = request.json.get('email')
        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        token = serializer.dumps(email, salt=Config.SECRET_KEY)
        reset_url = f"{Config.FRONTEND_URL}/reset_password/{token}"

        msg = Message("Password Reset Request", sender=Config.MAIL_DEFAULT_SENDER, recipients=[email])
        msg.body = f"To reset your password, click the following link: {reset_url}"

        mail.send(msg)
        logging.info(f"Password reset email sent to: {email}")
        return jsonify({"message": "Password reset email sent"}), 200

    except Exception as e:
        logging.error(f"Failed to send password reset email: {str(e)}")
        return jsonify({"error": "Failed to send password reset email"}), 500


@auth_bp.route('/reset_password/<token>', methods=['POST'])
def reset_password(token):
    """
    Endpoint to reset the password using a token.
    Expects JSON with new password.
    """
    try:
        email = serializer.loads(token, salt=Config.SECRET_KEY, max_age=3600)
        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        new_password = request.json.get('password')
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()

        logging.info(f"Password reset successful for: {email}")
        return jsonify({"message": "Password reset successful"}), 200

    except SignatureExpired:
        logging.warning("Password reset token expired")
        return jsonify({"error": "Token expired"}), 400
    except Exception as e:
        logging.error(f"Failed to reset password: {str(e)}")
        return jsonify({"error": "Failed to reset password"}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Endpoint to log out a user.
    Clears the session.
    """
    try:
        user_id = get_jwt_identity()
        session.clear()
        logging.info(f"User logged out: {user_id}")
        return jsonify({"message": "Logged out successfully"}), 200

    except Exception as e:
        logging.error(f"Failed to log out user: {str(e)}")
        return jsonify({"error": "Failed to log out user"}), 500

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from app import db
from flask_limiter import Limiter
from flask import current_app

auth_blueprint = Blueprint('auth', __name__)

# Rate limiter to prevent brute-force attacks on login attempts
limiter = Limiter(key_func=lambda: request.remote_addr)

@auth_blueprint.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")  # Rate limiting: 5 login attempts per minute
def login():
    """
    Handle user login. Check the username and password against the database.
    If successful, set the session variables and redirect to the dashboard.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the user exists in the database
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            # Log the user in by setting session data
            session.clear()  # Clear any previous session
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            current_app.logger.info(f"User {user.username} logged in successfully")
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
            current_app.logger.warning(f"Failed login attempt for username: {username}")
            return redirect(url_for('auth.login'))

    return render_template('login.html')


@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle user registration. Check if the username already exists, then hash
    the password and save the new user in the database.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists!', 'warning')
            current_app.logger.warning(f"Attempt to register with existing username: {username}")
            return redirect(url_for('auth.register'))

        # Create new user with hashed password
        new_user = User(username=username)
        new_user.set_password(password)  # Hash the password using the User model's method

        # Add the user to the database
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            current_app.logger.info(f"New user {username} registered successfully")
            return redirect(url_for('auth.login'))
        except Exception as e:
            current_app.logger.error(f"Error registering user {username}: {str(e)}")
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            return redirect(url_for('auth.register'))

    return render_template('register.html')


@auth_blueprint.route('/logout')
def logout():
    """
    Log the user out by clearing session data, then redirect to the login page.
    """
    session.clear()  # Clear all session data
    flash('You have been logged out.', 'info')
    current_app.logger.info(f"User logged out successfully")
    return redirect(url_for('auth.login'))


@auth_blueprint.before_app_request
def load_logged_in_user():
    """
    Load the logged-in user before every request, if a user ID is in the session.
    This makes user information accessible in templates.
    """
    user_id = session.get('user_id')
    if user_id:
        session['user'] = User.query.get(user_id)  # Load the user from the database
    else:
        session['user'] = None

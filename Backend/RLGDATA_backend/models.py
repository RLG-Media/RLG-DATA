from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    """
    User model for authentication and user management.
    Includes methods for setting and verifying passwords.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)  # Added email field
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Track user creation time

    def set_password(self, password):
        """ Hash the password and store it. """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """ Check if the provided password matches the hashed password. """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Role(db.Model):
    """
    Role model for managing user roles (admin, user, etc.).
    This allows role-based access control in the future.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"<Role {self.name}>"


class UserRole(db.Model):
    """
    UserRole model to assign roles to users.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    user = db.relationship('User', backref='roles', lazy=True)
    role = db.relationship('Role', backref='users', lazy=True)

    def __repr__(self):
        return f"<UserRole User: {self.user_id} - Role: {self.role_id}>"


class Project(db.Model):
    """
    Project model to store user projects.
    Each project contains a name, keywords, and is linked to the user who created it.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    keywords = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=True)  # Optional description for each project
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='projects', lazy=True)

    def __repr__(self):
        return f"<Project {self.name} - User: {self.user.username}>"


class ScrapingTask(db.Model):
    """
    ScrapingTask model for tracking scraping jobs initiated by users.
    Stores the URL, task status, user ID, and results.
    """
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, in-progress, complete, failed
    result = db.Column(db.Text)  # Store the scraped results or link to external storage
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Track task creation time
    completed_at = db.Column(db.DateTime, nullable=True)  # Track task completion time
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='scraping_tasks', lazy=True)

    def __repr__(self):
        return f"<ScrapingTask {self.url} - Status: {self.status}>"


class Invite(db.Model):
    """
    Invite model to store invitations sent to new users.
    Each invite contains an email, role, token, and status (pending, accepted, expired).
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    token = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, accepted, expired
    date_sent = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Invite {self.email} - Status: {self.status}>"

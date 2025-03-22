from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_cors import CORS
from flask import request

# Initialize extensions without binding to the app yet.
db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()
migrate = Migrate()
socketio = SocketIO()
# Configure Limiter with a more flexible key function.
# You can change the key function to incorporate user, IP, or token-based limits.
limiter = Limiter(key_func=lambda: request.headers.get('X-User-ID', request.remote_addr))
cors = CORS()

def init_extensions(app):
    """
    Initialize all Flask extensions and bind them to the application instance.
    
    This function initializes:
      - SQLAlchemy for ORM and database interactions.
      - JWTManager for handling JSON Web Tokens.
      - Mail for sending emails.
      - Migrate for handling database migrations.
      - SocketIO for real-time communication.
      - Limiter for API rate limiting.
      - CORS for enabling Cross-Origin Resource Sharing.
    
    Args:
        app: The Flask application instance.
    
    Additional Recommendations:
      - Review the limiter key function for more granularity (e.g., combine user and IP).
      - Customize CORS settings (e.g., allowed origins) as needed for security.
      - Ensure that mail and JWT configurations are set in your app configuration.
    """
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)
    limiter.init_app(app)
    cors.init_app(app)

    app.logger.info("Extensions initialized successfully.")


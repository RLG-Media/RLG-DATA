from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_limiter import Limiter
from flask_socketio import SocketIO
from flask_migrate import Migrate
from flask_cors import CORS
from celery import Celery
import logging
from dotenv import load_dotenv
import os
from config import Config

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()
limiter = Limiter(key_func=lambda: request.remote_addr)
socketio = SocketIO()
migrate = Migrate()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)

# Function to create the Flask app
def create_app():
    app = Flask(__name__)

    # Load configurations from config.py and .env
    app.config.from_object(Config)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Set up extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    socketio.init_app(app)
    migrate.init_app(app, db)
    celery.conf.update(app.config)
    
    # Enable CORS (Cross-Origin Resource Sharing)
    CORS(app)

    # Register Blueprints
    from .routes import routes_blueprint
    from .search import search_blueprint
    from .data_export import export_blueprint

    app.register_blueprint(routes_blueprint)
    app.register_blueprint(search_blueprint)
    app.register_blueprint(export_blueprint)

    # Error handling
    from .error_handling import log_error

    @app.errorhandler(Exception)
    def handle_exception(error):
        log_error(error)
        return jsonify({'error': 'An internal server error occurred. Our team has been notified.'}), 500

    # Setup logging
    logging.basicConfig(level=logging.INFO, filename='app.log', format='%(asctime)s %(levelname)s: %(message)s')

    return app

# Celery setup for background tasks
def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super().__call__(*args, **kwargs)

    celery.Task = ContextTask
    return celery

# Initialize Celery with the app context
app = create_app()
celery = make_celery(app)

# Run migrations for the database (Run outside of the Flask app)
def run_migrations():
    migrate.init_app(app, db)
    with app.app_context():
        from flask_migrate import upgrade, migrate, init
        init()  # Run this once to initialize migrations
        migrate()
        upgrade()

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)

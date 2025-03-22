from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session, send_file
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta, datetime
import os
import validators
from functools import wraps
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_cors import CORS
from celery import Celery
import logging
import stripe

# Import internal modules
from backend import get_available_tools, get_user_data, limiter
from backend.adaptive_scraper import load_model
from backend.email_utils import send_scraping_completed_email
from pdf_generator import generate_pdf_report
from celery_tasks import scrape_website
from visualization import create_mentions_graph, create_sentiment_graph
from error_handling import log_error
from recommendation_system import recommend_tools
from routes import routes_blueprint
from search import search_blueprint
from data_export import export_blueprint
from extensions import init_extensions
from sentry_sdk.integrations.flask import FlaskIntegration
import sentry_sdk
from logging_config import setup_logging

# Setting up the logger
setup_logging()

# Create the Flask app using a factory pattern
def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable Cross-Origin Resource Sharing

    # Set up configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/rlg_data')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    app.config['CELERY_BROKER_URL'] = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    app.config['CELERY_RESULT_BACKEND'] = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    app.config['STRIPE_PUBLIC_KEY'] = os.getenv('STRIPE_PUBLIC_KEY')
    app.config['STRIPE_SECRET_KEY'] = os.getenv('STRIPE_SECRET_KEY')

    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    mail = Mail(app)
    socketio = SocketIO(app)
    limiter.init_app(app)
    celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    migrate = Migrate(app, db)

    # Stripe API setup
    stripe.api_key = app.config['STRIPE_SECRET_KEY']

    # Sentry SDK for error monitoring
    sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"), integrations=[FlaskIntegration()])

    # Set up logging
    logging.basicConfig(level=logging.INFO, filename='rlg_data.log')

    # Register Blueprints
    app.register_blueprint(search_blueprint)
    app.register_blueprint(export_blueprint)
    app.register_blueprint(routes_blueprint)

    # Error handling
    @app.errorhandler(Exception)
    def handle_exception(error):
        log_error(error)
        return jsonify({'error': 'An internal server error occurred. Our team has been notified.'}), 500

    return app

app = create_app()

# User authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    stripe_customer_id = db.Column(db.String(120), unique=True)
    subscription_status = db.Column(db.String(20), default='inactive')

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    keywords = db.Column(db.String(200))

# API Resources
class UserResource(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        return jsonify(id=user.id, username=user.username, is_admin=user.is_admin, subscription_status=user.subscription_status)

class ProjectResource(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        if user.subscription_status != 'active':
            return jsonify({'message': 'Active subscription required'}), 403
        projects = Project.query.filter_by(user_id=user.id).all()
        return jsonify([{'id': p.id, 'name': p.name, 'keywords': p.keywords} for p in projects])

    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        if user.subscription_status != 'active':
            return jsonify({'message': 'Active subscription required'}), 403
        data = request.get_json()
        new_project = Project(name=data['name'], user_id=user.id, keywords=data['keywords'])
        db.session.add(new_project)
        db.session.commit()
        return jsonify({'message': 'Project created successfully', 'id': new_project.id})

# Routes
@app.route('/dashboard')
@login_required
def dashboard():
    user_data = get_user_data(session['user_id'])
    available_tools = get_available_tools()
    recommended_tools = recommend_tools(user_data, available_tools)
    mentions_graph = create_mentions_graph()
    sentiment_graph = create_sentiment_graph()
    return render_template('dashboard.html', recommended_tools=recommended_tools, mentions_graph=mentions_graph, sentiment_graph=sentiment_graph)

@app.route('/scrape', methods=['POST'])
@limiter.limit("5 per hour")
@login_required
def scrape():
    try:
        url = request.form['url']
        if not validators.url(url):
            flash('Invalid URL.', 'danger')
            return redirect(url_for('dashboard'))
        
        model = load_model()
        scrape_website.delay(url, model)
        send_scraping_completed_email('user@example.com', url)
        logging.info(f"Started scraping for {url} at {datetime.now()}")
        flash('Scraping started. Check back shortly.', 'info')
    except Exception as e:
        logging.error(f"Error during scraping for {url}: {str(e)}")
        flash('Error during scraping.', 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/download_report/<project_name>')
@login_required
def download_report(project_name):
    pdf = generate_pdf_report(project_name)
    return send_file(pdf, as_attachment=True, download_name=f"{project_name}_report.pdf", mimetype='application/pdf')

# WebSocket events for real-time updates
@socketio.on('connect')
def handle_connect():
    logging.info(f"Client connected: {request.sid}")
    emit('message', {'data': 'Connected to RLG DATA WebSocket'})

@socketio.on('disconnect')
def handle_disconnect():
    logging.info(f"Client disconnected: {request.sid}")

# API Endpoints
api = Api(app)  # Ensure API is initialized on the app instance
api.add_resource(UserResource, '/api/user')
api.add_resource(ProjectResource, '/api/projects')

# Start the app with SocketIO
if __name__ == '__main__':
    db.create_all(app=app)  # Create tables
    socketio.run(app)

# In app.py or create_app function
from task_monitoring import task_monitoring
app.register_blueprint(task_monitoring, url_prefix='/monitor')

from backend.routes.password_reset import password_reset_bp
app.register_blueprint(password_reset_bp, url_prefix="/auth")

from flask import Flask
from shared.monitoring import setup_monitoring
app = Flask(__name__)
setup_monitoring(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

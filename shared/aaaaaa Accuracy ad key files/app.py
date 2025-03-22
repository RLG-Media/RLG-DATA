from flask import Flask, jsonify, request, render_template, redirect, url_for, flash, session, send_file
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from flask_mail import Mail
from flask_limiter import Limiter
from flask_cors import CORS
from flask_migrate import Migrate
from celery import Celery
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import timedelta, datetime
import os
import logging
import validators
from dotenv import load_dotenv
from sentry_sdk.integrations.flask import FlaskIntegration
import sentry_sdk

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/shared_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['CELERY_BROKER_URL'] = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
app.config['CELERY_RESULT_BACKEND'] = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
mail = Mail(app)
socketio = SocketIO(app)
limiter = Limiter(get_remote_address, app=app)
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
migrate = Migrate(app, db)

# Sentry SDK for error monitoring
sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"), integrations=[FlaskIntegration()])

# Logging configuration
logging.basicConfig(level=logging.INFO, filename='shared_backend.log')
logger = logging.getLogger(__name__)

# Import internal modules
from backend.adaptive_scraper import load_model
from backend.email_utils import send_scraping_completed_email
from pdf_generator import generate_pdf_report
from celery_tasks import scrape_website, scrape_platform_content
from visualization import create_mentions_graph, create_sentiment_graph
from recommendation_system import recommend_tools
from monitoring import setup_monitoring
from routes import routes_blueprint
from search import search_blueprint
from data_export import export_blueprint
from shared.routes.password_reset import password_reset_bp

# Register Blueprints
app.register_blueprint(routes_blueprint)
app.register_blueprint(search_blueprint)
app.register_blueprint(export_blueprint)
app.register_blueprint(password_reset_bp, url_prefix="/auth")

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

class CreatorAccount(db.Model):
    __tablename__ = 'creator_account'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    platform = db.Column(db.String(50), nullable=False)
    performance_metrics = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# User authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes and API
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
        logger.info(f"Started scraping for {url} at {datetime.now()}")
        flash('Scraping started. Check back shortly.', 'info')
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        flash('Error during scraping.', 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/download_report/<project_name>')
@login_required
def download_report(project_name):
    pdf = generate_pdf_report(project_name)
    return send_file(pdf, as_attachment=True, download_name=f"{project_name}_report.pdf", mimetype='application/pdf')

# WebSocket events
@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected: {request.sid}")
    emit('message', {'data': 'Connected to RLG WebSocket'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"Client disconnected: {request.sid}")

# API Endpoints
api = Api(app)
api.add_resource(UserResource, '/api/user')
api.add_resource(ProjectResource, '/api/projects')

# Error handling
@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request"}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_server_error(error):
    logger.error(f"Unhandled Exception: {error}")
    return jsonify({"error": "Internal server error"}), 500

# Initialize monitoring and run the app
setup_monitoring(app)

if __name__ == '__main__':
    db.create_all()
    socketio.run(app, host="0.0.0.0", port=5000)

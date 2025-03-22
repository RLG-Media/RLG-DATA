# app.py - RLG Fans Backend Service
import os
import logging
from datetime import timedelta
from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_limiter import Limiter
from flask_cors import CORS
from flask_migrate import Migrate
from celery import Celery
from shared.data_models import BasePerformanceMetrics, RegionData
from shared.analytics import ContentAnalyzer, TrendProcessor
from shared.scraping import PlatformScraperFactory
from shared.utilities import validate_email_format, rate_limit_key
from flask_mail import Mail
from shared.exceptions import handle_api_errors

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, template_folder='../templates')
app.config.update({
    'SQLALCHEMY_DATABASE_URI': os.getenv('DATABASE_URL'),
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY'),
    'JWT_ACCESS_TOKEN_EXPIRES': timedelta(hours=1),
    'CELERY_BROKER_URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    'CELERY_RESULT_BACKEND': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    'MAIL_SERVER': os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
    'MAIL_PORT': int(os.getenv('MAIL_PORT', 587)),
    'MAIL_USE_TLS': os.getenv('MAIL_USE_TLS', 'true').lower() == 'true',
    'MAIL_USERNAME': os.getenv('MAIL_USERNAME'),
    'MAIL_PASSWORD': os.getenv('MAIL_PASSWORD'),
    'RATELIMIT_DEFAULT': '500/hour;100/minute',
    'ANALYTICS_CACHE_TTL': int(os.getenv('ANALYTICS_CACHE_TTL', 3600))
})

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
CORS(app, resources={r"/*": {"origins": os.getenv('ALLOWED_ORIGINS', '*')}})
limiter = Limiter(app=app, key_func=rate_limit_key)
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
mail = Mail(app)

# Import shared monitoring setup
from shared.monitoring import setup_monitoring, setup_logging
setup_monitoring(app)
setup_logging()

# Configure logging
logger = logging.getLogger('rlg_fans_backend')
logger.setLevel(logging.INFO)

# Database Models
class CreatorAccount(db.Model, BasePerformanceMetrics):
    __tablename__ = 'creator_accounts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    platform = db.Column(db.String(50), nullable=False, index=True)
    region = db.Column(db.String(50), index=True)
    country = db.Column(db.String(50), index=True)
    city = db.Column(db.String(50), index=True)
    town = db.Column(db.String(50), index=True)
    performance_metrics = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'platform': self.platform,
            'region': self.region,
            'country': self.country,
            'city': self.city,
            'town': self.town,
            'performance_metrics': self.performance_metrics,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# API Routes
@app.route('/rlg_fans/scrape_content', methods=['POST'])
@jwt_required()
@limiter.limit(os.getenv('SCRAPE_RATE_LIMIT', '5/hour'))
@handle_api_errors
def scrape_content():
    """
    Scrapes trending content from specified platforms using shared scraping utilities
    """
    data = request.get_json()
    platform = data.get('platform')
    username = data.get('username')
    region = data.get('region', 'global')
    
    if not platform or not username:
        return jsonify({"error": "Missing platform or username"}), 400
    
    task = scrape_platform_content.delay(platform, username, region)
    logger.info(f"Scraping task queued: {task.id} for {username}@{platform}")
    
    return jsonify({
        "message": "Scraping initiated",
        "task_id": task.id,
        "status_check": f"/tasks/{task.id}/status"
    }), 202

@app.route('/rlg_fans/generate_report', methods=['POST'])
@jwt_required()
@handle_api_errors
def generate_report():
    """
    Generates comprehensive performance report using shared analytics modules
    """
    user_id = get_jwt_identity()
    platform = request.json.get('platform')
    region = request.json.get('region', 'global')
    
    report_data = ContentAnalyzer.generate_report(
        user_id=user_id,
        platform=platform,
        region=region,
        cache_ttl=app.config['ANALYTICS_CACHE_TTL']
    )
    
    return jsonify({
        "report": report_data,
        "metadata": {
            "generated_at": datetime.utcnow().isoformat(),
            "region": region,
            "platform": platform
        }
    }), 200

@app.route('/rlg_fans/trending_analysis', methods=['POST'])
@jwt_required()
@handle_api_errors
def trending_analysis():
    """
    Provides regional trending analysis using shared TrendProcessor
    """
    platform = request.json.get('platform')
    region_data = RegionData(
        region=request.json.get('region'),
        country=request.json.get('country'),
        city=request.json.get('city'),
        town=request.json.get('town')
    )
    
    analysis_results = TrendProcessor.analyze(
        platform=platform,
        region_data=region_data,
        max_results=50
    )
    
    return jsonify({
        "platform": platform,
        "region_data": region_data.to_dict(),
        "trends": analysis_results
    }), 200

# Celery Tasks
@celery.task(bind=True, max_retries=3)
def scrape_platform_content(self, platform, username, region='global'):
    """
    Robust scraping task with retry logic and regional support
    """
    try:
        scraper = PlatformScraperFactory.get_scraper(platform)
        result = scraper.scrape(
            username=username,
            region=region,
            max_retries=3,
            request_timeout=30
        )
        
        # Save results with regional data
        account = CreatorAccount.query.filter_by(username=username, platform=platform).first()
        if not account:
            account = CreatorAccount(username=username, platform=platform)
            
        account.region = region
        account.performance_metrics = result.metrics
        db.session.add(account)
        db.session.commit()
        
        logger.info(f"Successfully scraped {username}@{platform} in {region}")
        return result.to_dict()
        
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
        self.retry(exc=e, countdown=30)

# Email Notifications
@app.route('/rlg_fans/send_report_email', methods=['POST'])
@jwt_required()
@handle_api_errors
def send_report_email():
    data = request.get_json()
    recipient_email = data.get('email')
    platform = data.get('platform')
    
    if not validate_email_format(recipient_email):
        return jsonify({"error": "Invalid email format"}), 400
    
    report_data = ContentAnalyzer.generate_report(
        user_id=get_jwt_identity(),
        platform=platform,
        region=data.get('region', 'global')
    )
    
    msg = mail.EmailMessage()
    msg.subject = f"{platform.capitalize()} Performance Report"
    msg.sender = app.config['MAIL_DEFAULT_SENDER']
    msg.recipients = [recipient_email]
    msg.html = render_template(
        'performance_report.html',
        report=report_data,
        platform=platform
    )
    
    mail.send(msg)
    logger.info(f"Sent performance report to {recipient_email}")
    
    return jsonify({
        "message": "Report delivered successfully",
        "email": recipient_email
    }), 200

# Error Handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "error": "Bad request",
        "details": str(error.description)
    }), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Resource not found",
        "path": request.path
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal Server Error: {str(error)}")
    return jsonify({
        "error": "Internal server error",
        "reference": request.headers.get('X-Request-ID', 'N/A')
    }), 500

# Initialization
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host=os.getenv('HOST', '0.0.0.0'), 
            port=int(os.getenv('PORT', 5000)),
            debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true')

# Register blueprints
from backend.routes.password_reset import password_reset_bp
app.register_blueprint(password_reset_bp, url_prefix="/auth")
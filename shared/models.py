from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """
    User model for creator, brand, and admin accounts.
    Supports role management, authentication, subscription details, and location-based pricing.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False, index=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(50), default='creator')  # 'creator', 'brand', 'admin'
    subscription_status = db.Column(db.String(50), default='inactive')
    location = db.Column(db.String(50), nullable=True)  # Store location (e.g., 'IL' for Israel)

    # Relationships
    platforms = db.relationship('Platform', back_populates='creator', lazy='dynamic')
    campaigns = db.relationship('Campaign', back_populates='user', lazy='dynamic')

    # Methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username} (Role: {self.role})>"

    def set_location(self, location):
        self.location = location

    def get_location(self):
        return self.location

    def is_israel(self):
        return self.location == 'IL'

class Platform(db.Model):
    """
    Represents platforms integrated with RLG Fans.
    Includes API keys and preferences for dynamic configurations.
    """
    __tablename__ = 'platforms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    api_key = db.Column(db.String(200), nullable=True)  # Optional API keys for services
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    creator = db.relationship('User', back_populates='platforms')
    content_data = db.relationship('ContentData', back_populates='platform', lazy='dynamic')
    trend_analyses = db.relationship('TrendAnalysis', back_populates='platform', lazy='dynamic')
    monetization_strategies = db.relationship('MonetizationStrategy', back_populates='platform', lazy='dynamic')
    api_integrations = db.relationship('ExternalAPIIntegration', back_populates='platform', lazy='dynamic')

    def __repr__(self):
        return f"<Platform {self.name} - Creator: {self.creator.username}>"

class ContentData(db.Model):
    """
    Stores performance data for content on various platforms.
    Includes engagement metrics, analysis reports, and monetization details.
    """
    __tablename__ = 'content_data'
    id = db.Column(db.Integer, primary_key=True)
    platform_id = db.Column(db.Integer, db.ForeignKey('platforms.id'), nullable=False)
    platform = db.relationship('Platform', back_populates='content_data')
    content_type = db.Column(db.String(50), nullable=False)  # 'short-form', 'long-form', 'live-stream'
    engagement_score = db.Column(db.Float, nullable=False, default=0.0)
    monetization_score = db.Column(db.Float, nullable=False, default=0.0)
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    shares = db.Column(db.Integer, default=0)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    analysis_report = db.Column(db.Text)  # Detailed content analysis summary

    def __repr__(self):
        return f"<ContentData {self.content_type} for Platform ID {self.platform_id}>"

class TrendAnalysis(db.Model):
    """
    Tracks trending topics and keywords on integrated platforms.
    Supports dynamic updates for content strategy optimization.
    """
    __tablename__ = 'trend_analysis'
    id = db.Column(db.Integer, primary_key=True)
    platform_id = db.Column(db.Integer, db.ForeignKey('platforms.id'), nullable=False)
    platform = db.relationship('Platform', back_populates='trend_analyses')
    keyword = db.Column(db.String(200), nullable=False)
    trend_score = db.Column(db.Float, nullable=False)
    trend_analysis_report = db.Column(db.Text, nullable=True)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<TrendAnalysis {self.keyword} for Platform ID {self.platform_id}>"

class MonetizationStrategy(db.Model):
    """
    Stores recommendations and strategies for monetization.
    Provides actionable insights for pricing, formats, and algorithm optimization.
    """
    __tablename__ = 'monetization_strategy'
    id = db.Column(db.Integer, primary_key=True)
    platform_id = db.Column(db.Integer, db.ForeignKey('platforms.id'), nullable=False)
    platform = db.relationship('Platform', back_populates='monetization_strategies')
    strategy_type = db.Column(db.String(100), nullable=False)  # 'pricing', 'content_format', 'algorithm_optimization'
    suggestion = db.Column(db.Text, nullable=False)
    expected_impact = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<MonetizationStrategy {self.strategy_type} for Platform ID {self.platform_id}>"

class Campaign(db.Model):
    """
    Represents marketing and advertising campaigns.
    Tracks analytics for engagement and revenue generation.
    """
    __tablename__ = 'campaigns'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='campaigns')
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    total_engagement = db.Column(db.Integer, default=0)
    total_revenue = db.Column(db.Float, default=0.0)

    def __repr__(self):
        return f"<Campaign {self.title} - User: {self.user.username}>"

class ExternalAPIIntegration(db.Model):
    """
    Tracks API interactions for external services integrated into RLG Fans.
    Provides logging for monitoring API usage and performance.
    """
    __tablename__ = 'external_api_integrations'
    id = db.Column(db.Integer, primary_key=True)
    platform_id = db.Column(db.Integer, db.ForeignKey('platforms.id'), nullable=False)
    platform = db.relationship('Platform', back_populates='api_integrations')
    api_endpoint = db.Column(db.String(200), nullable=False)
    request_data = db.Column(db.Text, nullable=True)
    response_data = db.Column(db.Text, nullable=True)
    status_code = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ExternalAPIIntegration {self.api_endpoint} - Platform ID {self.platform_id}>"


from flask import Flask, jsonify, request, render_template, redirect, url_for, abort
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt_identity
)
from models import db, User, Platform, ContentData, Campaign, TrendAnalysis, MonetizationStrategy
from werkzeug.exceptions import HTTPException
from datetime import datetime, timedelta
import logging

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rlg_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
db.init_app(app)
jwt = JWTManager(app)

# Logger setup
logger = logging.getLogger(__name__)

# Routes

@app.route("/")
def index():
    return render_template("index.html", title="Welcome to RLG Data")

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        token = create_access_token(identity=user.id, expires_delta=timedelta(hours=1))
        return jsonify({"access_token": token, "user_id": user.id, "role": user.role}), 200
    return jsonify({"message": "Invalid credentials"}), 401

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if User.query.filter((User.email == email) | (User.username == username)).first():
        return jsonify({"message": "User with the same email or username already exists"}), 409

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@app.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "subscription_status": user.subscription_status,
        "created_at": user.created_at
    }), 200

@app.route("/platforms", methods=["GET", "POST"])
@jwt_required()
def manage_platforms():
    user_id = get_jwt_identity()

    if request.method == "GET":
        platforms = Platform.query.filter_by(creator_id=user_id).all()
        return jsonify([{ "id": p.id, "name": p.name, "api_key": p.api_key } for p in platforms]), 200

    elif request.method == "POST":
        data = request.get_json()
        name = data.get("name")
        api_key = data.get("api_key")

        platform = Platform(name=name, api_key=api_key, creator_id=user_id)
        db.session.add(platform)
        db.session.commit()

        return jsonify({"message": "Platform added successfully"}), 201

@app.route("/content-data/<int:platform_id>", methods=["GET"])
@jwt_required()
def get_content_data(platform_id):
    user_id = get_jwt_identity()
    platform = Platform.query.filter_by(id=platform_id, creator_id=user_id).first()

    if not platform:
        return jsonify({"message": "Platform not found or access denied"}), 404

    content_data = ContentData.query.filter_by(platform_id=platform_id).all()
    return jsonify([{ "id": c.id, "content_type": c.content_type, "engagement_score": c.engagement_score, "monetization_score": c.monetization_score, "views": c.views, "likes": c.likes, "comments": c.comments, "shares": c.shares, "posted_at": c.posted_at } for c in content_data]), 200

@app.route("/campaigns", methods=["GET", "POST"])
@jwt_required()
def manage_campaigns():
    user_id = get_jwt_identity()

    if request.method == "GET":
        campaigns = Campaign.query.filter_by(user_id=user_id).all()
        return jsonify([{ "id": c.id, "title": c.title, "description": c.description, "start_date": c.start_date, "end_date": c.end_date, "total_engagement": c.total_engagement, "total_revenue": c.total_revenue } for c in campaigns]), 200

    elif request.method == "POST":
        data = request.get_json()
        title = data.get("title")
        description = data.get("description")
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        campaign = Campaign(
            user_id=user_id,
            title=title,
            description=description,
            start_date=datetime.fromisoformat(start_date),
            end_date=datetime.fromisoformat(end_date) if end_date else None
        )
        db.session.add(campaign)
        db.session.commit()

        return jsonify({"message": "Campaign created successfully"}), 201

@app.route("/trend-analysis", methods=["GET"])
@jwt_required()
def trend_analysis():
    user_id = get_jwt_identity()
    trends = TrendAnalysis.query.filter_by(user_id=user_id).all()
    return jsonify([{ "id": t.id, "keyword": t.keyword, "popularity": t.popularity, "insights": t.insights } for t in trends]), 200

@app.route("/monetization-strategies", methods=["GET"])
@jwt_required()
def monetization_strategies():
    user_id = get_jwt_identity()
    strategies = MonetizationStrategy.query.filter_by(user_id=user_id).all()
    return jsonify([{ "id": m.id, "strategy": m.strategy, "success_rate": m.success_rate } for m in strategies]), 200

@app.route("/support", methods=["GET"])
def support():
    return render_template("support.html", title="Support")

@app.route("/privacy-policy", methods=["GET"])
def privacy_policy():
    return render_template("privacy_policy.html", title="Privacy Policy")

@app.route("/terms-of-service", methods=["GET"])
def terms_of_service():
    return render_template("terms_of_service.html", title="Terms of Service")

@app.errorhandler(HTTPException)
def handle_exception(e):
    response = e.get_response()
    response.data = jsonify({ "code": e.code, "name": e.name, "description": e.description })
    response.content_type = "application/json"
    return response

# Run the app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from werkzeug.exceptions import BadRequest, Unauthorized
from models import User, Content, Notifications  # Assuming these are ORM models for the database
from utils import validate_request_data, paginate_results
from security import rate_limit

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "your_jwt_secret_key"
jwt = JWTManager(app)

# Rate limit decorator (e.g., 100 requests per hour per user)
RATE_LIMIT_RULE = "100/hour"

@app.route("/mobile/auth/login", methods=["POST"])
@rate_limit(rule=RATE_LIMIT_RULE)
def login():
    """
    Endpoint for mobile user login.
    Validates credentials and issues JWT token.
    """
    data = request.json
    validate_request_data(data, required_fields=["username", "password"])

    user = User.authenticate(data["username"], data["password"])
    if not user:
        raise Unauthorized("Invalid username or password.")

    token = create_access_token(identity={"id": user.id, "role": user.role})
    return jsonify({"token": token, "user": user.to_dict()}), 200


@app.route("/mobile/auth/register", methods=["POST"])
@rate_limit(rule=RATE_LIMIT_RULE)
def register():
    """
    Endpoint for mobile user registration.
    Registers a new user and issues a JWT token.
    """
    data = request.json
    validate_request_data(data, required_fields=["username", "password", "email"])

    if User.query.filter_by(username=data["username"]).first():
        raise BadRequest("Username already exists.")

    user = User.create(**data)
    token = create_access_token(identity={"id": user.id, "role": user.role})
    return jsonify({"token": token, "user": user.to_dict()}), 201


@app.route("/mobile/content", methods=["GET"])
@jwt_required()
@rate_limit(rule=RATE_LIMIT_RULE)
def get_content():
    """
    Endpoint to fetch content for the mobile app.
    Supports filtering and pagination.
    """
    filters = {
        "platform": request.args.get("platform"),
        "category": request.args.get("category"),
        "date_range": request.args.get("date_range"),
    }
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))

    content_query = Content.query.filter_by_active(filters)
    paginated_content = paginate_results(content_query, page, per_page)
    return jsonify(paginated_content), 200


@app.route("/mobile/content/<int:content_id>/engagement", methods=["POST"])
@jwt_required()
@rate_limit(rule=RATE_LIMIT_RULE)
def update_engagement(content_id):
    """
    Endpoint to update user engagement with content (e.g., likes, shares).
    """
    data = request.json
    validate_request_data(data, required_fields=["action"])

    content = Content.query.get_or_404(content_id)
    content.update_engagement(action=data["action"], user_id=request.identity["id"])
    return jsonify({"message": "Engagement updated successfully."}), 200


@app.route("/mobile/notifications", methods=["GET"])
@jwt_required()
@rate_limit(rule=RATE_LIMIT_RULE)
def get_notifications():
    """
    Endpoint to fetch user notifications for the mobile app.
    Supports pagination.
    """
    user_id = request.identity["id"]
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))

    notifications_query = Notifications.query.filter_by(user_id=user_id).order_by(Notifications.timestamp.desc())
    paginated_notifications = paginate_results(notifications_query, page, per_page)
    return jsonify(paginated_notifications), 200


@app.route("/mobile/user/profile", methods=["GET"])
@jwt_required()
@rate_limit(rule=RATE_LIMIT_RULE)
def get_user_profile():
    """
    Endpoint to fetch the authenticated user's profile.
    """
    user_id = request.identity["id"]
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200


@app.route("/mobile/user/profile", methods=["PUT"])
@jwt_required()
@rate_limit(rule=RATE_LIMIT_RULE)
def update_user_profile():
    """
    Endpoint to update the authenticated user's profile.
    """
    user_id = request.identity["id"]
    data = request.json

    user = User.query.get_or_404(user_id)
    user.update_profile(data)
    return jsonify({"message": "Profile updated successfully.", "user": user.to_dict()}), 200


@app.route("/mobile/content/upload", methods=["POST"])
@jwt_required()
@rate_limit(rule=RATE_LIMIT_RULE)
def upload_content():
    """
    Endpoint to allow users to upload content via the mobile app.
    """
    data = request.json
    validate_request_data(data, required_fields=["title", "description", "file"])

    content = Content.create(
        user_id=request.identity["id"],
        title=data["title"],
        description=data["description"],
        file=data["file"],
        platform=data.get("platform"),
    )
    return jsonify({"message": "Content uploaded successfully.", "content": content.to_dict()}), 201


@app.errorhandler(BadRequest)
def handle_bad_request(error):
    return jsonify({"error": str(error)}), 400


@app.errorhandler(Unauthorized)
def handle_unauthorized(error):
    return jsonify({"error": str(error)}), 401


if __name__ == "__main__":
    app.run(debug=True)

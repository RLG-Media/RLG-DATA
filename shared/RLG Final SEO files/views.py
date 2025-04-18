from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from backend.api_integration import fetch_data_from_api, post_data_to_api
from shared.error_handling import APIError, validate_request_data
from backend.models import User, Platform, Campaign
from flask import current_app as app

# Create a Blueprint for the views
views = Blueprint("views", __name__)

# Home Page
@views.route("/", methods=["GET"])
@login_required
def home():
    """
    Renders the home/dashboard page for the logged-in user, showing personalized data.
    """
    try:
        # Fetch user-related data from an API or database
        user_data = fetch_data_from_api(f"/users/{current_user.id}")
        
        # Example of platform data integration
        platforms = Platform.query.filter_by(creator_id=current_user.id).all()
        
        # Return dashboard page with user and platform data
        return render_template("dashboard.html", user=current_user, data=user_data, platforms=platforms)
    
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        app.logger.error(f"Error loading dashboard: {e}")
        return jsonify({"error": "Failed to load the dashboard. Please try again later."}), 500


# Service Page
@views.route("/service/<string:service_name>", methods=["GET"])
@login_required
def service_page(service_name):
    """
    Renders a dynamic page for a specific service (e.g., 'facebook', 'tiktok').
    Fetches service-specific data for the logged-in user.
    """
    try:
        service_data = fetch_data_from_api(f"/services/{service_name}")
        return render_template("service_pages.html", service=service_name, data=service_data)
    
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        app.logger.error(f"Error loading service: {service_name} - {e}")
        return jsonify({"error": f"Failed to load service: {service_name}."}), 500


# Settings Page
@views.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """
    Handles settings updates for the current user, including profile and preferences.
    Supports both GET (view) and POST (update) methods.
    """
    if request.method == "GET":
        return render_template("settings.html", user=current_user)
    
    elif request.method == "POST":
        try:
            data = request.form.to_dict()
            required_fields = ["email", "notification_preferences"]
            validate_request_data(data, required_fields)
            
            # Example: Update user settings via API or database
            post_data_to_api(f"/users/{current_user.id}/settings", data)
            return redirect(url_for("views.settings"))
        
        except APIError as e:
            return jsonify(e.to_dict()), e.status_code
        except Exception as e:
            app.logger.error(f"Error updating settings: {e}")
            return jsonify({"error": "Failed to update settings. Please try again later."}), 500


# Analytics Page
@views.route("/analytics", methods=["GET"])
@login_required
def analytics():
    """
    Renders the analytics page with personalized insights, charts, and engagement metrics.
    """
    try:
        # Example: Fetch analytics data from API or generate on the fly
        analytics_data = fetch_data_from_api("/analytics")
        
        # You may want to include user-specific data here
        user_analytics = Campaign.query.filter_by(user_id=current_user.id).all()
        
        return render_template("analytics.html", user=current_user, analytics=analytics_data, campaigns=user_analytics)
    
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        app.logger.error(f"Error loading analytics: {e}")
        return jsonify({"error": "Failed to load analytics. Please try again later."}), 500


# API Integration Testing Page
@views.route("/test-api", methods=["POST"])
@login_required
def test_api():
    """
    Endpoint to test API integration.
    Accepts JSON payload and forwards it to an external API for testing.
    """
    try:
        data = request.get_json()
        required_fields = ["endpoint", "payload"]
        validate_request_data(data, required_fields)

        # Forward data to the specified API endpoint
        response = post_data_to_api(data["endpoint"], data["payload"])
        return jsonify({"message": "API tested successfully", "response": response}), 200
    
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        app.logger.error(f"API test failed: {e}")
        return jsonify({"error": "API testing failed. Please check the input and try again."}), 500


# Error Pages
@views.app_errorhandler(404)
def page_not_found(e):
    """
    Custom 404 error page.
    """
    app.logger.error(f"404 Error: {e}")
    return render_template("404.html"), 404


@views.app_errorhandler(500)
def internal_server_error(e):
    """
    Custom 500 error page.
    """
    app.logger.error(f"500 Error: {e}")
    return render_template("500.html"), 500


# Additional Routes (e.g., for new services)
@views.route("/new-feature", methods=["GET"])
@login_required
def new_feature():
    """
    Placeholder for a new feature or service page, such as a marketing campaign or platform service.
    """
    try:
        # Here you could render a page for a new feature, for example, a platform analytics page
        return render_template("new_feature.html", user=current_user)
    
    except Exception as e:
        app.logger.error(f"Error loading new feature: {e}")
        return jsonify({"error": "Failed to load new feature. Please try again later."}), 500


# Service-specific API Integration (if needed)
@views.route("/platforms/<int:platform_id>/integrations", methods=["GET", "POST"])
@login_required
def platform_integrations(platform_id):
    """
    Manage API integrations for a specific platform (like Facebook, Instagram, etc.)
    Handles both GET (view integrations) and POST (add or update integrations) methods.
    """
    if request.method == "GET":
        try:
            platform = Platform.query.get_or_404(platform_id)
            integrations = platform.api_integrations
            return render_template("platform_integrations.html", platform=platform, integrations=integrations)
        
        except Exception as e:
            app.logger.error(f"Error fetching integrations for platform {platform_id}: {e}")
            return jsonify({"error": "Failed to load integrations. Please try again later."}), 500
    
    elif request.method == "POST":
        try:
            # Example: Add a new integration for a platform
            data = request.form.to_dict()
            required_fields = ["api_endpoint", "api_key"]
            validate_request_data(data, required_fields)

            # Create a new ExternalAPIIntegration
            new_integration = ExternalAPIIntegration(
                platform_id=platform_id,
                api_endpoint=data["api_endpoint"],
                api_key=data["api_key"],
            )
            db.session.add(new_integration)
            db.session.commit()
            
            return redirect(url_for("views.platform_integrations", platform_id=platform_id))
        
        except Exception as e:
            app.logger.error(f"Error adding integration for platform {platform_id}: {e}")
            return jsonify({"error": "Failed to add integration. Please try again later."}), 500

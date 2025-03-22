# api_routes.py - RLG Data and RLG Fans API Routes Integration

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from shared.logging_config import logger
from backend.data_ingestion import ingest_data
from backend.analytics_engine import perform_analytics
from backend.scraper_utils import scrape_platform_content
from backend.report_generator import generate_comprehensive_report
from backend.trending_analysis import analyze_trends
from backend.authentication_utils import validate_user_permissions
from backend.email_notifications import send_notification
from backend.cache_management import get_cached_data, cache_data
from backend.error_handlers import handle_api_errors
from backend.external_apis import fetch_external_data
from backend.notification_system import send_push_notification

# Define Blueprint
api_routes = Blueprint("api_routes", __name__, url_prefix="/api")

# API Routes for RLG Data and RLG Fans

@api_routes.route("/data/ingest", methods=["POST"])
@jwt_required()
@handle_api_errors
def data_ingestion_route():
    """
    Route to ingest raw data from supported sources.
    """
    try:
        user_id = get_jwt_identity()
        data_source = request.json.get("source")
        validate_user_permissions(user_id, action="data_ingestion")

        logger.info(f"User {user_id} initiated data ingestion from {data_source}.")
        ingestion_result = ingest_data(data_source)

        return jsonify({"message": "Data ingestion successful", "result": ingestion_result}), 200
    except Exception as e:
        logger.error(f"Error in data ingestion: {e}")
        return jsonify({"error": "Data ingestion failed"}), 500


@api_routes.route("/analytics/perform", methods=["POST"])
@jwt_required()
@handle_api_errors
def analytics_route():
    """
    Route to perform analytics on ingested data.
    """
    try:
        user_id = get_jwt_identity()
        dataset_id = request.json.get("dataset_id")
        analysis_type = request.json.get("type", "basic")

        logger.info(f"User {user_id} requested analytics on dataset {dataset_id}.")
        analysis_result = perform_analytics(dataset_id, analysis_type)

        return jsonify({"message": "Analytics completed", "result": analysis_result}), 200
    except Exception as e:
        logger.error(f"Error in analytics: {e}")
        return jsonify({"error": "Analytics operation failed"}), 500


@api_routes.route("/fans/scrape", methods=["POST"])
@jwt_required()
@handle_api_errors
def fans_scrape_route():
    """
    Route to scrape platform content for RLG Fans.
    """
    try:
        user_id = get_jwt_identity()
        platform = request.json.get("platform")
        username = request.json.get("username")
        validate_user_permissions(user_id, action="content_scraping")

        logger.info(f"User {user_id} initiated scraping for {username} on {platform}.")
        scrape_result = scrape_platform_content(platform, username)

        return jsonify({"message": "Scraping completed", "result": scrape_result}), 200
    except Exception as e:
        logger.error(f"Error in content scraping: {e}")
        return jsonify({"error": "Content scraping failed"}), 500


@api_routes.route("/reports/generate", methods=["POST"])
@jwt_required()
@handle_api_errors
def generate_report_route():
    """
    Route to generate a comprehensive report for RLG Fans or RLG Data.
    """
    try:
        user_id = get_jwt_identity()
        platform = request.json.get("platform")
        report_scope = request.json.get("scope", "platform_overview")

        logger.info(f"User {user_id} requested report generation for {platform}.")
        report_data = generate_comprehensive_report(user_id, platform, report_scope)

        return jsonify({"message": "Report generated successfully", "report": report_data}), 200
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return jsonify({"error": "Report generation failed"}), 500


@api_routes.route("/trends/analyze", methods=["POST"])
@jwt_required()
@handle_api_errors
def trending_analysis_route():
    """
    Route to analyze trends for specific platforms.
    """
    try:
        platform = request.json.get("platform")
        trend_type = request.json.get("trend_type", "engagement")

        logger.info(f"Trend analysis initiated for {platform} with type {trend_type}.")
        trends = analyze_trends(platform, trend_type)

        return jsonify({"message": "Trend analysis successful", "trends": trends}), 200
    except Exception as e:
        logger.error(f"Error in trend analysis: {e}")
        return jsonify({"error": "Trend analysis failed"}), 500


@api_routes.route("/notifications/send", methods=["POST"])
@jwt_required()
@handle_api_errors
def send_notification_route():
    """
    Route to send notifications to users or creators.
    """
    try:
        user_id = get_jwt_identity()
        notification_type = request.json.get("type")
        target_user_id = request.json.get("target_user_id")

        logger.info(f"User {user_id} sending notification of type {notification_type}.")
        notification_result = send_push_notification(user_id, target_user_id, notification_type)

        return jsonify({"message": "Notification sent successfully", "result": notification_result}), 200
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        return jsonify({"error": "Notification sending failed"}), 500


@api_routes.route("/cache/get", methods=["GET"])
@jwt_required()
@handle_api_errors
def get_cache_route():
    """
    Route to retrieve cached data.
    """
    try:
        cache_key = request.args.get("key")
        cached_data = get_cached_data(cache_key)

        return jsonify({"message": "Cache retrieved successfully", "data": cached_data}), 200
    except Exception as e:
        logger.error(f"Error retrieving cache: {e}")
        return jsonify({"error": "Cache retrieval failed"}), 500


@api_routes.route("/cache/set", methods=["POST"])
@jwt_required()
@handle_api_errors
def set_cache_route():
    """
    Route to set data into the cache.
    """
    try:
        cache_key = request.json.get("key")
        cache_value = request.json.get("value")
        ttl = request.json.get("ttl", 3600)  # Default TTL of 1 hour

        cache_data(cache_key, cache_value, ttl)

        return jsonify({"message": "Cache set successfully"}), 200
    except Exception as e:
        logger.error(f"Error setting cache: {e}")
        return jsonify({"error": "Cache setting failed"}), 500

# search_blueprint.py - Search Functionality for RLG Fans

from flask import Blueprint, jsonify, request, current_app
from models import Project, User
from utils.search_utils import search_content, search_analytics, search_trending_topics
import logging

# Initialize Blueprint
search_blueprint = Blueprint('search', __name__)

# Set up logging
logging.basicConfig(level=logging.INFO, filename='search.log', format='%(asctime)s %(levelname)s: %(message)s')

@search_blueprint.route('/search/content', methods=['POST'])
def search_content_route():
    """
    Search for content across projects based on keywords and filters.
    """
    try:
        data = request.get_json()
        keyword = data.get('keyword')
        filters = data.get('filters', {})
        
        if not keyword:
            return jsonify({"error": "Keyword is required for search"}), 400

        # Call search utility to fetch content based on keyword and filters
        results = search_content(keyword, filters)
        logging.info(f"Content search performed with keyword: {keyword}")

        return jsonify({"results": results}), 200

    except Exception as e:
        logging.error(f"Error during content search: {str(e)}")
        return jsonify({"error": "Failed to perform content search"}), 500


@search_blueprint.route('/search/analytics', methods=['POST'])
def search_analytics_route():
    """
    Search and analyze user engagement data and trends.
    """
    try:
        data = request.get_json()
        keyword = data.get('keyword')
        date_range = data.get('date_range', {})
        
        if not keyword:
            return jsonify({"error": "Keyword is required for search"}), 400

        # Call search utility for analytics based on keyword and date range
        results = search_analytics(keyword, date_range)
        logging.info(f"Analytics search performed with keyword: {keyword}")

        return jsonify({"results": results}), 200

    except Exception as e:
        logging.error(f"Error during analytics search: {str(e)}")
        return jsonify({"error": "Failed to perform analytics search"}), 500


@search_blueprint.route('/search/trending', methods=['POST'])
def search_trending_route():
    """
    Fetch trending topics from integrated platforms based on user-defined filters.
    """
    try:
        data = request.get_json()
        platform = data.get('platform')
        filters = data.get('filters', {})

        if not platform:
            return jsonify({"error": "Platform is required for trending search"}), 400

        # Call search utility to fetch trending topics
        results = search_trending_topics(platform, filters)
        logging.info(f"Trending topics search performed for platform: {platform}")

        return jsonify({"results": results}), 200

    except Exception as e:
        logging.error(f"Error during trending search: {str(e)}")
        return jsonify({"error": "Failed to perform trending search"}), 500


@search_blueprint.route('/search/users', methods=['GET'])
def search_users():
    """
    Search for users by username or other criteria.
    """
    try:
        username = request.args.get('username')
        role = request.args.get('role')

        if not username and not role:
            return jsonify({"error": "At least one search criterion (username or role) is required"}), 400

        # Query database for users based on criteria
        query = User.query
        if username:
            query = query.filter(User.username.ilike(f"%{username}%"))
        if role:
            query = query.join(User.roles).filter(User.role == role)

        users = query.all()
        user_list = [{"id": user.id, "username": user.username, "role": user.role.name} for user in users]

        logging.info("User search performed with criteria: " + str(request.args))

        return jsonify({"results": user_list}), 200

    except Exception as e:
        logging.error(f"Error during user search: {str(e)}")
        return jsonify({"error": "Failed to search users"}), 500

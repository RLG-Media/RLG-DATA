from flask import Blueprint, request, jsonify
from sqlalchemy import or_, func
from models import Project, SocialMediaData
from app import db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create a Blueprint for search-related routes
search_blueprint = Blueprint('search', __name__, url_prefix='/search')


### FULL-TEXT SEARCH FUNCTION ###

@search_blueprint.route('/projects', methods=['GET'])
def search_projects():
    """
    Search for projects based on keywords in the project name or description.
    
    :return: JSON response with search results
    """
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'error': 'Search query is required.'}), 400

        # Perform a full-text search on the project name and description
        results = Project.query.filter(
            or_(
                Project.name.ilike(f'%{query}%'),
                Project.description.ilike(f'%{query}%')
            )
        ).all()

        project_data = [
            {
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'keywords': project.keywords,
                'created_at': project.created_at
            } for project in results
        ]
        
        return jsonify({'projects': project_data}), 200

    except Exception as e:
        logging.error(f"Error searching projects: {e}")
        return jsonify({'error': 'Failed to search projects.'}), 500


@search_blueprint.route('/mentions', methods=['GET'])
def search_mentions():
    """
    Search for social media mentions based on keywords or content.
    
    :return: JSON response with search results
    """
    try:
        query = request.args.get('q', '').strip()
        platform = request.args.get('platform')  # Optional platform filter
        if not query:
            return jsonify({'error': 'Search query is required.'}), 400

        # Perform a full-text search on the mention content
        mention_query = SocialMediaData.query.filter(
            SocialMediaData.content.ilike(f'%{query}%')
        )

        # Apply platform filter if provided
        if platform:
            mention_query = mention_query.filter_by(platform=platform)

        mentions = mention_query.all()

        mention_data = [
            {
                'id': mention.id,
                'platform': mention.platform,
                'content': mention.content,
                'created_at': mention.created_at
            } for mention in mentions
        ]
        
        return jsonify({'mentions': mention_data}), 200

    except Exception as e:
        logging.error(f"Error searching mentions: {e}")
        return jsonify({'error': 'Failed to search mentions.'}), 500


### FILTERING AND PAGINATION ###

@search_blueprint.route('/mentions/filtered', methods=['GET'])
def search_mentions_filtered():
    """
    Search for mentions and apply filters like date range or platform.
    
    :return: JSON response with search results
    """
    try:
        query = request.args.get('q', '').strip()
        platform = request.args.get('platform')  # Optional platform filter
        start_date = request.args.get('start_date')  # Optional start date filter
        end_date = request.args.get('end_date')  # Optional end date filter
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        if not query:
            return jsonify({'error': 'Search query is required.'}), 400

        mention_query = SocialMediaData.query.filter(
            SocialMediaData.content.ilike(f'%{query}%')
        )

        # Apply platform filter
        if platform:
            mention_query = mention_query.filter_by(platform=platform)

        # Apply date range filter
        if start_date:
            mention_query = mention_query.filter(SocialMediaData.created_at >= start_date)
        if end_date:
            mention_query = mention_query.filter(SocialMediaData.created_at <= end_date)

        # Apply pagination
        paginated_results = mention_query.paginate(page, per_page, False)

        mention_data = [
            {
                'id': mention.id,
                'platform': mention.platform,
                'content': mention.content,
                'created_at': mention.created_at
            } for mention in paginated_results.items
        ]

        return jsonify({
            'mentions': mention_data,
            'page': paginated_results.page,
            'total_pages': paginated_results.pages,
            'total_mentions': paginated_results.total
        }), 200

    except Exception as e:
        logging.error(f"Error searching mentions with filters: {e}")
        return jsonify({'error': 'Failed to search mentions.'}), 500


### SEARCH OPTIMIZATION (OPTIONAL) ###

def optimize_search_indexes():
    """
    Add full-text search indexes to optimize search queries.
    This is optional but improves search performance.
    """
    try:
        # Add a full-text search index on the content column of the SocialMediaData table
        db.session.execute("CREATE INDEX IF NOT EXISTS idx_content_search ON social_media_data (content)")
        db.session.commit()
        logging.info("Added index on 'content' in SocialMediaData table.")

        # Add indexes on project name and description for faster search queries
        db.session.execute("CREATE INDEX IF NOT EXISTS idx_project_name ON project (name)")
        db.session.execute("CREATE INDEX IF NOT EXISTS idx_project_description ON project (description)")
        db.session.commit()
        logging.info("Added indexes on 'name' and 'description' in Project table.")

    except Exception as e:
        logging.error(f"Error optimizing search indexes: {e}")


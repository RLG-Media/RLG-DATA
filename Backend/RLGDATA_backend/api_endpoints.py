from flask import Blueprint, jsonify, request
from app import db
from models import Project, User, SocialMediaData, TrendAnalysis, MonetizationStrategy
from api_integration import fetch_and_save_data, fetch_trend_analysis, fetch_monetization_strategy
from auth import token_required  # Assume this is a decorator for token-based authentication
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create a Blueprint for the API
api_blueprint = Blueprint('api', __name__, url_prefix='/api')

@api_blueprint.route('/projects', methods=['GET'])
@token_required
def get_projects(current_user):
    try:
        projects = Project.query.filter_by(user_id=current_user.id).all()
        project_data = [
            {
                'id': project.id,
                'name': project.name,
                'keywords': project.keywords,
                'description': project.description,
                'created_at': project.created_at
            } for project in projects
        ]
        return jsonify({'projects': project_data}), 200

    except Exception as e:
        logging.error(f"Error fetching projects: {e}")
        return jsonify({'error': 'Failed to retrieve projects'}), 500

@api_blueprint.route('/projects/<int:project_id>', methods=['GET'])
@token_required
def get_project(current_user, project_id):
    try:
        project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
        if not project:
            return jsonify({'error': 'Project not found'}), 404

        project_data = {
            'id': project.id,
            'name': project.name,
            'keywords': project.keywords,
            'description': project.description,
            'created_at': project.created_at
        }
        return jsonify({'project': project_data}), 200

    except Exception as e:
        logging.error(f"Error fetching project {project_id}: {e}")
        return jsonify({'error': 'Failed to retrieve project'}), 500

@api_blueprint.route('/projects', methods=['POST'])
@token_required
def create_project(current_user):
    try:
        data = request.get_json()
        project_name = data['name']
        keywords = data['keywords']
        description = data.get('description', '')

        new_project = Project(
            name=project_name,
            keywords=keywords,
            description=description,
            user_id=current_user.id
        )
        db.session.add(new_project)
        db.session.commit()

        project_data = {
            'id': new_project.id,
            'name': new_project.name,
            'keywords': new_project.keywords,
            'description': new_project.description,
            'created_at': new_project.created_at
        }
        return jsonify({'project': project_data}), 201

    except Exception as e:
        logging.error(f"Error creating project: {e}")
        return jsonify({'error': 'Failed to create project'}), 500

@api_blueprint.route('/projects/<int:project_id>', methods=['PUT'])
@token_required
def update_project(current_user, project_id):
    try:
        project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
        if not project:
            return jsonify({'error': 'Project not found'}), 404

        data = request.get_json()
        project.name = data['name']
        project.keywords = data['keywords']
        project.description = data.get('description', project.description)

        db.session.commit()

        project_data = {
            'id': project.id,
            'name': project.name,
            'keywords': project.keywords,
            'description': project.description,
            'created_at': project.created_at
        }
        return jsonify({'project': project_data}), 200

    except Exception as e:
        logging.error(f"Error updating project {project_id}: {e}")
        return jsonify({'error': 'Failed to update project'}), 500

@api_blueprint.route('/projects/<int:project_id>', methods=['DELETE'])
@token_required
def delete_project(current_user, project_id):
    try:
        project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
        if not project:
            return jsonify({'error': 'Project not found'}), 404

        db.session.delete(project)
        db.session.commit()

        return jsonify({'message': 'Project deleted successfully'}), 200

    except Exception as e:
        logging.error(f"Error deleting project {project_id}: {e}")
        return jsonify({'error': 'Failed to delete project'}), 500

@api_blueprint.route('/projects/<int:project_id>/scrape', methods=['POST'])
@token_required
def run_scraping_task(current_user, project_id):
    try:
        project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
        if not project:
            return jsonify({'error': 'Project not found'}), 404

        keywords = project.keywords.split(',')
        for keyword in keywords:
            logging.info(f"Running scraping task for project: {project.name} on keyword: {keyword}")
            fetch_and_save_data(keyword)

        return jsonify({'message': 'Scraping task completed successfully'}), 200

    except Exception as e:
        logging.error(f"Error running scraping task for project {project_id}: {e}")
        return jsonify({'error': 'Failed to run scraping task'}), 500

@api_blueprint.route('/data/<int:project_id>', methods=['GET'])
@token_required
def get_project_data(current_user, project_id):
    try:
        project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
        if not project:
            return jsonify({'error': 'Project not found'}), 404

        social_data = SocialMediaData.query.filter_by(project_id=project_id).all()
        data = [
            {
                'platform': item.platform,
                'content': item.content,
                'created_at': item.created_at
            } for item in social_data
        ]
        return jsonify({'data': data}), 200

    except Exception as e:
        logging.error(f"Error fetching project data for {project_id}: {e}")
        return jsonify({'error': 'Failed to retrieve project data'}), 500

@api_blueprint.route('/projects/<int:project_id>/trend-analysis', methods=['GET'])
@token_required
def get_trend_analysis(current_user, project_id):
    try:
        project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
        if not project:
            return jsonify({'error': 'Project not found'}), 404

        trend_analysis = TrendAnalysis.query.filter_by(project_id=project_id).all()
        trend_data = [
            {
                'trend': item.trend,
                'score': item.score,
                'created_at': item.created_at
            } for item in trend_analysis
        ]
        return jsonify({'trend_analysis': trend_data}), 200

    except Exception as e:
        logging.error(f"Error fetching trend analysis for project {project_id}: {e}")
        return jsonify({'error': 'Failed to retrieve trend analysis'}), 500

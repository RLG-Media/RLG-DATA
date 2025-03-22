import csv
import json
import io
import pandas as pd
from flask import Blueprint, request, jsonify, make_response
from models import Project, SocialMediaData
from app import db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create a Blueprint for data export routes
export_blueprint = Blueprint('export', __name__, url_prefix='/export')


### CSV EXPORT ###

@export_blueprint.route('/projects/csv', methods=['GET'])
def export_projects_csv():
    """
    Export project data to CSV format.
    
    :return: CSV file response
    """
    try:
        # Query all projects
        projects = Project.query.all()

        # Create an in-memory CSV file
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Name', 'Description', 'Keywords', 'Created At'])

        # Write project data
        for project in projects:
            writer.writerow([project.id, project.name, project.description, project.keywords, project.created_at])

        # Prepare response
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=projects.csv'
        response.headers['Content-Type'] = 'text/csv'
        return response

    except Exception as e:
        logging.error(f"Error exporting projects to CSV: {e}")
        return jsonify({'error': 'Failed to export projects to CSV'}), 500


### EXCEL EXPORT ###

@export_blueprint.route('/projects/excel', methods=['GET'])
def export_projects_excel():
    """
    Export project data to Excel format.
    
    :return: Excel file response
    """
    try:
        # Query all projects
        projects = Project.query.all()

        # Create a Pandas DataFrame
        project_data = [
            {'ID': project.id, 'Name': project.name, 'Description': project.description,
             'Keywords': project.keywords, 'Created At': project.created_at}
            for project in projects
        ]
        df = pd.DataFrame(project_data)

        # Create an in-memory Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Projects')

        # Prepare response
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=projects.xlsx'
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        return response

    except Exception as e:
        logging.error(f"Error exporting projects to Excel: {e}")
        return jsonify({'error': 'Failed to export projects to Excel'}), 500


### JSON EXPORT ###

@export_blueprint.route('/projects/json', methods=['GET'])
def export_projects_json():
    """
    Export project data to JSON format.
    
    :return: JSON file response
    """
    try:
        # Query all projects
        projects = Project.query.all()

        # Create JSON structure
        project_data = [
            {'id': project.id, 'name': project.name, 'description': project.description,
             'keywords': project.keywords, 'created_at': project.created_at.isoformat()}
            for project in projects
        ]

        # Prepare response
        response = jsonify({'projects': project_data})
        response.headers['Content-Disposition'] = 'attachment; filename=projects.json'
        return response

    except Exception as e:
        logging.error(f"Error exporting projects to JSON: {e}")
        return jsonify({'error': 'Failed to export projects to JSON'}), 500


### EXPORT FILTERS ###

@export_blueprint.route('/mentions/csv', methods=['GET'])
def export_mentions_csv():
    """
    Export filtered social media mentions to CSV format based on platform or date range.
    
    :return: CSV file response
    """
    try:
        platform = request.args.get('platform')  # Optional platform filter
        start_date = request.args.get('start_date')  # Optional start date filter
        end_date = request.args.get('end_date')  # Optional end date filter

        mention_query = SocialMediaData.query

        # Apply platform filter
        if platform:
            mention_query = mention_query.filter_by(platform=platform)

        # Apply date range filter
        if start_date:
            mention_query = mention_query.filter(SocialMediaData.created_at >= start_date)
        if end_date:
            mention_query = mention_query.filter(SocialMediaData.created_at <= end_date)

        # Fetch the filtered mentions
        mentions = mention_query.all()

        # Create an in-memory CSV file
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(['ID', 'Platform', 'Content', 'Created At'])

        # Write mention data
        for mention in mentions:
            writer.writerow([mention.id, mention.platform, mention.content, mention.created_at])

        # Prepare response
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=mentions.csv'
        response.headers['Content-Type'] = 'text/csv'
        return response

    except Exception as e:
        logging.error(f"Error exporting mentions to CSV: {e}")
        return jsonify({'error': 'Failed to export mentions to CSV'}), 500

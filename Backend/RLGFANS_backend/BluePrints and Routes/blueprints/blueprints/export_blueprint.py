# export_blueprint.py - Export Data and Reports in RLG Fans

from flask import Blueprint, jsonify, send_file, request, current_app
from datetime import datetime
import os
import logging
from io import BytesIO
from pdf_generator import generate_pdf_report
from models import Project, User
from utils.file_utils import export_csv, export_json
from werkzeug.utils import secure_filename
from config import Config

# Initialize Blueprint
export_blueprint = Blueprint('export', __name__)

# Set up logging
logging.basicConfig(level=logging.INFO, filename='export.log', format='%(asctime)s %(levelname)s: %(message)s')


@export_blueprint.route('/export/pdf/<int:project_id>', methods=['GET'])
def export_pdf(project_id):
    """
    Export project report as PDF.
    """
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({"error": "Project not found"}), 404

        pdf_file = generate_pdf_report(project)
        logging.info(f"PDF report generated for project ID: {project_id}")

        return send_file(
            BytesIO(pdf_file),
            as_attachment=True,
            download_name=f"{secure_filename(project.name)}_report_{datetime.now().strftime('%Y%m%d')}.pdf",
            mimetype='application/pdf'
        )

    except Exception as e:
        logging.error(f"Failed to export PDF for project ID {project_id}: {str(e)}")
        return jsonify({"error": "Failed to generate PDF report"}), 500


@export_blueprint.route('/export/csv/<int:project_id>', methods=['GET'])
def export_csv_data(project_id):
    """
    Export project data as CSV.
    """
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({"error": "Project not found"}), 404

        csv_data = export_csv(project)
        logging.info(f"CSV report generated for project ID: {project_id}")

        return send_file(
            BytesIO(csv_data),
            as_attachment=True,
            download_name=f"{secure_filename(project.name)}_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mimetype='text/csv'
        )

    except Exception as e:
        logging.error(f"Failed to export CSV for project ID {project_id}: {str(e)}")
        return jsonify({"error": "Failed to export CSV data"}), 500


@export_blueprint.route('/export/json/<int:project_id>', methods=['GET'])
def export_json_data(project_id):
    """
    Export project data as JSON.
    """
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({"error": "Project not found"}), 404

        json_data = export_json(project)
        logging.info(f"JSON report generated for project ID: {project_id}")

        return send_file(
            BytesIO(json_data.encode('utf-8')),
            as_attachment=True,
            download_name=f"{secure_filename(project.name)}_data_{datetime.now().strftime('%Y%m%d')}.json",
            mimetype='application/json'
        )

    except Exception as e:
        logging.error(f"Failed to export JSON for project ID {project_id}: {str(e)}")
        return jsonify({"error": "Failed to export JSON data"}), 500


@export_blueprint.route('/export/all_projects', methods=['GET'])
def export_all_projects():
    """
    Export all projects for the user as JSON.
    """
    try:
        user_id = request.args.get("user_id")
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        all_projects = [project.to_dict() for project in user.projects]
        export_data = export_json(all_projects)
        logging.info(f"All projects data exported for user ID: {user_id}")

        return send_file(
            BytesIO(export_data.encode('utf-8')),
            as_attachment=True,
            download_name=f"{user.username}_projects_{datetime.now().strftime('%Y%m%d')}.json",
            mimetype='application/json'
        )

    except Exception as e:
        logging.error(f"Failed to export all projects for user: {str(e)}")
        return jsonify({"error": "Failed to export all projects"}), 500


@export_blueprint.route('/export/analytics/csv', methods=['POST'])
def export_analytics_csv():
    """
    Export analytics data as CSV based on user filters.
    """
    try:
        data = request.get_json()
        analytics_data = current_app.analytics_service.fetch_analytics(data)
        csv_data = export_csv(analytics_data)

        logging.info(f"Analytics CSV exported based on filters: {data}")

        return send_file(
            BytesIO(csv_data),
            as_attachment=True,
            download_name=f"analytics_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mimetype='text/csv'
        )

    except Exception as e:
        logging.error(f"Failed to export analytics CSV: {str(e)}")
        return jsonify({"error": "Failed to export analytics CSV"}), 500


@export_blueprint.route('/export/analytics/json', methods=['POST'])
def export_analytics_json():
    """
    Export analytics data as JSON based on user filters.
    """
    try:
        data = request.get_json()
        analytics_data = current_app.analytics_service.fetch_analytics(data)
        json_data = export_json(analytics_data)

        logging.info(f"Analytics JSON exported based on filters: {data}")

        return send_file(
            BytesIO(json_data.encode('utf-8')),
            as_attachment=True,
            download_name=f"analytics_data_{datetime.now().strftime('%Y%m%d')}.json",
            mimetype='application/json'
        )

    except Exception as e:
        logging.error(f"Failed to export analytics JSON: {str(e)}")
        return jsonify({"error": "Failed to export analytics JSON"}), 500

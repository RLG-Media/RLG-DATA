from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from models import Project, User, SocialMediaData
from scraping_utils import scrape_website
from api_integration import fetch_and_save_data
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define the Blueprint for project management
projects_blueprint = Blueprint('projects', __name__)

@projects_blueprint.route('/projects', methods=['GET'])
def view_projects():
    """
    Display all projects for the logged-in user.
    """
    try:
        user_id = request.args.get('user_id')  # Assuming session or token gives user info
        projects = Project.query.filter_by(user_id=user_id).all()

        return render_template('projects/view_projects.html', projects=projects)

    except Exception as e:
        logging.error(f"Error viewing projects: {e}")
        flash('An error occurred while fetching projects.', 'danger')
        return redirect(url_for('dashboard'))


@projects_blueprint.route('/projects/create', methods=['GET', 'POST'])
def create_project():
    """
    Create a new project with a list of keywords, competitors, or topics to monitor.
    """
    if request.method == 'POST':
        try:
            user_id = request.form['user_id']
            project_name = request.form['project_name']
            keywords = request.form['keywords']  # Comma-separated list of keywords
            description = request.form['description']

            # Create the new project in the database
            new_project = Project(user_id=user_id, name=project_name, description=description, keywords=keywords)
            db.session.add(new_project)
            db.session.commit()

            logging.info(f"Created new project: {project_name}")
            flash('Project created successfully!', 'success')
            return redirect(url_for('projects.view_projects'))

        except Exception as e:
            logging.error(f"Error creating project: {e}")
            flash('An error occurred while creating the project.', 'danger')

    return render_template('projects/create_project.html')


@projects_blueprint.route('/projects/edit/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    """
    Edit an existing project.
    """
    project = Project.query.get_or_404(project_id)

    if request.method == 'POST':
        try:
            project.name = request.form['project_name']
            project.keywords = request.form['keywords']
            project.description = request.form['description']

            db.session.commit()
            logging.info(f"Updated project: {project.name}")
            flash('Project updated successfully!', 'success')
            return redirect(url_for('projects.view_projects'))

        except Exception as e:
            logging.error(f"Error updating project {project_id}: {e}")
            flash('An error occurred while updating the project.', 'danger')

    return render_template('projects/edit_project.html', project=project)


@projects_blueprint.route('/projects/delete/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    """
    Delete a project by its ID.
    """
    try:
        project = Project.query.get_or_404(project_id)
        db.session.delete(project)
        db.session.commit()

        logging.info(f"Deleted project: {project.name}")
        flash('Project deleted successfully!', 'success')
        return redirect(url_for('projects.view_projects'))

    except Exception as e:
        logging.error(f"Error deleting project {project_id}: {e}")
        flash('An error occurred while deleting the project.', 'danger')
        return redirect(url_for('projects.view_projects'))


@projects_blueprint.route('/projects/details/<int:project_id>', methods=['GET'])
def project_details(project_id):
    """
    View the details of a project, including data visualizations.
    """
    try:
        project = Project.query.get_or_404(project_id)

        # Fetch related data (e.g., mentions from APIs and scraping)
        social_data = SocialMediaData.query.filter_by(project_id=project_id).all()

        return render_template('projects/project_details.html', project=project, social_data=social_data)

    except Exception as e:
        logging.error(f"Error viewing project details for {project_id}: {e}")
        flash('An error occurred while fetching project details.', 'danger')
        return redirect(url_for('projects.view_projects'))


@projects_blueprint.route('/projects/scrape/<int:project_id>', methods=['POST'])
def run_scraping_task(project_id):
    """
    Run a scraping task for the given project based on its keywords.
    """
    try:
        project = Project.query.get_or_404(project_id)

        # Trigger the web scraping for each keyword in the project
        keywords = project.keywords.split(',')
        for keyword in keywords:
            logging.info(f"Running scraping task for project: {project.name} on keyword: {keyword}")
            fetch_and_save_data(keyword)  # Calls the API and scraping functions

        flash('Scraping task completed successfully!', 'success')
        return redirect(url_for('projects.project_details', project_id=project_id))

    except Exception as e:
        logging.error(f"Error running scraping task for project {project_id}: {e}")
        flash('An error occurred while running the scraping task.', 'danger')
        return redirect(url_for('projects.view_projects'))

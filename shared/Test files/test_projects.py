import pytest
from flask import Flask
from flask.testing import FlaskClient
from projects import app, db, Project  # Import your app, db, and Project model

@pytest.fixture
def client():
    """
    Sets up a test client for the Flask app.
    Returns:
        FlaskClient: Test client for the app.
    """
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory database for tests
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Create tables
        yield client
        with app.app_context():
            db.drop_all()  # Clean up tables after tests


def test_create_project(client: FlaskClient):
    """
    Test the creation of a new project.
    """
    response = client.post('/api/projects', json={
        'name': 'Test Project',
        'description': 'This is a test project',
        'start_date': '2025-01-01',
        'end_date': '2025-12-31'
    })
    assert response.status_code == 201
    assert response.json['message'] == 'Project created successfully'
    assert 'id' in response.json


def test_get_projects(client: FlaskClient):
    """
    Test retrieving the list of projects.
    """
    # Create a project
    client.post('/api/projects', json={
        'name': 'Sample Project',
        'description': 'This is a sample project',
        'start_date': '2025-01-01',
        'end_date': '2025-12-31'
    })

    # Retrieve the projects
    response = client.get('/api/projects')
    assert response.status_code == 200
    projects = response.json
    assert len(projects) == 1
    assert projects[0]['name'] == 'Sample Project'


def test_update_project(client: FlaskClient):
    """
    Test updating an existing project.
    """
    # Create a project
    create_response = client.post('/api/projects', json={
        'name': 'Old Project Name',
        'description': 'Old description',
        'start_date': '2025-01-01',
        'end_date': '2025-12-31'
    })
    project_id = create_response.json['id']

    # Update the project
    update_response = client.put(f'/api/projects/{project_id}', json={
        'name': 'Updated Project Name',
        'description': 'Updated description',
        'start_date': '2025-02-01',
        'end_date': '2025-11-30'
    })
    assert update_response.status_code == 200
    assert update_response.json['message'] == 'Project updated successfully'

    # Verify the update
    get_response = client.get('/api/projects')
    assert get_response.status_code == 200
    projects = get_response.json
    assert projects[0]['name'] == 'Updated Project Name'
    assert projects[0]['description'] == 'Updated description'


def test_delete_project(client: FlaskClient):
    """
    Test deleting an existing project.
    """
    # Create a project
    create_response = client.post('/api/projects', json={
        'name': 'Project to Delete',
        'description': 'This project will be deleted',
        'start_date': '2025-01-01',
        'end_date': '2025-12-31'
    })
    project_id = create_response.json['id']

    # Delete the project
    delete_response = client.delete(f'/api/projects/{project_id}')
    assert delete_response.status_code == 200
    assert delete_response.json['message'] == 'Project deleted successfully'

    # Verify deletion
    get_response = client.get('/api/projects')
    assert get_response.status_code == 200
    projects = get_response.json
    assert len(projects) == 0


def test_invalid_project_creation(client: FlaskClient):
    """
    Test project creation with invalid data.
    """
    response = client.post('/api/projects', json={
        'name': '',  # Name is required
        'description': 'This project has no name',
        'start_date': '2025-01-01',
        'end_date': '2025-12-31'
    })
    assert response.status_code == 400
    assert response.json['error'] == 'Invalid data'


def test_get_nonexistent_project(client: FlaskClient):
    """
    Test retrieving a project that does not exist.
    """
    response = client.get('/api/projects/9999')  # Non-existent project ID
    assert response.status_code == 404
    assert response.json['error'] == 'Project not found'


def test_update_nonexistent_project(client: FlaskClient):
    """
    Test updating a project that does not exist.
    """
    response = client.put('/api/projects/9999', json={
        'name': 'Non-existent Project',
        'description': 'This project does not exist',
        'start_date': '2025-01-01',
        'end_date': '2025-12-31'
    })
    assert response.status_code == 404
    assert response.json['error'] == 'Project not found'


def test_delete_nonexistent_project(client: FlaskClient):
    """
    Test deleting a project that does not exist.
    """
    response = client.delete('/api/projects/9999')  # Non-existent project ID
    assert response.status_code == 404
    assert response.json['error'] == 'Project not found'

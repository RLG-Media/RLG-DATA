# test_endpoints.py

import json
import pytest
from app import create_app
from backend.models import db, User, Project, ScheduledTaskLog
from flask_jwt_extended import create_access_token

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def get_auth_header(user_id):
    """Helper function to create auth header with JWT token for testing."""
    token = create_access_token(identity=user_id)
    return {'Authorization': f'Bearer {token}'}

def test_register_user(client):
    """Test user registration endpoint."""
    response = client.post('/api/register', json={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'password123'
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'User registered successfully.'

def test_login_user(client):
    """Test user login endpoint."""
    # First, register a user
    client.post('/api/register', json={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'password123'
    })
    # Attempt to login
    response = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data

def test_project_creation(client):
    """Test creating a new project."""
    # Register and log in the user
    client.post('/api/register', json={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'password123'
    })
    login_resp = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    access_token = json.loads(login_resp.data)['access_token']

    # Create a project
    response = client.post('/api/projects', json={
        'name': 'My Project',
        'keywords': 'keyword1, keyword2'
    }, headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'Project created successfully'

def test_get_projects(client):
    """Test retrieving a list of projects."""
    # Register and log in user
    client.post('/api/register', json={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'password123'
    })
    login_resp = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    access_token = json.loads(login_resp.data)['access_token']

    # Create a project
    client.post('/api/projects', json={
        'name': 'My Project',
        'keywords': 'keyword1, keyword2'
    }, headers={'Authorization': f'Bearer {access_token}'})

    # Retrieve projects
    response = client.get('/api/projects', headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['name'] == 'My Project'

def test_scheduled_task_log(client):
    """Test retrieval of scheduled task logs."""
    with client.application.app_context():
        # Add a sample task log
        task_log = ScheduledTaskLog(task_name='scheduled_scraping_task', status='Success')
        db.session.add(task_log)
        db.session.commit()

    response = client.get('/api/scheduled_tasks')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['task_name'] == 'scheduled_scraping_task'

def test_scrape_platform_endpoint(client):
    """Test scraping endpoint for individual platforms."""
    # Register and log in user
    client.post('/api/register', json={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'password123'
    })
    login_resp = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    access_token = json.loads(login_resp.data)['access_token']

    # Test scraping for a platform
    response = client.post('/api/scrape', json={
        'platform': 'OnlyFans'
    }, headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Scraping started successfully for OnlyFans'

def test_notification_endpoint(client):
    """Test notification retrieval endpoint."""
    # Register and log in user
    client.post('/api/register', json={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'password123'
    })
    login_resp = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    access_token = json.loads(login_resp.data)['access_token']

    # Retrieve notifications
    response = client.get('/api/notifications', headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)  # Ensure we get a list of notifications


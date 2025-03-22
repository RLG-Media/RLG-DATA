import unittest
from app import create_app, db
from models import User, Project, SocialMediaData
from api_integration import fetch_twitter_data
from cache import cache
from unittest.mock import patch
from flask import jsonify

class TestRLGData(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Set up the test class by initializing the Flask app and database.
        """
        cls.app = create_app('testing')  # Use a testing config
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

        # Create all database tables
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        """
        Tear down the test class by dropping the database tables and popping the context.
        """
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        """
        Set up test data and clean up the cache before each test.
        """
        cache.flushall()  # Clear Redis cache before each test

    def tearDown(self):
        """
        Clean up after each test.
        """
        db.session.remove()

    ### UNIT TESTS ###

    def test_user_creation(self):
        """
        Test creating a new user in the database.
        """
        user = User(username='test_user', password_hash='hashed_password')
        db.session.add(user)
        db.session.commit()

        fetched_user = User.query.filter_by(username='test_user').first()
        self.assertIsNotNone(fetched_user)
        self.assertEqual(fetched_user.username, 'test_user')

    def test_project_creation(self):
        """
        Test creating a new project for a user.
        """
        user = User(username='project_user', password_hash='hashed_password')
        db.session.add(user)
        db.session.commit()

        project = Project(name='Test Project', keywords='keyword1,keyword2', user_id=user.id)
        db.session.add(project)
        db.session.commit()

        fetched_project = Project.query.filter_by(name='Test Project').first()
        self.assertIsNotNone(fetched_project)
        self.assertEqual(fetched_project.keywords, 'keyword1,keyword2')

    ### INTEGRATION TESTS ###

    @patch('api_integration.fetch_twitter_data')
    def test_realtime_data_fetch(self, mock_fetch_twitter_data):
        """
        Test the integration of real-time data fetching for a project.
        """
        # Mock Twitter API data
        mock_fetch_twitter_data.return_value = [{'text': 'Test tweet'}]

        # Create a project
        user = User(username='realtime_user', password_hash='hashed_password')
        db.session.add(user)
        db.session.commit()

        project = Project(name='Realtime Project', keywords='keyword1', user_id=user.id)
        db.session.add(project)
        db.session.commit()

        # Fetch real-time data
        from realtime_data import fetch_realtime_data
        fetch_realtime_data(project.id)

        social_data = SocialMediaData.query.filter_by(project_id=project.id).all()
        self.assertEqual(len(social_data), 1)
        self.assertEqual(social_data[0].content, 'Test tweet')

    ### API ENDPOINT TESTS ###

    def test_api_create_project(self):
        """
        Test the API endpoint for creating a new project.
        """
        user = User(username='api_user', password_hash='hashed_password')
        db.session.add(user)
        db.session.commit()

        response = self.client.post('/api/projects', json={
            'name': 'API Project',
            'keywords': 'api,project',
            'description': 'A test project'
        }, headers={'Authorization': 'Bearer <valid_token>'})  # Assume a valid token for testing

        self.assertEqual(response.status_code, 201)
        self.assertIn('API Project', response.get_json()['project']['name'])

    def test_api_get_projects(self):
        """
        Test the API endpoint for retrieving all projects for a user.
        """
        user = User(username='api_user_2', password_hash='hashed_password')
        db.session.add(user)
        db.session.commit()

        project = Project(name='Existing Project', keywords='existing', user_id=user.id)
        db.session.add(project)
        db.session.commit()

        response = self.client.get('/api/projects', headers={'Authorization': 'Bearer <valid_token>'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Existing Project', response.get_json()['projects'][0]['name'])

    ### DATABASE TESTS ###

    def test_project_deletion(self):
        """
        Test deleting a project from the database.
        """
        user = User(username='delete_user', password_hash='hashed_password')
        db.session.add(user)
        db.session.commit()

        project = Project(name='Delete Project', keywords='delete', user_id=user.id)
        db.session.add(project)
        db.session.commit()

        # Verify the project exists
        project_id = project.id
        self.assertIsNotNone(Project.query.get(project_id))

        # Delete the project
        db.session.delete(project)
        db.session.commit()

        # Verify the project was deleted
        self.assertIsNone(Project.query.get(project_id))

    ### CACHING TESTS ###

    def test_cache_project_data(self):
        """
        Test caching project data to improve performance.
        """
        user = User(username='cache_user', password_hash='hashed_password')
        db.session.add(user)
        db.session.commit()

        project = Project(name='Cache Project', keywords='cache', user_id=user.id)
        db.session.add(project)
        db.session.commit()

        from performance_optimization import get_cached_project_data
        cached_data = get_cached_project_data(project.id)

        # Verify the data is cached and can be retrieved
        self.assertIsNotNone(cached_data)

    @patch('performance_optimization.invalidate_cache')
    def test_invalidate_cache(self, mock_invalidate_cache):
        """
        Test invalidating the cache after a project update.
        """
        user = User(username='invalidate_user', password_hash='hashed_password')
        db.session.add(user)
        db.session.commit()

        project = Project(name='Invalidate Project', keywords='invalidate', user_id=user.id)
        db.session.add(project)
        db.session.commit()

        # Invalidate cache after updating the project
        mock_invalidate_cache.return_value = True
        from performance_optimization import invalidate_project_cache
        invalidate_project_cache(project.id)

        mock_invalidate_cache.assert_called_once()


from flask import Blueprint
from flask_restx import Api, Resource, fields

# Create a blueprint for API documentation with a dedicated URL prefix.
api_blueprint = Blueprint('api_doc', __name__, url_prefix='/api-docs')

# Initialize the Flask-RESTX API with versioning and title details.
api = Api(
    api_blueprint,
    version='1.0',
    title='RLG Data & RLG Fans API Documentation',
    description='This documentation provides details for the RLG Data and RLG Fans RESTful API. '
                'It covers endpoints for user management, integrations, reports, and analytics. '
                'The API adheres to Semantic Versioning and is designed to be robust, scalable, '
                'and regionally accurate.',
    doc='/'  # Swagger UI available at /api-docs/
)

# Example namespace for user-related operations.
ns_users = api.namespace('users', description='Operations related to user management')

# Define an example model for user data.
user_model = api.model('User', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a user'),
    'username': fields.String(required=True, description='The username'),
    'email': fields.String(required=True, description='The user email address')
})

@ns_users.route('/')
class UserList(Resource):
    @ns_users.doc('list_users')
    @ns_users.marshal_list_with(user_model)
    def get(self):
        """
        List all users.
        """
        # Replace with actual logic to fetch user data.
        return [
            {'id': 1, 'username': 'john_doe', 'email': 'john@example.com'},
            {'id': 2, 'username': 'jane_doe', 'email': 'jane@example.com'}
        ]

    @ns_users.doc('create_user')
    @ns_users.expect(user_model, validate=True)
    @ns_users.response(201, 'User created successfully.')
    def post(self):
        """
        Create a new user.
        """
        # Replace with actual logic to create a user.
        data = api.payload
        data['id'] = 3  # Simulate an auto-generated ID.
        return data, 201

# Example namespace for integration-related operations.
ns_integrations = api.namespace('integrations', description='Operations for managing integrations')

integration_model = api.model('Integration', {
    'name': fields.String(required=True, description='Name of the integration'),
    'api_key': fields.String(required=True, description='API key for the integration'),
    'config': fields.Raw(description='Additional configuration for the integration')
})

@ns_integrations.route('/')
class IntegrationList(Resource):
    @ns_integrations.doc('list_integrations')
    @ns_integrations.marshal_list_with(integration_model)
    def get(self):
        """
        List all integrations.
        """
        # Replace with actual logic to fetch integration data.
        return [
            {'name': 'Slack', 'api_key': 'xxx', 'config': {'channel': '#general'}},
            {'name': 'Google Analytics', 'api_key': 'yyy', 'config': {}}
        ]

# Example namespace for reports and analytics.
ns_reports = api.namespace('reports', description='Operations related to report generation and analytics')

report_model = api.model('Report', {
    'report_id': fields.String(required=True, description='Unique report identifier'),
    'created_at': fields.DateTime(description='Timestamp of report creation'),
    'data': fields.Raw(description='Report data')
})

@ns_reports.route('/')
class ReportList(Resource):
    @ns_reports.doc('list_reports')
    @ns_reports.marshal_list_with(report_model)
    def get(self):
        """
        List all reports.
        """
        # Replace with actual logic to fetch reports.
        return [
            {'report_id': 'rpt-001', 'created_at': datetime.utcnow().isoformat(), 'data': {'key': 'value'}},
            {'report_id': 'rpt-002', 'created_at': datetime.utcnow().isoformat(), 'data': {'key': 'value'}}
        ]

# Helper function to integrate the API documentation blueprint into your Flask app.
def init_api_documentation(app):
    """
    Registers the API documentation blueprint with the provided Flask app.
    
    Args:
        app: The Flask application instance.
    """
    app.register_blueprint(api_blueprint)

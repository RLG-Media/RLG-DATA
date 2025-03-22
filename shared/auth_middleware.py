# auth_middleware.py

from functools import wraps
from flask import request, jsonify, current_app, g
from jwt import decode, exceptions
from app.models.user import User

def token_required(f):
    """Decorator to require a valid token for accessing a route."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check if token is present in request headers
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Decode the token and get the user information
            decoded_data = decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=["HS256"]
            )
            user_id = decoded_data['user_id']

            # Fetch user from database and assign to the global context (g)
            g.current_user = User.query.get(user_id)
            if g.current_user is None:
                return jsonify({'message': 'User not found.'}), 404

        except exceptions.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except exceptions.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401

        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """Decorator to restrict route access to admin users only."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not getattr(g, 'current_user', None):
            return jsonify({'message': 'Authentication required!'}), 401

        # Ensure the current user has admin privileges
        if not g.current_user.is_admin:
            return jsonify({'message': 'Admin access required!'}), 403

        return f(*args, **kwargs)
    return decorated

def platform_specific_access(platform_name):
    """Decorator to ensure users have access to specific platforms."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not getattr(g, 'current_user', None):
            return jsonify({'message': 'Authentication required!'}), 401

        # Ensure the user has access to the specific platform
        allowed_platforms = g.current_user.get_allowed_platforms()
        if platform_name not in allowed_platforms:
            return jsonify({'message': f'Access to {platform_name} is not allowed for your account.'}), 403

        return f(*args, **kwargs)
    return decorated

# Optional: Rate limiting by role and platform
def rate_limit_by_role_and_platform(f):
    """Decorator to apply rate limits based on user roles and platforms."""
    @wraps(f)
    def decorated(*args, **kwargs):
        user_role = getattr(g.current_user, 'role', 'guest')  # Default to 'guest'
        platform = request.args.get('platform', 'default')  # Get platform from request args
        role_limits = {
            'admin': current_app.config['RATE_LIMIT_ADMIN'],
            'creator': current_app.config['RATE_LIMIT_CREATOR'],
            'brand': current_app.config['RATE_LIMIT_BRAND'],
            'guest': current_app.config['RATE_LIMIT_GUEST']
        }
        platform_limits = current_app.config['PLATFORM_RATE_LIMITS'].get(platform, {})
        limit = platform_limits.get(user_role, role_limits.get(user_role, current_app.config['RATE_LIMIT_DEFAULT']))

        # Implement rate limiting logic here (e.g., using Redis or in-memory counters)

        return f(*args, **kwargs)
    return decorated

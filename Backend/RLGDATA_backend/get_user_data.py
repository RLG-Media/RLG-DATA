import requests
from flask import current_app
from models import User
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def get_user_data(user_id: int) -> dict:
    """
    Retrieve detailed user data from the database, and fetch additional data from external APIs if needed.
    :param user_id: The ID of the user to fetch data for.
    :return: A dictionary containing user data.
    """
    try:
        # Query user data from the database
        user = User.query.get(user_id)

        if not user:
            logging.error(f"User with ID {user_id} not found.")
            return {}

        # Build the initial user data dictionary
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'subscription_status': user.subscription_status,
            'social_profiles': {}  # Store social profile data here
        }

        # Fetch additional data from external services (e.g., social media platforms)
        social_services = {
            'twitter': fetch_twitter_data,
            'facebook': fetch_facebook_data,
            'instagram': fetch_instagram_data,
            'linkedin': fetch_linkedin_data
        }

        for service, fetch_function in social_services.items():
            try:
                profile_data = fetch_function(user)
                if profile_data:
                    user_data['social_profiles'][service] = profile_data
            except Exception as e:
                logging.error(f"Error fetching data from {service}: {e}")

        logging.info(f"User data successfully fetched for user: {user.username}")
        return user_data

    except Exception as e:
        logging.error(f"An error occurred while fetching user data for user ID {user_id}: {e}")
        return {}

# Helper functions to fetch data from external services
def fetch_twitter_data(user: User) -> dict:
    """
    Fetch Twitter profile data for the user (example function).
    This would require the appropriate tokens and API access.
    :param user: The user object.
    :return: A dictionary containing Twitter profile data.
    """
    try:
        twitter_url = f"https://api.twitter.com/2/users/by/username/{user.username}"
        headers = {
            "Authorization": f"Bearer {current_app.config['TWITTER_BEARER_TOKEN']}"
        }
        response = requests.get(twitter_url, headers=headers)
        response.raise_for_status()

        twitter_data = response.json()
        return {
            'followers_count': twitter_data.get('followers_count', 0),
            'tweets': twitter_data.get('tweets', []),
            'profile_url': f"https://twitter.com/{user.username}"
        }
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch Twitter data for user {user.username}: {e}")
        return {}

def fetch_facebook_data(user: User) -> dict:
    """
    Fetch Facebook profile data for the user (example function).
    :param user: The user object.
    :return: A dictionary containing Facebook profile data.
    """
    try:
        facebook_url = f"https://graph.facebook.com/v12.0/{user.facebook_id}?fields=id,name,followers_count"
        headers = {
            "Authorization": f"Bearer {current_app.config['FACEBOOK_ACCESS_TOKEN']}"
        }
        response = requests.get(facebook_url, headers=headers)
        response.raise_for_status()

        facebook_data = response.json()
        return {
            'followers_count': facebook_data.get('followers_count', 0),
            'profile_url': f"https://www.facebook.com/{user.facebook_id}"
        }
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch Facebook data for user {user.username}: {e}")
        return {}

def fetch_instagram_data(user: User) -> dict:
    """
    Fetch Instagram profile data for the user (example function).
    :param user: The user object.
    :return: A dictionary containing Instagram profile data.
    """
    try:
        instagram_url = f"https://graph.instagram.com/{user.instagram_id}?fields=id,username,followers_count"
        headers = {
            "Authorization": f"Bearer {current_app.config['INSTAGRAM_ACCESS_TOKEN']}"
        }
        response = requests.get(instagram_url, headers=headers)
        response.raise_for_status()

        instagram_data = response.json()
        return {
            'followers_count': instagram_data.get('followers_count', 0),
            'profile_url': f"https://www.instagram.com/{user.username}"
        }
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch Instagram data for user {user.username}: {e}")
        return {}

def fetch_linkedin_data(user: User) -> dict:
    """
    Fetch LinkedIn profile data for the user (example function).
    :param user: The user object.
    :return: A dictionary containing LinkedIn profile data.
    """
    try:
        linkedin_url = f"https://api.linkedin.com/v2/me"
        headers = {
            "Authorization": f"Bearer {current_app.config['LINKEDIN_ACCESS_TOKEN']}"
        }
        response = requests.get(linkedin_url, headers=headers)
        response.raise_for_status()

        linkedin_data = response.json()
        return {
            'connections_count': linkedin_data.get('numConnections', 0),
            'profile_url': linkedin_data.get('publicProfileUrl', '')
        }
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch LinkedIn data for user {user.username}: {e}")
        return {}


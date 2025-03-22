import logging
from typing import List, Dict, Any
from flask import current_app
from shared.utils import log_error, log_info  # Shared logging utilities

# Configure logging if not already configured by the app
logging.basicConfig(level=logging.INFO)

def get_available_tools(user: Any) -> List[Dict[str, Any]]:
    """
    Retrieve the list of tools available to a specific user based on their subscription level.
    The available tools include internal features, integrations, and external APIs.

    Args:
        user: The user object to check subscription level and permissions. It is expected that:
              - user.subscription_status is a string (e.g., 'active', 'inactive').
              - user.username is available for logging.
              - user.features_enabled is a list of enabled integrations (e.g., ['twitter_integration']).

    Returns:
        List[Dict[str, Any]]: A list of dictionaries representing the available tools for the user.
                              Each tool dictionary includes 'name', 'description', 'link', and 'enabled' status.
    """
    try:
        # Define standard tools available to all users or only if subscription is active.
        tools = [
            {
                'name': 'Sentiment Analysis',
                'description': 'Analyze social media sentiment in real-time.',
                'link': '/sentiment-analysis',
                'enabled': user.subscription_status == 'active'
            },
            {
                'name': 'Brand Health Monitoring',
                'description': 'Track brand mentions and online presence.',
                'link': '/brand-health',
                'enabled': user.subscription_status == 'active'
            },
            {
                'name': 'Content Planning',
                'description': 'Generate content ideas based on trending topics.',
                'link': '/content-planning',
                'enabled': user.subscription_status == 'active'
            },
            {
                'name': 'Influencer Matching',
                'description': 'Find and match with relevant influencers for your brand.',
                'link': '/influencer-matching',
                'enabled': user.subscription_status == 'active'
            },
            {
                'name': 'Crisis Management',
                'description': 'Manage social media crises and analyze threats.',
                'link': '/crisis-management',
                'enabled': user.subscription_status == 'active'
            },
            {
                'name': 'Event Monitoring',
                'description': 'Monitor events and hashtags across social media.',
                'link': '/event-monitoring',
                'enabled': user.subscription_status == 'active'
            },
            {
                'name': 'Social Media Scheduling',
                'description': 'Schedule posts across social platforms.',
                'link': '/content-scheduling',
                'enabled': user.subscription_status == 'active'
            },
            {
                'name': 'Real-Time Mentions',
                'description': 'Monitor mentions of your brand in real-time.',
                'link': '/real-time-mentions',
                'enabled': user.subscription_status == 'active'
            },
            {
                'name': 'PDF Reports',
                'description': 'Generate detailed PDF reports with graphs and analysis.',
                'link': '/reports',
                'enabled': True  # This feature is enabled for all users
            },
        ]

        # Retrieve custom tools (e.g., third-party integrations) based on the user's profile.
        user_specific_tools = fetch_custom_tools(user)
        tools.extend(user_specific_tools)

        log_info(f"Available tools for user {user.username}: {len(tools)}")
        return tools

    except Exception as e:
        log_error(f"Error retrieving available tools for user {user.username}: {e}")
        return []


def fetch_custom_tools(user: Any) -> List[Dict[str, Any]]:
    """
    Fetch custom tools or third-party integrations that are available based on the user's profile.
    For example, integrations with Twitter or YouTube analytics.

    Args:
        user: The user object for which to fetch custom tools.
              Expected to have an attribute 'features_enabled', a list of strings.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries representing custom tools.
    """
    try:
        custom_tools: List[Dict[str, Any]] = []

        # Example: Twitter integration
        if 'twitter_integration' in user.features_enabled:
            custom_tools.append({
                'name': 'Twitter Analytics',
                'description': 'Analyze Twitter activity and follower growth.',
                'link': '/twitter-analytics',
                'enabled': True
            })

        # Example: YouTube integration
        if 'youtube_integration' in user.features_enabled:
            custom_tools.append({
                'name': 'YouTube Channel Insights',
                'description': 'Monitor YouTube channel performance and video statistics.',
                'link': '/youtube-insights',
                'enabled': True
            })

        log_info(f"Custom tools fetched for user {user.username}: {len(custom_tools)}")
        return custom_tools

    except Exception as e:
        log_error(f"Error fetching custom tools for user {user.username}: {e}")
        return []

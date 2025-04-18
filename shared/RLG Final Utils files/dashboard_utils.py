# dashboard_utils.py - Utilities for Dashboard Management in RLG Data and RLG Fans

from datetime import datetime, timedelta
from backend.database import fetch_data, save_data, update_data
from shared.logging_config import logger
from backend.analytics_engine import calculate_metrics
from backend.cache_management import get_cached_data, set_cached_data
from backend.error_handlers import DashboardError

# Constants for Cache Keys
CACHE_EXPIRY = 3600  # Cache expiry in seconds (1 hour)
DATA_OVERVIEW_CACHE_KEY = "dashboard_data_overview"
USER_ACTIVITY_CACHE_KEY = "dashboard_user_activity"
TREND_ANALYSIS_CACHE_KEY = "dashboard_trend_analysis"

def fetch_dashboard_overview(user_id, platform):
    """
    Fetches the data overview for the dashboard.

    Args:
        user_id (int): The ID of the user.
        platform (str): The platform name (e.g., RLG Data, RLG Fans).

    Returns:
        dict: An overview of the dashboard data.
    """
    cache_key = f"{DATA_OVERVIEW_CACHE_KEY}_{user_id}_{platform}"
    cached_data = get_cached_data(cache_key)

    if cached_data:
        logger.info(f"Fetched dashboard overview from cache for user {user_id} on {platform}.")
        return cached_data

    try:
        # Fetch data overview from the database
        data = fetch_data("dashboard_overview", {"user_id": user_id, "platform": platform})
        if not data:
            logger.warning(f"No dashboard overview data found for user {user_id} on {platform}.")
            return {}

        # Perform additional calculations (if required)
        metrics = calculate_metrics(data)

        # Cache the result
        set_cached_data(cache_key, metrics, CACHE_EXPIRY)
        logger.info(f"Dashboard overview data cached for user {user_id} on {platform}.")
        return metrics
    except Exception as e:
        logger.error(f"Error fetching dashboard overview for user {user_id} on {platform}: {e}")
        raise DashboardError(f"Failed to fetch dashboard overview: {e}")


def fetch_user_activity(user_id, days=7):
    """
    Fetches user activity data for the dashboard.

    Args:
        user_id (int): The ID of the user.
        days (int): Number of days to include in the activity log.

    Returns:
        list: A list of user activity data.
    """
    cache_key = f"{USER_ACTIVITY_CACHE_KEY}_{user_id}_{days}"
    cached_data = get_cached_data(cache_key)

    if cached_data:
        logger.info(f"Fetched user activity from cache for user {user_id}.")
        return cached_data

    try:
        start_date = datetime.now() - timedelta(days=days)
        data = fetch_data("user_activity", {"user_id": user_id, "start_date": start_date})
        if not data:
            logger.warning(f"No user activity data found for user {user_id}.")
            return []

        # Cache the result
        set_cached_data(cache_key, data, CACHE_EXPIRY)
        logger.info(f"User activity data cached for user {user_id}.")
        return data
    except Exception as e:
        logger.error(f"Error fetching user activity for user {user_id}: {e}")
        raise DashboardError(f"Failed to fetch user activity: {e}")


def fetch_trend_analysis(platform, metric, days=30):
    """
    Fetches trend analysis data for the dashboard.

    Args:
        platform (str): The platform name (e.g., RLG Data, RLG Fans).
        metric (str): The metric to analyze (e.g., "engagement", "growth").
        days (int): Number of days to include in the trend analysis.

    Returns:
        dict: A dictionary containing trend analysis data.
    """
    cache_key = f"{TREND_ANALYSIS_CACHE_KEY}_{platform}_{metric}_{days}"
    cached_data = get_cached_data(cache_key)

    if cached_data:
        logger.info(f"Fetched trend analysis from cache for platform {platform} (metric: {metric}).")
        return cached_data

    try:
        start_date = datetime.now() - timedelta(days=days)
        data = fetch_data("trend_analysis", {"platform": platform, "metric": metric, "start_date": start_date})
        if not data:
            logger.warning(f"No trend analysis data found for platform {platform} (metric: {metric}).")
            return {}

        # Perform any additional analytics on the data
        trends = calculate_metrics(data, metric=metric)

        # Cache the result
        set_cached_data(cache_key, trends, CACHE_EXPIRY)
        logger.info(f"Trend analysis data cached for platform {platform} (metric: {metric}).")
        return trends
    except Exception as e:
        logger.error(f"Error fetching trend analysis for platform {platform} (metric: {metric}): {e}")
        raise DashboardError(f"Failed to fetch trend analysis: {e}")


def update_dashboard_settings(user_id, settings):
    """
    Updates dashboard settings for the user.

    Args:
        user_id (int): The ID of the user.
        settings (dict): The new dashboard settings.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    try:
        updated = update_data("dashboard_settings", {"user_id": user_id}, settings)
        if updated:
            logger.info(f"Dashboard settings updated for user {user_id}.")
            return True
        else:
            logger.warning(f"Failed to update dashboard settings for user {user_id}.")
            return False
    except Exception as e:
        logger.error(f"Error updating dashboard settings for user {user_id}: {e}")
        raise DashboardError(f"Failed to update dashboard settings: {e}")


def refresh_dashboard_cache(user_id, platform):
    """
    Refreshes the cache for a user's dashboard.

    Args:
        user_id (int): The ID of the user.
        platform (str): The platform name (e.g., RLG Data, RLG Fans).

    Returns:
        bool: True if the cache refresh was successful, False otherwise.
    """
    try:
        # Clear existing cache
        cache_keys = [
            f"{DATA_OVERVIEW_CACHE_KEY}_{user_id}_{platform}",
            f"{USER_ACTIVITY_CACHE_KEY}_{user_id}",
            f"{TREND_ANALYSIS_CACHE_KEY}_{platform}_engagement_30",  # Example metric and period
        ]
        for key in cache_keys:
            set_cached_data(key, None, 0)  # Clear cache

        # Repopulate cache
        fetch_dashboard_overview(user_id, platform)
        fetch_user_activity(user_id)
        fetch_trend_analysis(platform, "engagement")

        logger.info(f"Dashboard cache refreshed for user {user_id} on {platform}.")
        return True
    except Exception as e:
        logger.error(f"Error refreshing dashboard cache for user {user_id} on {platform}: {e}")
        raise DashboardError(f"Failed to refresh dashboard cache: {e}")

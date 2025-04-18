import re
from urllib.parse import urlparse
from datetime import datetime

def is_valid_email(email):
    """
    Validate an email address format.
    """
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def is_valid_url(url):
    """
    Check if the URL has a valid format and uses HTTP or HTTPS.
    """
    parsed_url = urlparse(url)
    return parsed_url.scheme in ('http', 'https') and bool(parsed_url.netloc)

def is_valid_api_key(api_key):
    """
    Validate API keys to ensure they are alphanumeric and of expected length.
    Modify length according to each platform's standard if necessary.
    """
    return bool(api_key) and api_key.isalnum() and 20 <= len(api_key) <= 60

def is_positive_integer(value):
    """
    Ensure the value is a positive integer.
    """
    return isinstance(value, int) and value > 0

def is_valid_platform(platform):
    """
    Validate platform name based on supported platforms for RLG Data and RLG Fans.
    """
    supported_platforms = {
        'RLG Data': [
            'Twitter', 'Instagram', 'Facebook', 'YouTube', 'TikTok',
            'LinkedIn', 'Pinterest', 'Snapchat'
        ],
        'RLG Fans': [
            'OnlyFans', 'Fansly', 'Fanvue', 'Patreon', 'JustForFans',
            'Fapello', 'Alua', 'FeetFinder', 'Sheer', 'YouFanly',
            'Pornhub', 'Snapchat', 'TikTok', 'YouTube', 'Facebook'
        ]
    }
    for platforms in supported_platforms.values():
        if platform in platforms:
            return True
    return False

def is_valid_date_format(date_text):
    """
    Validate if the date is in the format YYYY-MM-DD.
    """
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_content(content, min_length=10, max_length=500):
    """
    Check if content text meets length requirements.
    """
    return min_length <= len(content) <= max_length

def is_valid_sentiment_score(score):
    """
    Ensure sentiment score is between 0 and 100 (representing a percentage).
    """
    return isinstance(score, (int, float)) and 0 <= score <= 100

def is_valid_tag(tag):
    """
    Validate tags for trending content or mentions, ensuring they're alphanumeric and within length limits.
    """
    tag_regex = r'^[a-zA-Z0-9_-]+$'
    return re.match(tag_regex, tag) and 1 <= len(tag) <= 50

def validate_mention_data(mention_data):
    """
    Validate mention data to ensure it has valid format for platform, mentions count.
    """
    required_keys = {'platform', 'mentions'}
    if not isinstance(mention_data, dict) or not required_keys.issubset(mention_data.keys()):
        return False
    return (
        is_valid_platform(mention_data.get('platform')) and
        is_positive_integer(mention_data.get('mentions'))
    )

def validate_trending_content_data(content_data):
    """
    Validate trending content data to ensure it contains required keys and formats.
    """
    required_keys = {'content', 'engagement'}
    if not isinstance(content_data, dict) or not required_keys.issubset(content_data.keys()):
        return False
    return (
        validate_content(content_data.get('content')) and
        is_positive_integer(content_data.get('engagement'))
    )

def validate_follower_data(follower_data):
    """
    Validate follower data for platforms under RLG Fans to ensure counts are positive integers.
    """
    required_keys = {'platform', 'followers'}
    if not isinstance(follower_data, dict) or not required_keys.issubset(follower_data.keys()):
        return False
    return (
        is_valid_platform(follower_data.get('platform')) and
        is_positive_integer(follower_data.get('followers'))
    )

def validate_engagement_data(engagement_data):
    """
    Validate engagement data, ensuring platform and engagement rates are positive.
    """
    required_keys = {'platform', 'engagement_rate'}
    if not isinstance(engagement_data, dict) or not required_keys.issubset(engagement_data.keys()):
        return False
    return (
        is_valid_platform(engagement_data.get('platform')) and
        0 <= engagement_data.get('engagement_rate') <= 100
    )

def validate_api_key(api_key, platform):
    """
    Specific validation for API keys per platform, can add platform-specific rules.
    """
    if not is_valid_api_key(api_key):
        return False
    # Example: Add additional platform-specific validation here if needed
    return True

def validate_real_time_update(data):
    """
    Ensure real-time updates contain required fields and valid formats.
    """
    required_keys = {'platform', 'data_type', 'value'}
    if not isinstance(data, dict) or not required_keys.issubset(data.keys()):
        return False
    return (
        is_valid_platform(data.get('platform')) and
        isinstance(data.get('data_type'), str) and
        isinstance(data.get('value'), (int, float))
    )

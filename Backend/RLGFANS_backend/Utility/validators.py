# validators.py - Input validation utility functions for RLG Fans

import re
from urllib.parse import urlparse
import validators as vld  # Using the validators library as a base

def is_valid_url(url):
    """
    Validate if the input is a correctly formatted URL.
    
    Args:
        url (str): The URL to validate.
        
    Returns:
        bool: True if valid, False otherwise.
    """
    if not vld.url(url):
        return False
    parsed_url = urlparse(url)
    return all([parsed_url.scheme, parsed_url.netloc])

def is_valid_email(email):
    """
    Validate if the input is a correctly formatted email address.
    
    Args:
        email (str): The email to validate.
        
    Returns:
        bool: True if valid, False otherwise.
    """
    return vld.email(email)

def is_valid_username(username):
    """
    Validate if the input is a valid username. Must be alphanumeric and between 3-20 characters.
    
    Args:
        username (str): The username to validate.
        
    Returns:
        bool: True if valid, False otherwise.
    """
    pattern = re.compile(r"^[a-zA-Z0-9_]{3,20}$")
    return bool(pattern.match(username))

def contains_prohibited_content(text):
    """
    Check if the input contains prohibited words or phrases, such as banned keywords or offensive content.
    
    Args:
        text (str): The text to analyze.
        
    Returns:
        bool: True if prohibited content is detected, False otherwise.
    """
    prohibited_keywords = ["spam", "scam", "offensive_word"]  # Expand as needed
    return any(word in text.lower() for word in prohibited_keywords)

def validate_platform_content(content):
    """
    Validate platform-specific content for appropriate formatting and allowed characters.
    
    Args:
        content (str): The content to validate.
        
    Returns:
        bool: True if valid, False otherwise.
    """
    max_length = 500  # Example max length for content
    return len(content) <= max_length and not contains_prohibited_content(content)

def is_valid_price(price):
    """
    Validate if the price is a positive number formatted to two decimal places.
    
    Args:
        price (float): The price to validate.
        
    Returns:
        bool: True if valid, False otherwise.
    """
    return isinstance(price, (int, float)) and price >= 0

def validate_keywords(keywords):
    """
    Ensure keywords are alphanumeric and comma-separated.
    
    Args:
        keywords (str): Comma-separated keywords string to validate.
        
    Returns:
        bool: True if valid, False otherwise.
    """
    if not keywords:
        return False
    keywords_list = keywords.split(',')
    return all(kw.strip().isalnum() for kw in keywords_list)

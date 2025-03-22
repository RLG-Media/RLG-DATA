# trend_analysis.py - Identifies and analyzes content trends for RLG Fans

from collections import Counter
import re
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(filename='trend_analysis.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')

def extract_hashtags(text):
    """
    Extract hashtags from a given text.
    
    Args:
        text (str): Text from which to extract hashtags.
        
    Returns:
        list: List of hashtags in the text.
    """
    hashtags = re.findall(r"#(\w+)", text)
    logging.debug(f"Extracted hashtags: {hashtags}")
    return hashtags


def analyze_trends(texts, top_n=10):
    """
    Analyze trends by identifying the most common hashtags and keywords.
    
    Args:
        texts (list): List of texts to analyze.
        top_n (int): Number of top trends to return (default: 10).
        
    Returns:
        dict: Dictionary with top hashtags and keywords.
    """
    try:
        all_hashtags = []
        all_words = []
        
        for text in texts:
            all_hashtags.extend(extract_hashtags(text))
            all_words.extend(re.findall(r'\b\w+\b', text.lower()))
        
        # Count frequency of hashtags and words
        top_hashtags = Counter(all_hashtags).most_common(top_n)
        top_keywords = Counter(all_words).most_common(top_n)
        
        trends = {
            "top_hashtags": top_hashtags,
            "top_keywords": top_keywords
        }
        
        logging.info(f"Trend analysis completed: {trends}")
        return trends
    except Exception as e:
        logging.error(f"Trend analysis failed: {str(e)}")
        return {"top_hashtags": [], "top_keywords": []}


def track_trending_content(texts, frequency_threshold=5):
    """
    Identify recurring trends in content based on a frequency threshold.
    
    Args:
        texts (list): List of texts to analyze for recurring trends.
        frequency_threshold (int): Minimum frequency for a trend to be considered significant.
        
    Returns:
        list: List of significant trends.
    """
    try:
        all_words = [word for text in texts for word in re.findall(r'\b\w+\b', text.lower())]
        word_counts = Counter(all_words)
        
        significant_trends = [word for word, count in word_counts.items() if count >= frequency_threshold]
        
        logging.info(f"Significant trends identified: {significant_trends}")
        return significant_trends
    except Exception as e:
        logging.error(f"Error tracking trending content: {str(e)}")
        return []


def log_trends(trends, platform):
    """
    Log identified trends with a timestamp for future reference.
    
    Args:
        trends (dict): Dictionary of trends (e.g., hashtags and keywords).
        platform (str): Platform from which the trends are identified.
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"Trends for {platform} at {timestamp}: {trends}")
    except Exception as e:
        logging.error(f"Error logging trends for {platform}: {str(e)}")

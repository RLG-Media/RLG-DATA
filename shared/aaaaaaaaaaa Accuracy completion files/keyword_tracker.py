"""
keyword_tracker.py

This module provides functions to track and analyze keyword occurrences in text data,
specifically designed for both RLG Data (media articles) and RLG Fans (social posts).
It is built to be robust, scalable, and region-aware, and is intended to be integrated
into automated pipelines for real-time or batch analysis.

Dependencies:
    - logging (standard library)
    - re (for regular expression-based search)
    - collections.Counter (for counting occurrences)
    - pandas (optional; used here for bulk analysis convenience)
    
For more advanced NLP capabilities, consider integrating spaCy or NLTK.
"""

import re
import logging
from collections import Counter
from typing import List, Dict, Optional
import pandas as pd

# Configure logging
logger = logging.getLogger("KeywordTracker")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

def track_keywords_in_text(text: str, keywords: List[str], ignore_case: bool = True) -> Dict[str, int]:
    """
    Tracks keyword occurrences in a single block of text.
    
    Parameters:
        text (str): The text to search.
        keywords (List[str]): A list of keywords to track.
        ignore_case (bool): Whether to ignore case during matching.
    
    Returns:
        Dict[str, int]: A dictionary mapping each keyword to its occurrence count.
    """
    if ignore_case:
        text = text.lower()
        keywords = [kw.lower() for kw in keywords]
    
    counts = Counter()
    for kw in keywords:
        # Use word boundaries to match whole words.
        pattern = r'\b' + re.escape(kw) + r'\b'
        matches = re.findall(pattern, text)
        count = len(matches)
        counts[kw] = count
        logger.debug(f"Keyword '{kw}' found {count} times in text.")
    
    return dict(counts)

def track_keywords_in_articles(articles: List[dict], keywords: List[str], text_field: str = "title") -> Dict[str, int]:
    """
    Analyzes a list of articles to track keyword occurrences.
    
    Parameters:
        articles (List[dict]): List of articles, each being a dictionary.
                               Each article must contain a text field (default "title") where keywords are searched.
        keywords (List[str]): List of keywords to track.
        text_field (str): The key in each article dict that holds the text to search.
    
    Returns:
        Dict[str, int]: Aggregated keyword counts across all articles.
    """
    aggregated_counts = Counter()
    for article in articles:
        text = article.get(text_field, "")
        counts = track_keywords_in_text(text, keywords)
        aggregated_counts.update(counts)
    logger.info(f"Aggregated keyword counts in articles: {dict(aggregated_counts)}")
    return dict(aggregated_counts)

def track_keywords_in_fan_posts(fan_posts: List[dict], keywords: List[str], text_field: str = "content") -> Dict[str, int]:
    """
    Analyzes a list of fan posts to track keyword occurrences.
    
    Parameters:
        fan_posts (List[dict]): List of fan posts, each as a dictionary.
                                Each post must contain a text field (default "content") where keywords are searched.
        keywords (List[str]): List of keywords to track.
        text_field (str): The key in each fan post dict that holds the text to search.
    
    Returns:
        Dict[str, int]: Aggregated keyword counts across all fan posts.
    """
    aggregated_counts = Counter()
    for post in fan_posts:
        text = post.get(text_field, "")
        counts = track_keywords_in_text(text, keywords)
        aggregated_counts.update(counts)
    logger.info(f"Aggregated keyword counts in fan posts: {dict(aggregated_counts)}")
    return dict(aggregated_counts)

def track_keywords_bulk(data: List[dict], keywords: List[str], text_field: str) -> pd.DataFrame:
    """
    Tracks keyword occurrences in a bulk dataset using pandas for easy aggregation and analysis.
    
    Parameters:
        data (List[dict]): List of dictionaries where each dictionary has a text field.
        keywords (List[str]): List of keywords to track.
        text_field (str): The key containing the text to search in each dictionary.
    
    Returns:
        pd.DataFrame: DataFrame with each keyword and its aggregated count.
    """
    # Create DataFrame from data
    df = pd.DataFrame(data)
    if text_field not in df.columns:
        logger.error(f"Text field '{text_field}' not found in data.")
        return pd.DataFrame()
    
    # Define a function to count keywords in each row
    def count_keywords(text):
        return track_keywords_in_text(text, keywords)
    
    df['keyword_counts'] = df[text_field].apply(lambda x: count_keywords(x) if isinstance(x, str) else {})
    
    # Aggregate counts across all rows
    total_counts = Counter()
    for counts in df['keyword_counts']:
        total_counts.update(counts)
    
    result_df = pd.DataFrame(total_counts.items(), columns=['keyword', 'count']).sort_values(by='count', ascending=False)
    logger.info("Bulk keyword tracking complete. Aggregated counts:")
    logger.info(result_df.to_dict(orient="records"))
    return result_df

# -------------------------------
# Additional Recommendations:
# -------------------------------
# 1. **Advanced Text Processing:** Consider using NLP libraries (spaCy, NLTK) for more nuanced text analysis,
#    such as lemmatization, stemming, or ignoring stopwords.
# 2. **Asynchronous Processing:** For large datasets, you might integrate async processing or parallelism to speed up tracking.
# 3. **Configuration Management:** Store region-specific keyword lists and text field names in a configuration file.
# 4. **Error Handling:** Enhance error handling for non-string inputs and unexpected data structures.
# 5. **Integration:** Integrate this module with your reporting or visualization tools for a complete analytics pipeline.

if __name__ == "__main__":
    # Standalone testing with sample data.
    sample_articles = [
        {"title": "RLG Data sees significant growth in media coverage"},
        {"title": "New trends emerge in digital marketing for RLG Data"},
        {"title": "Competitive analysis shows rising interest in RLG Data technology"}
    ]
    
    sample_fan_posts = [
        {"content": "I love the new features of RLG Fans platform!"},
        {"content": "RLG Fans community is very active and engaging."},
        {"content": "The recent update to RLG Fans is impressive."}
    ]
    
    # Define a sample keyword list.
    keywords = ["RLG", "media", "digital", "community", "update", "growth"]
    
    # Track keywords in articles.
    article_keyword_counts = track_keywords_in_articles(sample_articles, keywords)
    print("Keyword counts in articles:", article_keyword_counts)
    
    # Track keywords in fan posts.
    fan_keyword_counts = track_keywords_in_fan_posts(sample_fan_posts, keywords)
    print("Keyword counts in fan posts:", fan_keyword_counts)
    
    # Bulk tracking using pandas for articles.
    articles_df = track_keywords_bulk(sample_articles, keywords, text_field="title")
    print("Bulk keyword counts (articles):")
    print(articles_df)

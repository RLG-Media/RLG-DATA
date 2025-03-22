# data_processing.py - Handles data processing and transformation for RLG Fans

import pandas as pd
import numpy as np
from datetime import datetime
import re
import logging
from sentiment_analysis import analyze_sentiment
from engagement_metrics import calculate_engagement_score
from text_preprocessing import preprocess_text

# Set up logging
logging.basicConfig(filename='data_processing.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')


def clean_and_normalize_data(raw_data):
    """
    Clean and normalize raw data from various platforms.
    """
    logging.info("Starting data cleaning and normalization.")
    try:
        # Convert raw data to DataFrame
        df = pd.DataFrame(raw_data)
        
        # Standardize date format
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
        
        # Remove special characters from text content
        df['content'] = df['content'].apply(preprocess_text)
        
        # Normalize engagement metrics to integers
        df['likes'] = df['likes'].fillna(0).astype(int)
        df['comments'] = df['comments'].fillna(0).astype(int)
        df['shares'] = df['shares'].fillna(0).astype(int)

        logging.info("Data cleaning and normalization completed successfully.")
        return df
    except Exception as e:
        logging.error(f"Data cleaning and normalization failed: {str(e)}")
        raise e


def enrich_data_with_features(df):
    """
    Enrich data with additional features, including sentiment and engagement score.
    """
    logging.info("Starting feature enrichment for data.")
    try:
        # Add sentiment analysis
        df['sentiment'] = df['content'].apply(analyze_sentiment)
        
        # Calculate engagement score based on likes, comments, and shares
        df['engagement_score'] = df.apply(
            lambda row: calculate_engagement_score(row['likes'], row['comments'], row['shares']),
            axis=1
        )

        # Identify keywords and hashtags for further analysis
        df['keywords'] = df['content'].apply(extract_keywords)
        df['hashtags'] = df['content'].apply(extract_hashtags)

        logging.info("Feature enrichment completed successfully.")
        return df
    except Exception as e:
        logging.error(f"Feature enrichment failed: {str(e)}")
        raise e


def extract_keywords(text):
    """
    Extract main keywords from the content.
    """
    try:
        words = [word for word in text.split() if len(word) > 3 and word.isalpha()]
        return words
    except Exception as e:
        logging.error(f"Keyword extraction failed: {str(e)}")
        return []


def extract_hashtags(text):
    """
    Extract hashtags from the content.
    """
    try:
        hashtags = re.findall(r"#(\w+)", text)
        return hashtags
    except Exception as e:
        logging.error(f"Hashtag extraction failed: {str(e)}")
        return []


def transform_to_time_series(df):
    """
    Transform the data into a time series format for temporal analysis.
    """
    logging.info("Starting time series transformation.")
    try:
        # Resample data by day and calculate daily engagement metrics
        df.set_index('created_at', inplace=True)
        time_series_data = df.resample('D').agg({
            'likes': 'sum',
            'comments': 'sum',
            'shares': 'sum',
            'engagement_score': 'mean'
        }).fillna(0)

        logging.info("Time series transformation completed successfully.")
        return time_series_data
    except Exception as e:
        logging.error(f"Time series transformation failed: {str(e)}")
        raise e


def process_and_save_data(raw_data, output_path='processed_data.csv'):
    """
    Main function to process raw data, enrich it with features, and save it.
    """
    logging.info("Starting full data processing workflow.")
    try:
        # Step 1: Clean and normalize the data
        df = clean_and_normalize_data(raw_data)
        
        # Step 2: Enrich data with additional features
        df = enrich_data_with_features(df)
        
        # Step 3: Save processed data for analysis
        df.to_csv(output_path, index=False)
        
        logging.info(f"Data processing workflow completed successfully. Data saved to {output_path}")
        return df
    except Exception as e:
        logging.error(f"Data processing workflow failed: {str(e)}")
        raise e

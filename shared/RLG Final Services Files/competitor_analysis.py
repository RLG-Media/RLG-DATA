"""
competitor_analysis.py

This module provides functionality for competitor analysis for both RLG Data and RLG Fans.
It retrieves competitor data from various sources, performs comparative analysis, and generates
actionable insights and recommendations to improve performance and brand equity.

Features:
- Fetch competitor data from pre-configured endpoints.
- Analyze media coverage and sentiment trends.
- Generate benchmark reports comparing key performance metrics.
- Provide recommendations for strategic improvements.
- Robust error handling and logging for scalability and automation.
"""

import logging
import requests
import pandas as pd

# Configure logging
logger = logging.getLogger("CompetitorAnalysis")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Example competitor configuration.
# In production, load these from secure configuration sources.
COMPETITOR_CONFIG = {
    "competitors": [
        {
            "name": "CompetitorA",
            "data_endpoint": "https://api.competitora.example.com/v1/data",
            "fans_endpoint": "https://api.competitora.example.com/v1/fans",
            "api_key": "COMPETITORA_API_KEY"
        },
        {
            "name": "CompetitorB",
            "data_endpoint": "https://api.competitorb.example.com/v1/data",
            "fans_endpoint": "https://api.competitorb.example.com/v1/fans",
            "api_key": "COMPETITORB_API_KEY"
        }
    ]
}

def fetch_competitor_data(endpoint, api_key=None):
    """
    Fetch competitor data from a given endpoint.
    
    Parameters:
        endpoint (str): The API URL from which to fetch data.
        api_key (str, optional): API key for authentication.
    
    Returns:
        dict or None: The JSON data from the API or None if an error occurs.
    """
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    try:
        response = requests.get(endpoint, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        logger.debug(f"Fetched data from {endpoint}: {data}")
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from {endpoint}: {e}")
        return None

def analyze_media_coverage(competitor_data_list):
    """
    Analyze media coverage across competitors.
    
    Parameters:
        competitor_data_list (list): List of dicts containing competitor data metrics.
        
    Expected keys in each dict:
        - name: Competitor name.
        - total_mentions: Total media mentions.
        - positive: Count of positive mentions.
        - neutral: Count of neutral mentions.
        - negative: Count of negative mentions.
        - reach: Audience reach metric.
    
    Returns:
        pd.DataFrame: DataFrame with computed sentiment scores and rankings.
    """
    # Convert list of dicts into a DataFrame.
    df = pd.DataFrame(competitor_data_list)
    if df.empty:
        logger.warning("No competitor data available for analysis.")
        return None

    # Calculate a sentiment score: (positive - negative) / total_mentions.
    # This is a simple metric to gauge overall sentiment.
    df['sentiment_score'] = (df['positive'] - df['negative']) / df['total_mentions']
    logger.info("Calculated sentiment scores for competitors.")

    # Rank competitors based on sentiment score and total mentions.
    df = df.sort_values(by=['sentiment_score', 'total_mentions'], ascending=False)
    return df

def generate_recommendations(analysis_df):
    """
    Generate recommendations based on competitor analysis.
    
    Parameters:
        analysis_df (pd.DataFrame): DataFrame containing competitor metrics and sentiment scores.
    
    Returns:
        list: A list of actionable recommendations.
    """
    recommendations = []
    if analysis_df is None or analysis_df.empty:
        recommendations.append("Insufficient data for recommendations.")
        return recommendations

    # Identify the top competitor.
    top_competitor = analysis_df.iloc[0]
    recommendations.append(
        f"Competitor {top_competitor['name']} has the highest sentiment score of {top_competitor['sentiment_score']:.2f}."
    )

    # Check if our own data is included (assumed to be labeled as "RLG").
    if "RLG" in analysis_df['name'].values:
        our_data = analysis_df[analysis_df['name'] == "RLG"].iloc[0]
        if our_data['sentiment_score'] < top_competitor['sentiment_score']:
            recommendations.append("Increase focus on positive messaging to improve sentiment score.")
        if our_data['total_mentions'] < top_competitor['total_mentions']:
            recommendations.append("Expand media outreach to boost brand presence and mentions.")
    else:
        recommendations.append("Include your own data in the analysis for more tailored recommendations.")
    
    return recommendations

def competitor_analysis():
    """
    Main function to perform competitor analysis for both RLG Data and RLG Fans.
    
    Steps:
    1. Fetch competitor data using the configured endpoints.
    2. Process and validate the retrieved data.
    3. Append your own (RLG) data for comparison.
    4. Analyze the data and calculate sentiment scores.
    5. Generate actionable recommendations.
    
    Returns:
        dict: A report including the analysis (as a list of dicts) and recommendations.
    """
    competitor_data_metrics = []

    # Fetch data for each competitor from the configuration.
    for competitor in COMPETITOR_CONFIG["competitors"]:
        name = competitor["name"]
        logger.info(f"Fetching competitor data for {name}.")
        data_endpoint = competitor.get("data_endpoint")
        api_key = competitor.get("api_key")
        
        # Fetch data for competitor.
        data = fetch_competitor_data(data_endpoint, api_key)
        if data is None:
            logger.warning(f"No data retrieved for competitor {name}. Skipping.")
            continue

        # Extract and validate necessary fields from data.
        try:
            total_mentions = data.get("total_mentions", 0)
            positive = data.get("positive", 0)
            neutral = data.get("neutral", 0)
            negative = data.get("negative", 0)
            reach = data.get("reach", 0)
        except Exception as e:
            logger.error(f"Error processing data for competitor {name}: {e}")
            continue

        competitor_data_metrics.append({
            "name": name,
            "total_mentions": total_mentions,
            "positive": positive,
            "neutral": neutral,
            "negative": negative,
            "reach": reach
        })

    # Append your own data for comparison.
    # Replace these dummy values with actual metrics for RLG Data/Fans.
    our_rlg_data = {
        "name": "RLG",
        "total_mentions": 1300,
        "positive": 900,
        "neutral": 300,
        "negative": 100,
        "reach": 15000
    }
    competitor_data_metrics.append(our_rlg_data)

    logger.info("Analyzing competitor data.")
    analysis_df = analyze_media_coverage(competitor_data_metrics)
    recommendations = generate_recommendations(analysis_df)

    # Prepare the final analysis report.
    analysis_report = {
        "analysis": analysis_df.to_dict(orient="records") if analysis_df is not None else [],
        "recommendations": recommendations
    }

    logger.info("Competitor analysis completed.")
    return analysis_report

if __name__ == "__main__":
    # For standalone testing, print the competitor analysis report.
    report = competitor_analysis()
    print("Competitor Analysis Report:")
    print(report)

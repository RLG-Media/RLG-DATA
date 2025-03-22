# data_analysis.py

import pandas as pd
import numpy as np
import logging
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from your_project_name.data_cleaning import clean_data
from your_project_name.analytics_engine import run_analytics
from your_project_name.config import REPORT_PATH, EMAIL_CONFIG
from your_project_name.error_handling import handle_error

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for the analysis
PLATFORM_LIST = ['OnlyFans', 'Patreon', 'Fansly', 'FANfix', 'Instagram', 'TikTok', 'YouTube']
SCALING_METHOD = 'standard'  # 'standard' for StandardScaler, 'minmax' for MinMaxScaler
ANALYSIS_TYPE = 'trend_analysis'  # Example analysis type (can be customized)

def perform_data_analysis(platforms=PLATFORM_LIST, start_date=None, end_date=None, scaling_method=SCALING_METHOD, analysis_type=ANALYSIS_TYPE):
    """
    Perform data analysis for the specified platforms and date range.
    
    Args:
        platforms (list): List of platforms to analyze.
        start_date (str): Optional start date for filtering the data (format: 'YYYY-MM-DD').
        end_date (str): Optional end date for filtering the data (format: 'YYYY-MM-DD').
        scaling_method (str): Method for scaling data, either 'standard' or 'minmax'.
        analysis_type (str): Type of analysis to perform, e.g., 'trend_analysis', 'engagement_analysis'.
    
    Returns:
        analysis_results (DataFrame): DataFrame containing the results of the analysis.
    """
    try:
        logger.info(f"Starting {analysis_type} for platforms: {', '.join(platforms)}")

        # Initialize an empty list to hold platform-specific analysis results
        analysis_results = []

        for platform in platforms:
            # Step 1: Fetch and clean data for the platform
            platform_data = fetch_and_clean_data(platform, start_date, end_date)
            
            if platform_data is None or platform_data.empty:
                logger.warning(f"No valid data available for platform: {platform}")
                continue

            # Step 2: Perform scaling if needed
            scaled_data = scale_data(platform_data, scaling_method)

            # Step 3: Perform the selected analysis type
            if analysis_type == 'trend_analysis':
                analysis_result = perform_trend_analysis(scaled_data, platform)
            elif analysis_type == 'engagement_analysis':
                analysis_result = perform_engagement_analysis(scaled_data, platform)
            else:
                logger.error(f"Unknown analysis type: {analysis_type}")
                continue

            # Step 4: Store the analysis result
            analysis_results.append(analysis_result)

        # Combine all platform analysis results into a single DataFrame
        final_analysis_df = pd.concat(analysis_results, ignore_index=True)
        save_analysis_report(final_analysis_df)
        
        return final_analysis_df

    except Exception as e:
        handle_error(e)
        return None


def fetch_and_clean_data(platform, start_date=None, end_date=None):
    """
    Fetch and clean data for a specific platform.
    
    Args:
        platform (str): The platform name (e.g., 'OnlyFans', 'Patreon').
        start_date (str): Optional start date for filtering.
        end_date (str): Optional end date for filtering.
    
    Returns:
        cleaned_data (DataFrame): The cleaned data for the platform.
    """
    try:
        logger.info(f"Fetching and cleaning data for platform: {platform}")

        # Fetch raw data from the database or APIs
        raw_data = get_platform_data(platform, start_date, end_date)
        
        # Clean the data
        cleaned_data = clean_data(raw_data, platform)
        
        if cleaned_data.empty:
            logger.warning(f"No cleaned data available for platform: {platform}")
        
        return cleaned_data

    except Exception as e:
        handle_error(e)
        return pd.DataFrame()


def scale_data(data, scaling_method='standard'):
    """
    Scale the data using the specified scaling method.
    
    Args:
        data (DataFrame): The data to scale.
        scaling_method (str): The scaling method to use ('standard' or 'minmax').
    
    Returns:
        scaled_data (DataFrame): The scaled data.
    """
    try:
        logger.info(f"Scaling data using method: {scaling_method}")

        if scaling_method == 'standard':
            scaler = StandardScaler()
        elif scaling_method == 'minmax':
            scaler = MinMaxScaler()
        else:
            raise ValueError("Invalid scaling method. Use 'standard' or 'minmax'.")

        # Assuming the numeric columns are those that need scaling
        numeric_columns = data.select_dtypes(include=np.number).columns
        scaled_data = data.copy()
        scaled_data[numeric_columns] = scaler.fit_transform(data[numeric_columns])

        return scaled_data

    except Exception as e:
        handle_error(e)
        return data


def perform_trend_analysis(data, platform):
    """
    Perform trend analysis on the given data.
    
    Args:
        data (DataFrame): The cleaned and scaled data.
        platform (str): The platform name for which the analysis is performed.
    
    Returns:
        trend_analysis_result (DataFrame): DataFrame with trend analysis results.
    """
    try:
        logger.info(f"Performing trend analysis for platform: {platform}")

        # Example: Trend analysis based on time (e.g., daily/monthly engagement trends)
        data['date'] = pd.to_datetime(data['date'])
        data['month'] = data['date'].dt.month
        trend_analysis_result = data.groupby(['month']).agg({
            'engagement': 'mean',
            'revenue': 'sum',
        }).reset_index()

        # Adding platform information to the result
        trend_analysis_result['platform'] = platform
        return trend_analysis_result

    except Exception as e:
        handle_error(e)
        return pd.DataFrame()


def perform_engagement_analysis(data, platform):
    """
    Perform engagement analysis on the given data.
    
    Args:
        data (DataFrame): The cleaned and scaled data.
        platform (str): The platform name for which the analysis is performed.
    
    Returns:
        engagement_analysis_result (DataFrame): DataFrame with engagement analysis results.
    """
    try:
        logger.info(f"Performing engagement analysis for platform: {platform}")

        # Example: Engagement analysis based on user interactions
        engagement_analysis_result = data.groupby(['user_id']).agg({
            'engagement': 'sum',
            'revenue': 'sum',
        }).reset_index()

        # Adding platform information to the result
        engagement_analysis_result['platform'] = platform
        return engagement_analysis_result

    except Exception as e:
        handle_error(e)
        return pd.DataFrame()


def save_analysis_report(report_df):
    """
    Save the analysis report to a CSV file.
    
    Args:
        report_df (DataFrame): The DataFrame containing the analysis report.
    """
    try:
        logger.info("Saving analysis report...")

        # Generate a timestamped file name for the report
        file_name = f"data_analysis_report_{pd.Timestamp.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        report_path = f"{REPORT_PATH}/{file_name}"
        
        report_df.to_csv(report_path, index=False)

        logger.info(f"Analysis report saved to: {report_path}")
        
        # Send the report via email (if configured)
        send_report_email(report_path, EMAIL_CONFIG)

    except Exception as e:
        handle_error(e)


if __name__ == "__main__":
    # Run the data analysis
    final_report_df = perform_data_analysis(platforms=PLATFORM_LIST, start_date="2024-01-01", end_date="2024-12-31")
    
    if final_report_df is not None and not final_report_df.empty:
        logger.info("Data analysis completed successfully.")
    else:
        logger.error("Data analysis failed.")

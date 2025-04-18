# cross_platform_report_generator.py

import pandas as pd
import json
import logging
from datetime import datetime
from sqlalchemy import create_engine
from your_project_name.data_ingestion import get_platform_data
from your_project_name.data_cleaning import clean_data
from your_project_name.analytics_engine import run_analytics
from your_project_name.notification_system import send_report_email
from your_project_name.error_handling import handle_error
from your_project_name.config import DATABASE_URI, EMAIL_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
PLATFORM_LIST = ['OnlyFans', 'Patreon', 'Fansly', 'FANfix', 'Instagram', 'TikTok', 'YouTube']
REPORT_PATH = "/path/to/save/reports/"
REPORT_FILE_NAME = "cross_platform_report_{}.csv".format(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))

# Initialize database connection (SQLAlchemy)
engine = create_engine(DATABASE_URI)

def generate_cross_platform_report(platforms=PLATFORM_LIST, start_date=None, end_date=None):
    """
    Generate a cross-platform performance report.
    
    Args:
        platforms (list): List of platforms to include in the report.
        start_date (str): Optional start date for filtering the data (format: 'YYYY-MM-DD').
        end_date (str): Optional end date for filtering the data (format: 'YYYY-MM-DD').
    
    Returns:
        report_df (DataFrame): The generated report as a Pandas DataFrame.
    """
    try:
        logger.info("Starting report generation process...")

        # Initialize an empty list to collect data from each platform
        report_data = []

        for platform in platforms:
            # Fetch platform data (could be API or database query)
            platform_data = get_platform_data(platform, start_date, end_date)
            
            if platform_data.empty:
                logger.warning(f"No data found for platform: {platform}")
                continue
            
            # Clean the fetched data
            cleaned_data = clean_data(platform_data, platform)
            
            if cleaned_data.empty:
                logger.warning(f"Cleaned data is empty for platform: {platform}")
                continue
            
            # Run analytics and generate insights
            analytics_result = run_analytics(cleaned_data, platform)
            
            # Add the analytics result to the report data list
            report_data.append(analytics_result)

        if not report_data:
            logger.error("No data to generate report.")
            return None

        # Combine all platform data into a single DataFrame
        report_df = pd.concat(report_data, ignore_index=True)

        # Save the generated report to CSV
        report_file_path = REPORT_PATH + REPORT_FILE_NAME
        report_df.to_csv(report_file_path, index=False)

        logger.info(f"Cross-platform report generated and saved to: {report_file_path}")

        # Send the report via email
        send_report_email(report_file_path, EMAIL_CONFIG)

        return report_df

    except Exception as e:
        handle_error(e)
        return None

def fetch_platform_data(platform, start_date=None, end_date=None):
    """
    Helper function to fetch platform-specific data from database or APIs.
    
    Args:
        platform (str): The name of the platform (e.g., 'OnlyFans', 'Patreon').
        start_date (str): Optional start date for filtering the data.
        end_date (str): Optional end date for filtering the data.
    
    Returns:
        data (DataFrame): The platform's data as a Pandas DataFrame.
    """
    try:
        logger.info(f"Fetching data for platform: {platform}")

        if platform not in PLATFORM_LIST:
            raise ValueError(f"Platform {platform} not supported")

        # Example: Fetch data from database
        query = f"SELECT * FROM {platform.lower()}_data WHERE date >= '{start_date}' AND date <= '{end_date}'"
        data = pd.read_sql(query, engine)

        if data.empty:
            logger.warning(f"No data found for {platform} in the specified date range.")
        
        return data
    
    except Exception as e:
        handle_error(e)
        return pd.DataFrame()

def generate_summary_report(report_df):
    """
    Generate a summary of the report including key performance metrics.
    
    Args:
        report_df (DataFrame): The generated cross-platform report.
    
    Returns:
        summary_dict (dict): A dictionary with key performance metrics.
    """
    try:
        logger.info("Generating summary report...")

        if report_df is None or report_df.empty:
            logger.error("Cannot generate summary. Report is empty.")
            return {}

        # Example summary calculations (engagement rate, revenue, etc.)
        summary_dict = {
            "total_platforms": len(report_df['platform'].unique()),
            "total_revenue": report_df['revenue'].sum(),
            "total_engagement": report_df['engagement'].sum(),
            "avg_engagement_rate": report_df['engagement'].mean(),
            "avg_revenue_per_user": report_df['revenue_per_user'].mean(),
            "top_performing_platform": report_df.groupby('platform')['revenue'].sum().idxmax()
        }

        logger.info("Summary report generated successfully.")
        return summary_dict

    except Exception as e:
        handle_error(e)
        return {}

def save_summary_to_file(summary_dict):
    """
    Save the summary of the report to a file.
    
    Args:
        summary_dict (dict): A dictionary with summary statistics.
    """
    try:
        if not summary_dict:
            logger.error("No summary data to save.")
            return

        summary_file_path = REPORT_PATH + "summary_report_{}.json".format(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        with open(summary_file_path, 'w') as f:
            json.dump(summary_dict, f, indent=4)

        logger.info(f"Summary report saved to: {summary_file_path}")
    except Exception as e:
        handle_error(e)

if __name__ == "__main__":
    # Generate the full cross-platform report and summary
    cross_platform_report_df = generate_cross_platform_report()
    
    if cross_platform_report_df is not None:
        # Generate and save the summary report
        summary = generate_summary_report(cross_platform_report_df)
        save_summary_to_file(summary)

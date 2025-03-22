"""
report_generator.py

This module generates HTML reports for both RLG Data (media articles) and RLG Fans (social posts).
It queries data using the DatabaseManager (SQLAlchemy-based), computes summary statistics with pandas,
and outputs the reports as HTML files saved in a designated reports directory.

Reports include:
    - Total record counts.
    - Sentiment distribution for RLG Data.
    - Average engagement and record counts for RLG Fans.
    - Date range of the scraped data.

For production, customize the report templates and extend the metrics as needed.
"""

import os
import logging
from datetime import datetime

import pandas as pd

# Import the DatabaseManager from our database_manager.py module.
from database_manager import DatabaseManager

# Configure logging for the report generator.
logger = logging.getLogger("ReportGenerator")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

# Define the directory to save report files.
REPORTS_DIR = "reports"
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)
    logger.info(f"Created reports directory: {REPORTS_DIR}")

class ReportGenerator:
    def __init__(self, region: str = "default"):
        """
        Initializes the ReportGenerator.

        Parameters:
            region (str): Region identifier to filter data (if desired). Default is 'default'.
        """
        self.region = region
        # Initialize the database manager (ensure DATABASE_URL or equivalent is configured).
        self.db_manager = DatabaseManager()
        logger.info(f"ReportGenerator initialized for region: {self.region}")

    def generate_rlg_data_report(self) -> str:
        """
        Generates an HTML report for RLG Data (media articles).
        
        The report includes:
            - Total number of articles.
            - Distribution of sentiment (e.g., positive, neutral, negative).
            - Time span of data (earliest and latest scrape timestamps).

        Returns:
            str: File path to the generated HTML report.
        """
        try:
            # Query RLG Data records, optionally filtering by region.
            records = self.db_manager.query_rlg_data(region=self.region)
            if not records:
                logger.warning("No RLG Data records found for report generation.")
                return ""

            # Convert SQLAlchemy records to a list of dictionaries.
            data_list = [
                {
                    "id": record.id,
                    "title": record.title,
                    "sentiment": record.sentiment,
                    "region": record.region,
                    "scraped_at": record.scraped_at
                }
                for record in records
            ]
            df = pd.DataFrame(data_list)
            logger.info(f"Retrieved {len(df)} RLG Data records for report.")

            # Compute summary statistics.
            total_articles = len(df)
            sentiment_distribution = df["sentiment"].value_counts().to_dict()
            min_date = df["scraped_at"].min()
            max_date = df["scraped_at"].max()

            # Prepare a summary DataFrame.
            summary = pd.DataFrame({
                "Metric": ["Total Articles", "Earliest Record", "Latest Record"],
                "Value": [total_articles, min_date, max_date]
            })

            # Build an HTML report.
            report_html = f"""
            <html>
                <head>
                    <title>RLG Data Report - {self.region.capitalize()}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        h1 {{ color: #2c3e50; }}
                        table {{ border-collapse: collapse; width: 80%; margin-bottom: 20px; }}
                        th, td {{ border: 1px solid #ddd; padding: 8px; }}
                        th {{ background-color: #f2f2f2; }}
                    </style>
                </head>
                <body>
                    <h1>RLG Data Report - Region: {self.region.capitalize()}</h1>
                    <h2>Summary Statistics</h2>
                    {summary.to_html(index=False, justify="center")}
                    <h2>Sentiment Distribution</h2>
                    {pd.DataFrame(list(sentiment_distribution.items()), columns=["Sentiment", "Count"]).to_html(index=False, justify="center")}
                    <h2>Detailed Records</h2>
                    {df.to_html(index=False, justify="center")}
                    <p>Report generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                </body>
            </html>
            """

            # Save the report to a file.
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"rlg_data_report_{self.region}_{timestamp}.html"
            filepath = os.path.join(REPORTS_DIR, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(report_html)
            logger.info(f"RLG Data report generated and saved to {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error generating RLG Data report: {e}")
            return ""

    def generate_rlg_fans_report(self) -> str:
        """
        Generates an HTML report for RLG Fans (social posts).

        The report includes:
            - Total number of fan posts.
            - Average engagement score.
            - Distribution of engagement (e.g., histogram data summary).
            - Time span of data (earliest and latest scrape timestamps).

        Returns:
            str: File path to the generated HTML report.
        """
        try:
            # Query RLG Fans records, optionally filtering by region.
            records = self.db_manager.query_rlg_fans(region=self.region)
            if not records:
                logger.warning("No RLG Fans records found for report generation.")
                return ""

            # Convert records to a list of dictionaries.
            data_list = [
                {
                    "id": record.id,
                    "content": record.content,
                    "engagement": record.engagement,
                    "region": record.region,
                    "scraped_at": record.scraped_at
                }
                for record in records
            ]
            df = pd.DataFrame(data_list)
            logger.info(f"Retrieved {len(df)} RLG Fans records for report.")

            # Compute summary statistics.
            total_posts = len(df)
            average_engagement = df["engagement"].mean() if total_posts > 0 else 0.0
            min_date = df["scraped_at"].min()
            max_date = df["scraped_at"].max()

            summary = pd.DataFrame({
                "Metric": ["Total Posts", "Average Engagement", "Earliest Record", "Latest Record"],
                "Value": [total_posts, f"{average_engagement:.2f}", min_date, max_date]
            })

            # Build an HTML report.
            report_html = f"""
            <html>
                <head>
                    <title>RLG Fans Report - {self.region.capitalize()}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        h1 {{ color: #2c3e50; }}
                        table {{ border-collapse: collapse; width: 80%; margin-bottom: 20px; }}
                        th, td {{ border: 1px solid #ddd; padding: 8px; }}
                        th {{ background-color: #f2f2f2; }}
                    </style>
                </head>
                <body>
                    <h1>RLG Fans Report - Region: {self.region.capitalize()}</h1>
                    <h2>Summary Statistics</h2>
                    {summary.to_html(index=False, justify="center")}
                    <h2>Detailed Records</h2>
                    {df.to_html(index=False, justify="center")}
                    <p>Report generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                </body>
            </html>
            """

            # Save the report to a file.
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"rlg_fans_report_{self.region}_{timestamp}.html"
            filepath = os.path.join(REPORTS_DIR, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(report_html)
            logger.info(f"RLG Fans report generated and saved to {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error generating RLG Fans report: {e}")
            return ""

# -------------------------------
# Standalone Testing
# -------------------------------
if __name__ == "__main__":
    try:
        # Initialize the report generator for a given region (default: 'default').
        report_gen = ReportGenerator(region="default")
        
        # Generate reports for both RLG Data and RLG Fans.
        data_report_path = report_gen.generate_rlg_data_report()
        fans_report_path = report_gen.generate_rlg_fans_report()
        
        if data_report_path:
            print(f"RLG Data report generated at: {data_report_path}")
        else:
            print("Failed to generate RLG Data report.")
        
        if fans_report_path:
            print(f"RLG Fans report generated at: {fans_report_path}")
        else:
            print("Failed to generate RLG Fans report.")
    
    except Exception as e:
        logger.error(f"Error in standalone report generation: {e}")

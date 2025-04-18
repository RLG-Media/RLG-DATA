import logging
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("platform_usage_insights.log"),
        logging.StreamHandler()
    ]
)

class PlatformUsageInsights:
    """
    Service class for analyzing and generating insights on platform usage metrics for RLG Data and RLG Fans.
    Includes multi-platform analysis, trends, and actionable recommendations.
    """

    def __init__(self):
        self.platforms = ["Facebook", "Instagram", "Twitter", "TikTok", "LinkedIn", "Pinterest", "Reddit", "Snapchat", "Threads"]
        logging.info("PlatformUsageInsights initialized for platforms: %s", self.platforms)

    def aggregate_usage_data(self, raw_data: List[Dict]) -> pd.DataFrame:
        """
        Aggregate raw usage data into a structured DataFrame.

        Args:
            raw_data: List of dictionaries containing platform usage metrics.

        Returns:
            A pandas DataFrame with aggregated metrics.
        """
        try:
            df = pd.DataFrame(raw_data)
            logging.info("Aggregated %d usage records into a DataFrame.", len(df))
            return df
        except Exception as e:
            logging.error("Failed to aggregate usage data: %s", e)
            raise

    def calculate_trends(self, data: pd.DataFrame, time_column: str, metric_column: str) -> pd.DataFrame:
        """
        Calculate trends in usage metrics over time.

        Args:
            data: DataFrame containing usage data.
            time_column: Column name for timestamps.
            metric_column: Column name for the metric to analyze.

        Returns:
            A DataFrame with trend data.
        """
        try:
            data[time_column] = pd.to_datetime(data[time_column])
            trend_data = data.groupby(data[time_column].dt.to_period("M"))[metric_column].sum().reset_index()
            trend_data[time_column] = trend_data[time_column].dt.to_timestamp()
            logging.info("Calculated trends for metric '%s'.", metric_column)
            return trend_data
        except Exception as e:
            logging.error("Failed to calculate trends: %s", e)
            raise

    def generate_recommendations(self, usage_data: pd.DataFrame) -> List[str]:
        """
        Generate actionable recommendations based on usage data.

        Args:
            usage_data: DataFrame containing platform usage metrics.

        Returns:
            A list of recommendations.
        """
        try:
            recommendations = []
            total_usage = usage_data.sum(axis=0)

            for platform in self.platforms:
                if platform in total_usage and total_usage[platform] < 1000:
                    recommendations.append(f"Increase content engagement on {platform} with targeted campaigns.")

            if total_usage.mean() > 5000:
                recommendations.append("Overall platform usage is high. Consider scaling server resources.")

            logging.info("Generated %d recommendations.", len(recommendations))
            return recommendations
        except Exception as e:
            logging.error("Failed to generate recommendations: %s", e)
            raise

    def export_insights(self, insights: pd.DataFrame, output_path: str) -> None:
        """
        Export insights to a CSV file.

        Args:
            insights: DataFrame containing insights.
            output_path: Path to save the CSV file.
        """
        try:
            insights.to_csv(output_path, index=False)
            logging.info("Insights exported to %s.", output_path)
        except Exception as e:
            logging.error("Failed to export insights: %s", e)
            raise

    def fetch_and_process_usage_data(self, api_client, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch usage data from multiple platforms and process it.

        Args:
            api_client: API client to fetch usage data.
            start_date: Start date for data fetching (YYYY-MM-DD).
            end_date: End date for data fetching (YYYY-MM-DD).

        Returns:
            A processed DataFrame with usage data.
        """
        try:
            raw_data = []
            for platform in self.platforms:
                platform_data = api_client.fetch_usage_data(platform, start_date, end_date)
                raw_data.extend(platform_data)

            processed_data = self.aggregate_usage_data(raw_data)
            logging.info("Fetched and processed usage data for all platforms.")
            return processed_data
        except Exception as e:
            logging.error("Failed to fetch and process usage data: %s", e)
            raise

# Example usage
if __name__ == "__main__":
    usage_insights = PlatformUsageInsights()

    # Simulated raw data
    raw_usage_data = [
        {"platform": "Facebook", "date": "2025-01-01", "engagements": 500},
        {"platform": "Instagram", "date": "2025-01-01", "engagements": 700},
        {"platform": "Twitter", "date": "2025-01-01", "engagements": 300},
        {"platform": "TikTok", "date": "2025-01-01", "engagements": 900},
    ]

    # Aggregate data
    aggregated_data = usage_insights.aggregate_usage_data(raw_usage_data)

    # Calculate trends
    trends = usage_insights.calculate_trends(aggregated_data, time_column="date", metric_column="engagements")

    # Generate recommendations
    recommendations = usage_insights.generate_recommendations(aggregated_data)
    for rec in recommendations:
        print(rec)

    # Export insights
    usage_insights.export_insights(trends, "usage_trends.csv")

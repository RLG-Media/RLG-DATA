import requests
import logging
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("competitive_analysis_tools.log"),
        logging.StreamHandler()
    ]
)

class CompetitiveAnalysisTools:
    """
    A service to perform competitive analysis across social media platforms.
    """

    def __init__(self):
        self.social_media_endpoints = {
            "twitter": "http://twitter_service:5000",
            "facebook": "http://facebook_service:5000",
            "instagram": "http://instagram_service:5000",
            "linkedin": "http://linkedin_service:5000",
            "tiktok": "http://tiktok_service:5000",
            "pinterest": "http://pinterest_service:5000",
            "reddit": "http://reddit_service:5000",
            "snapchat": "http://snapchat_service:5000",
            "threads": "http://threads_service:5000"
        }

    def fetch_competitor_data(self, platform: str, competitor_handle: str) -> Dict:
        """
        Fetch competitor data from the specified platform.

        Args:
            platform (str): The social media platform to fetch data from.
            competitor_handle (str): The competitor's username or handle.

        Returns:
            Dict: Data related to the competitor's activity and performance.
        """
        if platform not in self.social_media_endpoints:
            logging.error(f"Platform '{platform}' is not supported.")
            return {"error": f"Platform '{platform}' is not supported."}

        url = f"{self.social_media_endpoints[platform]}/competitor/{competitor_handle}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            logging.info(f"Fetched competitor data for {competitor_handle} on {platform}.")
            return response.json()
        except Exception as e:
            logging.error(f"Failed to fetch competitor data: {e}")
            return {"error": "Failed to fetch competitor data."}

    def compare_metrics(self, user_data: Dict, competitor_data: Dict) -> Dict:
        """
        Compare user metrics with competitor metrics.

        Args:
            user_data (Dict): Metrics data for the user.
            competitor_data (Dict): Metrics data for the competitor.

        Returns:
            Dict: Comparison results showing strengths and weaknesses.
        """
        comparison_results = {}

        for metric, user_value in user_data.items():
            competitor_value = competitor_data.get(metric, 0)

            comparison_results[metric] = {
                "user": user_value,
                "competitor": competitor_value,
                "difference": user_value - competitor_value
            }

        logging.info("Comparison metrics generated successfully.")
        return comparison_results

    def generate_insights(self, comparison_results: Dict) -> List[str]:
        """
        Generate actionable insights based on comparison results.

        Args:
            comparison_results (Dict): The results of the metric comparison.

        Returns:
            List[str]: A list of insights and recommendations.
        """
        insights = []

        for metric, values in comparison_results.items():
            if values["difference"] > 0:
                insights.append(f"You are outperforming your competitor in {metric} by {values['difference']}. Keep it up!")
            elif values["difference"] < 0:
                insights.append(f"Your competitor is ahead in {metric} by {abs(values['difference'])}. Consider improving your strategy in this area.")
            else:
                insights.append(f"You and your competitor are evenly matched in {metric}.")

        logging.info("Insights generated successfully.")
        return insights

    def benchmark_industry(self, industry: str) -> Dict:
        """
        Fetch and analyze industry-wide benchmarks for comparison.

        Args:
            industry (str): The industry to benchmark against.

        Returns:
            Dict: Industry benchmark data.
        """
        url = f"http://industry_benchmark_service:5000/benchmarks/{industry}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            logging.info(f"Fetched industry benchmark data for {industry}.")
            return response.json()
        except Exception as e:
            logging.error(f"Failed to fetch industry benchmarks: {e}")
            return {"error": "Failed to fetch industry benchmarks."}

# Example usage
if __name__ == "__main__":
    service = CompetitiveAnalysisTools()

    user_metrics = {
        "followers": 5000,
        "engagement_rate": 4.5,
        "posts_per_week": 10
    }

    competitor_metrics = service.fetch_competitor_data("twitter", "competitor_handle")
    if "error" not in competitor_metrics:
        comparison = service.compare_metrics(user_metrics, competitor_metrics)
        insights = service.generate_insights(comparison)

        for insight in insights:
            print(insight)

    industry_data = service.benchmark_industry("technology")
    print("Industry Benchmarks:", industry_data)

import datetime
import json
from typing import Any, Dict, List, Optional, Union
from collections import Counter
from statistics import mean
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("insights_backend.log"),
        logging.StreamHandler()
    ]
)

class InsightsBackend:
    """
    Backend class for managing insights for RLG Data and RLG Fans.
    Provides tools for aggregating, analyzing, and delivering actionable insights.
    """

    def __init__(self, data_source: str = "insights_data.json"):
        """
        Initializes the insights backend with a data source.
        :param data_source: Path to the data source file (JSON format).
        """
        self.data_source = data_source
        self._initialize_data_source()

    def _initialize_data_source(self):
        """Ensures the data source file exists and initializes it if empty."""
        try:
            with open(self.data_source, "r") as file:
                json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            with open(self.data_source, "w") as file:
                json.dump([], file)
            logging.info(f"Data source initialized at {self.data_source}.")

    def _read_data(self) -> List[Dict[str, Any]]:
        """Reads data from the data source."""
        with open(self.data_source, "r") as file:
            return json.load(file)

    def _write_data(self, data: List[Dict[str, Any]]):
        """Writes data to the data source."""
        with open(self.data_source, "w") as file:
            json.dump(data, file, indent=4)

    def add_insight(self, insight: Dict[str, Any]) -> bool:
        """
        Adds a new insight to the data source.
        :param insight: A dictionary containing the insight details.
        :return: True if the insight was added successfully.
        """
        data = self._read_data()
        data.append(insight)
        self._write_data(data)
        logging.info(f"New insight added: {insight['title']}.")
        return True

    def generate_overview(self) -> Dict[str, Any]:
        """
        Generates an overview of insights, including key statistics.
        :return: A dictionary containing the overview.
        """
        data = self._read_data()

        if not data:
            logging.warning("No insights available for overview generation.")
            return {
                "total_insights": 0,
                "platforms": [],
                "categories": [],
                "average_engagement": 0.0,
                "generated_on": datetime.datetime.now().isoformat()
            }

        platforms = Counter(item["platform"] for item in data)
        categories = Counter(item["category"] for item in data)
        avg_engagement = mean(item["engagement_score"] for item in data if "engagement_score" in item)

        overview = {
            "total_insights": len(data),
            "platforms": platforms.most_common(),
            "categories": categories.most_common(),
            "average_engagement": avg_engagement,
            "generated_on": datetime.datetime.now().isoformat()
        }

        logging.info("Overview generated.")
        return overview

    def filter_insights(self, platform: Optional[str] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Filters insights by platform and/or category.
        :param platform: The platform to filter by (e.g., 'Instagram').
        :param category: The category to filter by (e.g., 'Monetization').
        :return: A list of filtered insights.
        """
        data = self._read_data()
        filtered_data = data

        if platform:
            filtered_data = [item for item in filtered_data if item.get("platform") == platform]
        if category:
            filtered_data = [item for item in filtered_data if item.get("category") == category]

        logging.info(f"Filtered {len(filtered_data)} insights by platform: {platform}, category: {category}.")
        return filtered_data

    def generate_insight_recommendations(self, user_id: str, preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generates personalized insight recommendations based on user preferences.
        :param user_id: The unique identifier of the user.
        :param preferences: A dictionary of user preferences.
        :return: A list of recommended insights.
        """
        data = self._read_data()

        recommendations = [
            item for item in data
            if item["platform"] in preferences.get("platforms", [])
            and item["category"] in preferences.get("categories", [])
        ]

        sorted_recommendations = sorted(recommendations, key=lambda x: x.get("engagement_score", 0), reverse=True)
        logging.info(f"Generated {len(sorted_recommendations)} recommendations for user_id: {user_id}.")
        return sorted_recommendations

    def get_insight_details(self, insight_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves details of a specific insight by its ID.
        :param insight_id: The unique identifier of the insight.
        :return: A dictionary of insight details or None if not found.
        """
        data = self._read_data()
        insight = next((item for item in data if item.get("id") == insight_id), None)

        if insight:
            logging.info(f"Details retrieved for insight_id: {insight_id}.")
        else:
            logging.warning(f"Insight not found for insight_id: {insight_id}.")
        return insight

# --- Example Usage ---
if __name__ == "__main__":
    insights = InsightsBackend()

    # Add example insights
    insights.add_insight({
        "id": "1",
        "title": "Optimal Posting Times for Instagram",
        "platform": "Instagram",
        "category": "Engagement",
        "engagement_score": 85.3,
        "details": "Post between 6 PM and 9 PM for maximum engagement."
    })

    insights.add_insight({
        "id": "2",
        "title": "Monetization Tips for YouTube Creators",
        "platform": "YouTube",
        "category": "Monetization",
        "engagement_score": 92.7,
        "details": "Diversify income streams through sponsorships and memberships."
    })

    # Generate overview
    overview = insights.generate_overview()
    print("Overview:", overview)

    # Filter insights
    filtered = insights.filter_insights(platform="Instagram")
    print("Filtered Insights:", filtered)

    # Get recommendations
    user_preferences = {"platforms": ["YouTube"], "categories": ["Monetization"]}
    recommendations = insights.generate_insight_recommendations(user_id="123", preferences=user_preferences)
    print("Recommendations:", recommendations)

    # Get details of a specific insight
    insight_details = insights.get_insight_details("1")
    print("Insight Details:", insight_details)

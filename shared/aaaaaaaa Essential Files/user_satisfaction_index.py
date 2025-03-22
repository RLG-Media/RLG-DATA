import logging
from typing import List, Dict, Any
from datetime import datetime
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/user_satisfaction_index.log"),
    ],
)


class UserSatisfactionIndex:
    """
    A class to calculate, monitor, and analyze the User Satisfaction Index (USI) for RLG Data and RLG Fans.
    """

    def __init__(self):
        """
        Initialize the User Satisfaction Index system.
        """
        logging.info("UserSatisfactionIndex initialized.")

    def fetch_feedback_data(self) -> List[Dict[str, Any]]:
        """
        Fetch user feedback data from multiple platforms.

        Returns:
            A list of dictionaries containing user feedback data.
        """
        logging.info("Fetching user feedback data...")
        try:
            # Simulated feedback data
            feedback_data = [
                {"platform": "RLG_Data", "rating": 4.5, "comments": "Very helpful and easy to use."},
                {"platform": "RLG_Fans", "rating": 4.2, "comments": "Great for social media management."},
                {"platform": "Facebook", "rating": 3.8, "comments": "Could use better reporting features."},
                {"platform": "Twitter", "rating": 4.0, "comments": "Scheduling is fantastic!"},
                {"platform": "Instagram", "rating": 4.3, "comments": "Very intuitive interface."},
                {"platform": "LinkedIn", "rating": 4.1, "comments": "Analytics are spot on."},
            ]
            logging.info(f"Feedback data fetched: {feedback_data}")
            return feedback_data
        except Exception as e:
            logging.error(f"Error fetching feedback data: {e}")
            raise

    def calculate_usi(self, feedback_data: List[Dict[str, Any]]) -> float:
        """
        Calculate the User Satisfaction Index (USI) based on feedback ratings.

        Args:
            feedback_data: A list of dictionaries containing user feedback data.

        Returns:
            The calculated User Satisfaction Index as a float.
        """
        logging.info("Calculating User Satisfaction Index (USI)...")
        try:
            ratings = [feedback["rating"] for feedback in feedback_data]
            usi = np.mean(ratings) if ratings else 0.0
            logging.info(f"Calculated USI: {usi:.2f}")
            return usi
        except Exception as e:
            logging.error(f"Error calculating USI: {e}")
            raise

    def generate_usi_report(self, usi: float, feedback_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a detailed User Satisfaction Index report.

        Args:
            usi: The calculated User Satisfaction Index.
            feedback_data: A list of dictionaries containing user feedback data.

        Returns:
            A dictionary containing the USI report.
        """
        logging.info("Generating USI report...")
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "usi": round(usi, 2),
                "feedback_summary": feedback_data,
                "recommendations": self.generate_recommendations(feedback_data, usi),
            }
            logging.info(f"Generated USI report: {report}")
            return report
        except Exception as e:
            logging.error(f"Error generating USI report: {e}")
            raise

    def generate_recommendations(self, feedback_data: List[Dict[str, Any]], usi: float) -> List[str]:
        """
        Generate recommendations to improve user satisfaction based on feedback and USI.

        Args:
            feedback_data: A list of dictionaries containing user feedback data.
            usi: The calculated User Satisfaction Index.

        Returns:
            A list of recommendations.
        """
        logging.info("Generating recommendations for user satisfaction improvement...")
        recommendations = []
        try:
            if usi < 4.0:
                recommendations.append("Overall satisfaction is below expectations. Focus on usability improvements.")
            for feedback in feedback_data:
                if "better reporting" in feedback["comments"].lower():
                    recommendations.append(f"Improve reporting features on {feedback['platform']}.")
                if "scheduling" in feedback["comments"].lower() and feedback["rating"] < 4.0:
                    recommendations.append(f"Enhance scheduling features on {feedback['platform']}.")
            logging.info(f"Generated recommendations: {recommendations}")
            return recommendations
        except Exception as e:
            logging.error(f"Error generating recommendations: {e}")
            raise

    def save_usi_report(self, report: Dict[str, Any]) -> None:
        """
        Save the USI report to a file for future analysis.

        Args:
            report: The USI report to save.
        """
        try:
            file_name = f"reports/usi_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            logging.info(f"Saving USI report to {file_name}...")
            with open(file_name, "w") as file:
                import json
                json.dump(report, file, indent=4)
            logging.info(f"USI report saved to {file_name}.")
        except Exception as e:
            logging.error(f"Error saving USI report: {e}")
            raise


# Example Usage
if __name__ == "__main__":
    usi_manager = UserSatisfactionIndex()

    # Fetch feedback data
    feedback = usi_manager.fetch_feedback_data()

    # Calculate USI
    usi_score = usi_manager.calculate_usi(feedback)

    # Generate and save USI report
    report = usi_manager.generate_usi_report(usi_score, feedback)
    usi_manager.save_usi_report(report)

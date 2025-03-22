import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from shared.utils import log_info, log_error
from shared.config import SUPPORTED_SOCIAL_MEDIA_PLATFORMS, REPORT_STORAGE_PATH

class PredictiveEngagementReports:
    def __init__(self):
        self.supported_platforms = SUPPORTED_SOCIAL_MEDIA_PLATFORMS
        self.report_storage = REPORT_STORAGE_PATH

    def fetch_engagement_data(self, platform: str, start_date: str, end_date: str) -> pd.DataFrame:
        try:
            # Simulate fetching data from the platform
            log_info(f"Fetching engagement data for platform {platform} from {start_date} to {end_date}")
            # Simulated data for demonstration
            data = [
                {"post_id": "1", "likes": 100, "shares": 50, "comments": 20, "platform": platform},
                {"post_id": "2", "likes": 200, "shares": 80, "comments": 60, "platform": platform},
                {"post_id": "3", "likes": 150, "shares": 60, "comments": 40, "platform": platform},
            ]
            return pd.DataFrame(data)
        except Exception as e:
            log_error(f"Error fetching engagement data for {platform}: {str(e)}")
            return pd.DataFrame()

    def predict_engagement(self, data: pd.DataFrame, target_col: str = "engagement_score") -> Dict[str, Any]:
        try:
            if data.empty:
                return {"error": "No data available for prediction."}

            log_info("Preparing data for predictive model.")
            data["engagement_score"] = data["likes"] * 0.5 + data["shares"] * 0.3 + data["comments"] * 0.2

            X = data[["likes", "shares", "comments"]]
            y = (data[target_col] > data[target_col].median()).astype(int)

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)

            predictions = model.predict(X_test)
            report = classification_report(y_test, predictions, output_dict=True)

            return {
                "model_accuracy": report["accuracy"],
                "classification_report": report,
                "feature_importances": dict(zip(X.columns, model.feature_importances_)),
            }
        except Exception as e:
            log_error(f"Error during engagement prediction: {str(e)}")
            return {"error": str(e)}

    def generate_report(self, platform: str, report_data: Dict[str, Any]) -> str:
        try:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            report_filename = f"{platform}_predictive_engagement_report_{timestamp}.json"
            report_path = f"{self.report_storage}/{report_filename}"

            log_info(f"Generating predictive engagement report for {platform}.")
            with open(report_path, "w") as report_file:
                json.dump(report_data, report_file, indent=4)

            return report_path
        except Exception as e:
            log_error(f"Error generating report for {platform}: {str(e)}")
            return ""

    def run(self, platforms: List[str], date_range: Dict[str, str]) -> List[str]:
        try:
            start_date, end_date = date_range["start_date"], date_range["end_date"]
            generated_reports = []

            for platform in platforms:
                if platform not in self.supported_platforms:
                    log_error(f"Platform {platform} is not supported.")
                    continue

                data = self.fetch_engagement_data(platform, start_date, end_date)
                prediction_results = self.predict_engagement(data)

                if "error" in prediction_results:
                    log_error(f"Error in prediction for {platform}: {prediction_results['error']}")
                    continue

                report_path = self.generate_report(platform, prediction_results)
                if report_path:
                    log_info(f"Generated report for {platform}: {report_path}")
                    generated_reports.append(report_path)

            return generated_reports
        except Exception as e:
            log_error(f"Error running predictive engagement reports: {str(e)}")
            return []

# Example Usage
if __name__ == "__main__":
    predictor = PredictiveEngagementReports()
    supported_platforms = ["Facebook", "Instagram", "Twitter", "LinkedIn", "TikTok", "YouTube", "Pinterest", "Reddit"]

    date_range = {
        "start_date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
        "end_date": datetime.now().strftime("%Y-%m-%d"),
    }

    reports = predictor.run(supported_platforms, date_range)
    print("Generated Reports:", reports)

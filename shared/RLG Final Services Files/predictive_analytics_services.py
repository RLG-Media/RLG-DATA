import logging
from typing import List, Dict, Optional
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("predictive_analytics_services.log"),
        logging.StreamHandler()
    ]
)

class PredictiveAnalyticsService:
    """
    Service for predictive analytics to forecast trends and user behavior
    for RLG Data and RLG Fans.
    Supports predictive modeling across social media platforms.
    """

    def __init__(self):
        logging.info("Predictive Analytics Service initialized.")

    def preprocess_data(self, data: pd.DataFrame, target_column: str, feature_columns: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Preprocess data for predictive analytics.

        Args:
            data (pd.DataFrame): Input data.
            target_column (str): The name of the column to predict.
            feature_columns (List[str]): The names of columns to use as features.

        Returns:
            Dict[str, pd.DataFrame]: Preprocessed training and testing data.
        """
        try:
            X = data[feature_columns]
            y = data[target_column]

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            logging.info("Data preprocessing completed.")
            return {"X_train": X_train, "X_test": X_test, "y_train": y_train, "y_test": y_test}
        except Exception as e:
            logging.error(f"Failed to preprocess data: {e}")
            raise

    def build_and_train_model(self, X_train: pd.DataFrame, y_train: pd.Series) -> LinearRegression:
        """
        Build and train a predictive model.

        Args:
            X_train (pd.DataFrame): Training features.
            y_train (pd.Series): Training target variable.

        Returns:
            LinearRegression: Trained linear regression model.
        """
        try:
            model = LinearRegression()
            model.fit(X_train, y_train)
            logging.info("Model training completed.")
            return model
        except Exception as e:
            logging.error(f"Failed to train model: {e}")
            raise

    def evaluate_model(self, model: LinearRegression, X_test: pd.DataFrame, y_test: pd.Series) -> Dict:
        """
        Evaluate the performance of a predictive model.

        Args:
            model (LinearRegression): Trained model.
            X_test (pd.DataFrame): Testing features.
            y_test (pd.Series): Testing target variable.

        Returns:
            Dict: Evaluation metrics (e.g., RMSE, R-squared).
        """
        try:
            predictions = model.predict(X_test)
            rmse = mean_squared_error(y_test, predictions, squared=False)
            r2 = r2_score(y_test, predictions)

            metrics = {"RMSE": rmse, "R2": r2}
            logging.info(f"Model evaluation completed. Metrics: {metrics}")
            return metrics
        except Exception as e:
            logging.error(f"Failed to evaluate model: {e}")
            raise

    def forecast_trends(self, model: LinearRegression, future_data: pd.DataFrame) -> List[float]:
        """
        Use a trained model to forecast future trends.

        Args:
            model (LinearRegression): Trained model.
            future_data (pd.DataFrame): Data for future predictions.

        Returns:
            List[float]: Predicted values.
        """
        try:
            predictions = model.predict(future_data).tolist()
            logging.info("Trend forecasting completed.")
            return predictions
        except Exception as e:
            logging.error(f"Failed to forecast trends: {e}")
            raise

    def generate_insights(self, data: pd.DataFrame, platform: str) -> Dict:
        """
        Generate predictive insights for a specific platform.

        Args:
            data (pd.DataFrame): Historical data for analysis.
            platform (str): Name of the platform (e.g., "Twitter", "Facebook").

        Returns:
            Dict: Insights and recommendations.
        """
        try:
            insights = {
                "platform": platform,
                "average_engagement": data["engagement"].mean(),
                "top_performing_days": data.nlargest(3, "engagement")["date"].tolist()
            }
            logging.info(f"Generated insights for platform: {platform}")
            return insights
        except Exception as e:
            logging.error(f"Failed to generate insights for {platform}: {e}")
            raise

# Example Usage
if __name__ == "__main__":
    service = PredictiveAnalyticsService()

    # Example data
    example_data = pd.DataFrame({
        "date": pd.date_range(start="2025-01-01", periods=10),
        "engagement": [100, 150, 200, 250, 300, 350, 400, 450, 500, 550],
        "ad_spend": [50, 60, 70, 80, 90, 100, 110, 120, 130, 140]
    })

    preprocessed = service.preprocess_data(example_data, target_column="engagement", feature_columns=["ad_spend"])

    model = service.build_and_train_model(preprocessed["X_train"], preprocessed["y_train"])

    metrics = service.evaluate_model(model, preprocessed["X_test"], preprocessed["y_test"])
    print("Evaluation Metrics:", metrics)

    future_data = pd.DataFrame({"ad_spend": [150, 160, 170]})
    predictions = service.forecast_trends(model, future_data)
    print("Predicted Engagement:", predictions)

    insights = service.generate_insights(example_data, platform="Facebook")
    print("Platform Insights:", insights)

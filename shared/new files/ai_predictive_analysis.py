import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
import logging

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("ai_predictive_analysis.log"), logging.StreamHandler()]
)

class AIPredictiveAnalysis:
    def __init__(self, data):
        """
        Initialize the predictive analysis engine.
        :param data: DataFrame containing historical data for analysis.
        """
        self.data = data
        self.model = None
        self.scaler = StandardScaler()
        logging.info("AIPredictiveAnalysis initialized.")

    def preprocess_data(self, target_column, test_size=0.2, random_state=42):
        """
        Preprocess the data for training and testing.
        :param target_column: The column to predict.
        :param test_size: Proportion of the data to use for testing.
        :param random_state: Seed for reproducibility.
        :return: X_train, X_test, y_train, y_test
        """
        try:
            # Check for missing values and handle them
            self.data.fillna(self.data.median(), inplace=True)

            # Separate features and target
            X = self.data.drop(columns=[target_column])
            y = self.data[target_column]

            # Feature scaling
            X_scaled = self.scaler.fit_transform(X)

            # Split data into training and testing sets
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=test_size, random_state=random_state
            )
            logging.info("Data preprocessing completed.")
            return X_train, X_test, y_train, y_test
        except Exception as e:
            logging.error(f"Error during data preprocessing: {e}")
            return None, None, None, None

    def train_model(self, X_train, y_train):
        """
        Train a machine learning model.
        :param X_train: Training features.
        :param y_train: Training target.
        """
        try:
            self.model = RandomForestRegressor(random_state=42, n_estimators=100)
            self.model.fit(X_train, y_train)
            logging.info("Model training completed.")
        except Exception as e:
            logging.error(f"Error during model training: {e}")

    def evaluate_model(self, X_test, y_test):
        """
        Evaluate the model's performance.
        :param X_test: Testing features.
        :param y_test: Testing target.
        :return: Performance metrics (MAE, R2)
        """
        try:
            predictions = self.model.predict(X_test)
            mae = mean_absolute_error(y_test, predictions)
            r2 = r2_score(y_test, predictions)
            logging.info(f"Model evaluation completed. MAE: {mae}, R2: {r2}")
            return mae, r2
        except Exception as e:
            logging.error(f"Error during model evaluation: {e}")
            return None, None

    def predict_future(self, new_data):
        """
        Predict future outcomes based on new data.
        :param new_data: DataFrame containing new input data.
        :return: Predictions as a NumPy array.
        """
        try:
            new_data_scaled = self.scaler.transform(new_data)
            predictions = self.model.predict(new_data_scaled)
            logging.info("Future predictions generated.")
            return predictions
        except Exception as e:
            logging.error(f"Error during future predictions: {e}")
            return None

    def feature_importance(self):
        """
        Get the importance of features used in the model.
        :return: DataFrame containing feature names and their importance scores.
        """
        try:
            feature_importances = pd.DataFrame({
                "feature": self.data.columns.drop("target"),
                "importance": self.model.feature_importances_
            }).sort_values(by="importance", ascending=False)
            logging.info("Feature importance calculated.")
            return feature_importances
        except Exception as e:
            logging.error(f"Error during feature importance calculation: {e}")
            return None

# Example Usage
if __name__ == "__main__":
    # Example dataset
    historical_data = pd.DataFrame({
        "engagement_rate": [0.4, 0.5, 0.6, 0.7, 0.8],
        "content_length": [100, 150, 200, 250, 300],
        "hashtag_count": [3, 4, 5, 6, 7],
        "posting_time": [10, 12, 14, 16, 18],  # Hour of the day
        "views": [1000, 1500, 2000, 2500, 3000]
    })

    # Adding a target column (future engagement)
    historical_data["target"] = [0.45, 0.55, 0.65, 0.75, 0.85]

    # Initialize predictive analysis
    predictive_analysis = AIPredictiveAnalysis(historical_data)

    # Preprocess data
    X_train, X_test, y_train, y_test = predictive_analysis.preprocess_data("target")

    # Train model
    predictive_analysis.train_model(X_train, y_train)

    # Evaluate model
    mae, r2 = predictive_analysis.evaluate_model(X_test, y_test)
    print(f"Model Performance: MAE={mae}, R2={r2}")

    # Generate future predictions
    new_data = pd.DataFrame({
        "engagement_rate": [0.42, 0.52],
        "content_length": [120, 160],
        "hashtag_count": [4, 5],
        "posting_time": [11, 13],
        "views": [1100, 1700]
    })
    predictions = predictive_analysis.predict_future(new_data)
    print("Predictions for new data:", predictions)

    # Feature importance
    importance = predictive_analysis.feature_importance()
    print("Feature Importance:")
    print(importance)

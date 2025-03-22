import os
import json
import numpy as np
import pandas as pd
import datetime as dt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib

# Supported social media platforms
SOCIAL_MEDIA_PLATFORMS = [
    "Facebook", "Twitter", "Instagram", "LinkedIn", "TikTok",
    "Pinterest", "Reddit", "Snapchat", "YouTube", "Threads"
]

class SocialMediaEngagementForecaster:
    def __init__(self):
        self.data_file = "social_media_engagement_data.json"
        self.model_file = "engagement_forecast_model.pkl"
        self.model = None
        self.load_model()

    def load_data(self):
        """
        Loads engagement data from a JSON file.
        """
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as file:
                return json.load(file)
        return []

    def save_data(self, data):
        """
        Saves engagement data to a JSON file.
        """
        with open(self.data_file, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def preprocess_data(self, data):
        """
        Prepares data for machine learning model training.
        """
        df = pd.DataFrame(data)

        # Convert timestamps to numerical values
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["hour"] = df["timestamp"].dt.hour
        df["day_of_week"] = df["timestamp"].dt.dayofweek

        # One-hot encode social media platforms
        df = pd.get_dummies(df, columns=["platform"], prefix="platform")

        # Drop unnecessary columns
        df.drop(columns=["timestamp", "content"], inplace=True)

        return df

    def train_model(self):
        """
        Trains the engagement forecasting model.
        """
        data = self.load_data()
        if not data:
            print("⚠️ No engagement data available for training.")
            return

        df = self.preprocess_data(data)

        # Define features and target variable
        X = df.drop(columns=["engagement_score"])
        y = df["engagement_score"]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)

        # Evaluate the model
        predictions = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, predictions)
        print(f"✅ Model trained! Mean Absolute Error: {mae:.2f}")

        # Save the model
        joblib.dump(self.model, self.model_file)

    def load_model(self):
        """
        Loads the trained model from a file if available.
        """
        if os.path.exists(self.model_file):
            self.model = joblib.load(self.model_file)

    def forecast_engagement(self, platform, hour, day_of_week):
        """
        Predicts social media engagement for a given platform and time.
        """
        if self.model is None:
            print("⚠️ No trained model found. Training a new model...")
            self.train_model()

        if platform not in SOCIAL_MEDIA_PLATFORMS:
            raise ValueError(f"Unsupported platform: {platform}")

        # Prepare input data
        input_data = pd.DataFrame([{
            "hour": hour,
            "day_of_week": day_of_week,
            **{f"platform_{p}": 1 if p == platform else 0 for p in SOCIAL_MEDIA_PLATFORMS}
        }])

        prediction = self.model.predict(input_data)[0]
        return round(prediction, 2)

if __name__ == "__main__":
    forecaster = SocialMediaEngagementForecaster()
    forecaster.train_model()

    # Example forecast
    forecast = forecaster.forecast_engagement("Twitter", 15, 3)  # Wednesday at 3 PM
    print(f"📊 Predicted Engagement Score for Twitter at 3PM on Wednesday: {forecast}")

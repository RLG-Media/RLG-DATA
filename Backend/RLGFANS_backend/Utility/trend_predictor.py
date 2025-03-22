# trend_predictor.py

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split
import pandas as pd
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrendPredictor:
    def __init__(self, historical_data):
        """
        Initializes the TrendPredictor with historical data.
        :param historical_data: A DataFrame containing columns 'date', 'engagement', 'keywords'.
        """
        self.historical_data = historical_data
        self.model = None

    def preprocess_data(self):
        """
        Prepares the data for trend prediction, adding time-based features and converting text features.
        """
        logger.info("Preprocessing data for trend prediction...")
        self.historical_data['date'] = pd.to_datetime(self.historical_data['date'])
        self.historical_data['day_of_week'] = self.historical_data['date'].dt.dayofweek
        self.historical_data['day_of_month'] = self.historical_data['date'].dt.day
        self.historical_data['hour'] = self.historical_data['date'].dt.hour

        # Convert engagement into a numeric trend score (e.g., high = 3, medium = 2, low = 1)
        self.historical_data['engagement_level'] = self.historical_data['engagement'].apply(
            lambda x: 3 if x == "high" else (2 if x == "medium" else 1)
        )

        # Dummy encoding for keywords/topics
        keywords_dummies = self.historical_data['keywords'].str.get_dummies(sep=',')
        self.preprocessed_data = pd.concat([self.historical_data, keywords_dummies], axis=1)
        logger.info("Data preprocessing complete.")

    def train_model(self):
        """
        Trains a polynomial regression model on historical data to predict trends.
        """
        logger.info("Training trend prediction model...")
        X = self.preprocessed_data[['day_of_week', 'day_of_month', 'hour'] + list(self.preprocessed_data.columns[5:])]
        y = self.preprocessed_data['engagement_level']

        # Transform features for polynomial regression
        poly = PolynomialFeatures(degree=3)
        X_poly = poly.fit_transform(X)

        # Split data into training and test sets
        X_train, X_test, y_train, y_test = train_test_split(X_poly, y, test_size=0.2, random_state=42)

        # Train the model
        self.model = LinearRegression().fit(X_train, y_train)
        logger.info("Model training complete.")

        # Calculate and log model performance
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        logger.info(f"Training Score: {train_score:.2f}")
        logger.info(f"Test Score: {test_score:.2f}")

    def predict_trend(self, date, keywords):
        """
        Predicts the engagement trend based on date and keywords.
        :param date: The date and time for prediction.
        :param keywords: Keywords associated with the content.
        :return: Predicted engagement trend (high, medium, low).
        """
        logger.info("Predicting trend for provided date and keywords...")
        date = pd.to_datetime(date)
        day_of_week = date.dayofweek
        day_of_month = date.day
        hour = date.hour

        # Prepare dummy encoding for keywords
        keyword_features = {col: 0 for col in self.preprocessed_data.columns[5:]}
        for keyword in keywords.split(','):
            if keyword.strip() in keyword_features:
                keyword_features[keyword.strip()] = 1

        input_data = [day_of_week, day_of_month, hour] + list(keyword_features.values())

        # Transform features and make prediction
        poly = PolynomialFeatures(degree=3)
        input_data_poly = poly.fit_transform([input_data])
        engagement_level = self.model.predict(input_data_poly)

        # Convert engagement level to a qualitative trend
        if engagement_level >= 2.5:
            trend = "high"
        elif 1.5 <= engagement_level < 2.5:
            trend = "medium"
        else:
            trend = "low"
        logger.info(f"Predicted trend: {trend} with engagement level score of {engagement_level[0]:.2f}")
        return trend

    def upcoming_trends(self, days=7):
        """
        Predicts trends for the upcoming days based on previous data patterns.
        :param days: Number of days to forecast trends.
        :return: DataFrame with forecasted trends and engagement levels.
        """
        logger.info(f"Predicting trends for the next {days} days...")
        forecast_data = []

        for day in range(days):
            future_date = datetime.now() + timedelta(days=day)
            trend = self.predict_trend(future_date, keywords="")
            forecast_data.append({
                "date": future_date.strftime("%Y-%m-%d"),
                "predicted_trend": trend
            })

        trend_forecast_df = pd.DataFrame(forecast_data)
        logger.info("Upcoming trend predictions complete.")
        return trend_forecast_df

# Example Usage:
# data = pd.DataFrame({
#     'date': ['2023-10-01 12:00', '2023-10-02 13:00', '2023-10-03 14:00'],
#     'engagement': ['high', 'medium', 'low'],
#     'keywords': ['fashion, travel', 'food, wellness', 'sports, fitness']
# })
# predictor = TrendPredictor(data)
# predictor.preprocess_data()
# predictor.train_model()
# print(predictor.upcoming_trends())

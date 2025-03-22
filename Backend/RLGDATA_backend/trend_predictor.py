# trend_predictor.py

import logging
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrendPredictor:
    """
    A predictive analytics tool for identifying and forecasting content trends.
    """

    def __init__(self):
        """
        Initializes the TrendPredictor with default configurations.
        """
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.time_series_model = None

    def prepare_data(self, data, target_column):
        """
        Prepares data for predictive modeling by splitting into train and test sets.
        :param data: A pandas DataFrame containing the dataset.
        :param target_column: The name of the column to predict.
        :return: Training and testing datasets.
        """
        logger.info("Preparing data for trend prediction...")
        X = data.drop(columns=[target_column])
        y = data[target_column]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        logger.info(f"Data split: {len(X_train)} training samples, {len(X_test)} testing samples.")
        return X_train, X_test, y_train, y_test

    def train_model(self, X_train, y_train):
        """
        Trains the RandomForestRegressor on the given data.
        :param X_train: Features for training.
        :param y_train: Target values for training.
        """
        logger.info("Training the trend prediction model...")
        self.model.fit(X_train, y_train)
        logger.info("Model training complete.")

    def evaluate_model(self, X_test, y_test):
        """
        Evaluates the performance of the trained model.
        :param X_test: Features for testing.
        :param y_test: True target values for testing.
        :return: Mean Squared Error of the model.
        """
        logger.info("Evaluating the model...")
        predictions = self.model.predict(X_test)
        mse = mean_squared_error(y_test, predictions)
        logger.info(f"Model Mean Squared Error: {mse}")
        return mse

    def predict(self, new_data):
        """
        Predicts trends using the trained model.
        :param new_data: New data for prediction.
        :return: Predicted values.
        """
        logger.info("Making predictions with the trend prediction model...")
        predictions = self.model.predict(new_data)
        logger.info(f"Predictions: {predictions}")
        return predictions

    def time_series_forecast(self, data, column, forecast_periods=10):
        """
        Forecasts future trends using Exponential Smoothing.
        :param data: A pandas DataFrame containing the historical data.
        :param column: The name of the column to forecast.
        :param forecast_periods: Number of future periods to forecast.
        :return: A pandas DataFrame with historical and forecasted values.
        """
        logger.info("Performing time series forecasting...")
        self.time_series_model = ExponentialSmoothing(
            data[column],
            seasonal="add",
            seasonal_periods=12
        ).fit()

        forecast = self.time_series_model.forecast(forecast_periods)
        combined = pd.concat([data[column], forecast])
        logger.info("Time series forecasting complete.")
        return combined

    def plot_forecast(self, data, forecast):
        """
        Plots the historical data and forecasted trends.
        :param data: Historical data as a pandas Series.
        :param forecast: Forecasted data as a pandas Series.
        """
        logger.info("Plotting forecasted trends...")
        plt.figure(figsize=(12, 6))
        plt.plot(data, label="Historical Data")
        plt.plot(forecast, label="Forecast", linestyle="--")
        plt.title("Trend Forecasting")
        plt.xlabel("Time")
        plt.ylabel("Value")
        plt.legend()
        plt.show()


# Example Usage
if __name__ == "__main__":
    predictor = TrendPredictor()

    # Example dataset (replace with actual data)
    data = pd.DataFrame({
        "date": pd.date_range(start="2022-01-01", periods=100, freq="M"),
        "mentions": np.random.randint(50, 200, 100)
    })
    data.set_index("date", inplace=True)

    # Time Series Forecasting
    forecast = predictor.time_series_forecast(data, column="mentions", forecast_periods=12)
    predictor.plot_forecast(data["mentions"], forecast)

    # Predictive Modeling
    data["month"] = data.index.month
    data["year"] = data.index.year
    X_train, X_test, y_train, y_test = predictor.prepare_data(data, target_column="mentions")
    predictor.train_model(X_train, y_train)
    mse = predictor.evaluate_model(X_test, y_test)
    print(f"Model MSE: {mse}")

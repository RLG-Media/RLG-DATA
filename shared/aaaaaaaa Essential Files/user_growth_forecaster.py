import logging
from typing import List, Dict, Any
from datetime import datetime
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import matplotlib.pyplot as plt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/user_growth_forecaster.log"),
    ],
)

class UserGrowthForecaster:
    """
    Forecasts user growth trends for RLG Data and RLG Fans across different platforms.
    """

    def __init__(self):
        """
        Initialize the User Growth Forecaster.
        """
        logging.info("UserGrowthForecaster initialized.")
        self.models = {}

    def prepare_data(self, user_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Prepare user growth data for forecasting.

        Args:
            user_data: List of user data dictionaries with fields like 'date' and 'user_count'.

        Returns:
            A pandas DataFrame with formatted data.
        """
        try:
            logging.info("Preparing user growth data for forecasting...")
            df = pd.DataFrame(user_data)
            df['date'] = pd.to_datetime(df['date'])
            df.sort_values(by='date', inplace=True)
            df.set_index('date', inplace=True)
            logging.info("Data preparation completed.")
            return df
        except Exception as e:
            logging.error(f"Error preparing data: {e}")
            raise

    def train_forecasting_model(self, data: pd.DataFrame, method: str = "exponential_smoothing") -> Any:
        """
        Train a forecasting model on user growth data.

        Args:
            data: A pandas DataFrame with the user growth data.
            method: The forecasting method to use ('exponential_smoothing' or 'random_forest').

        Returns:
            A trained forecasting model.
        """
        try:
            logging.info(f"Training forecasting model using method: {method}...")
            if method == "exponential_smoothing":
                model = ExponentialSmoothing(data['user_count'], seasonal='add', seasonal_periods=12).fit()
            elif method == "random_forest":
                df = data.reset_index()
                df['timestamp'] = df['date'].apply(lambda x: x.timestamp())
                X = df[['timestamp']]
                y = df['user_count']
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                model = RandomForestRegressor(random_state=42)
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                mae = mean_absolute_error(y_test, y_pred)
                logging.info(f"Random Forest Model MAE: {mae}")
            else:
                raise ValueError("Invalid forecasting method.")
            self.models[method] = model
            logging.info(f"Model training completed using method: {method}.")
            return model
        except Exception as e:
            logging.error(f"Error training model: {e}")
            raise

    def forecast_user_growth(self, model: Any, periods: int, method: str = "exponential_smoothing") -> pd.DataFrame:
        """
        Forecast user growth using the trained model.

        Args:
            model: A trained forecasting model.
            periods: Number of periods to forecast.
            method: The forecasting method used.

        Returns:
            A pandas DataFrame with forecasted values.
        """
        try:
            logging.info(f"Forecasting user growth for {periods} periods using method: {method}...")
            if method == "exponential_smoothing":
                forecast = model.forecast(periods)
                forecast_df = pd.DataFrame({
                    'date': pd.date_range(start=model.data.endog.index[-1], periods=periods + 1, freq='M')[1:],
                    'forecast': forecast
                })
            elif method == "random_forest":
                start_date = model.X_train['timestamp'].max()
                future_dates = [start_date + (i * 30 * 24 * 60 * 60) for i in range(1, periods + 1)]
                forecast_values = model.predict(pd.DataFrame({'timestamp': future_dates}))
                forecast_df = pd.DataFrame({'date': future_dates, 'forecast': forecast_values})
            else:
                raise ValueError("Invalid forecasting method.")
            logging.info("Forecasting completed.")
            return forecast_df
        except Exception as e:
            logging.error(f"Error forecasting user growth: {e}")
            raise

    def visualize_forecast(self, actual: pd.DataFrame, forecast: pd.DataFrame) -> None:
        """
        Visualize actual and forecasted user growth.

        Args:
            actual: A pandas DataFrame with actual user growth data.
            forecast: A pandas DataFrame with forecasted user growth data.
        """
        try:
            logging.info("Visualizing user growth forecast...")
            plt.figure(figsize=(10, 6))
            plt.plot(actual.index, actual['user_count'], label="Actual", marker='o')
            plt.plot(forecast['date'], forecast['forecast'], label="Forecast", linestyle='--', marker='x')
            plt.xlabel("Date")
            plt.ylabel("User Count")
            plt.title("User Growth Forecast")
            plt.legend()
            plt.grid()
            plt.show()
            logging.info("Visualization completed.")
        except Exception as e:
            logging.error(f"Error visualizing forecast: {e}")
            raise


# Example Usage
if __name__ == "__main__":
    forecaster = UserGrowthForecaster()

    # Example user growth data
    user_data = [
        {"date": "2023-01-01", "user_count": 1000},
        {"date": "2023-02-01", "user_count": 1500},
        {"date": "2023-03-01", "user_count": 2000},
        {"date": "2023-04-01", "user_count": 2500},
        {"date": "2023-05-01", "user_count": 3000},
    ]

    # Prepare and process the data
    data_df = forecaster.prepare_data(user_data)

    # Train a model using exponential smoothing
    model = forecaster.train_forecasting_model(data_df, method="exponential_smoothing")

    # Forecast for the next 6 months
    forecast_df = forecaster.forecast_user_growth(model, periods=6)

    # Visualize the forecast
    forecaster.visualize_forecast(data_df, forecast_df)

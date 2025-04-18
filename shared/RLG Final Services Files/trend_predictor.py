import logging
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime

# Set up logging
logger = logging.getLogger("trend_predictor")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

class TrendPredictor:
    """
    Class for predicting trends and providing insights for content and engagement growth.
    
    This class offers multiple methods for trend analysis:
      - Preprocessing historical data (ensuring proper datetime format, sorting, filling missing values, and extracting time features).
      - Linear trend prediction using Linear Regression.
      - ARIMA-based forecasting for time series prediction.
      - Trend detection using rolling averages and standard deviations to classify periods as 'up', 'down', or 'stable'.
      - Generation of a comprehensive trend report combining these analyses.
    """
    
    def __init__(self, historical_data: pd.DataFrame):
        """
        Initializes the TrendPredictor with historical data.
        
        Args:
            historical_data (pd.DataFrame): DataFrame containing historical data with at least:
                - A 'date' column
                - A target column to be predicted (e.g., revenue, engagement, etc.)
        """
        self.historical_data = historical_data.copy()
        self.model = None

    def preprocess_data(self) -> bool:
        """
        Prepare data for trend prediction by:
          - Converting the 'date' column to datetime (if present).
          - Sorting the DataFrame by date.
          - Forward-filling missing values.
          - Extracting additional time-based features such as day_of_week and month.
        
        Returns:
            bool: True if preprocessing is successful, False otherwise.
        """
        logger.info("Preprocessing data for trend analysis...")
        try:
            if 'date' in self.historical_data.columns:
                self.historical_data['date'] = pd.to_datetime(self.historical_data['date'], errors='coerce')
                self.historical_data.sort_values(by='date', inplace=True)
            else:
                logger.warning("No 'date' column found in historical data.")

            self.historical_data.fillna(method='ffill', inplace=True)

            if 'date' in self.historical_data.columns:
                self.historical_data['day_of_week'] = self.historical_data['date'].dt.dayofweek
                self.historical_data['month'] = self.historical_data['date'].dt.month

            logger.info("Data preprocessing complete.")
            return True
        except Exception as e:
            logger.error(f"Error in data preprocessing: {e}")
            return False

    def linear_trend_prediction(self, target_column: str) -> List[float]:
        """
        Predict trends using a simple linear regression model.
        
        Args:
            target_column (str): The column name of the target metric to predict (e.g., "revenue").
        
        Returns:
            List[float]: A list of predicted values for the test set.
        """
        logger.info("Performing linear trend prediction...")
        try:
            # Ensure data is preprocessed
            if not self.preprocess_data():
                raise ValueError("Data preprocessing failed.")

            X = np.array(range(len(self.historical_data))).reshape(-1, 1)
            y = self.historical_data[target_column].values

            # Split data for model validation (this example uses a simple split)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            self.model = LinearRegression()
            self.model.fit(X_train, y_train)
            y_pred = self.model.predict(X_test)
            logger.info("Linear trend prediction completed successfully.")
            return y_pred.tolist()
        except Exception as e:
            logger.error(f"Error in linear trend prediction: {e}")
            return []

    def arima_forecasting(self, target_column: str, order: Tuple[int, int, int]=(5, 1, 0)) -> List[float]:
        """
        Predict future values using an ARIMA model for time series forecasting.
        
        Args:
            target_column (str): The column name of the target metric (e.g., "revenue").
            order (tuple): ARIMA model order (p, d, q). Default is (5, 1, 0).
        
        Returns:
            List[float]: Forecasted values for the next 10 data points.
        """
        logger.info("Performing ARIMA forecasting...")
        try:
            # Ensure target column exists and data is preprocessed
            if not self.preprocess_data():
                raise ValueError("Data preprocessing failed.")

            series = self.historical_data[target_column]
            model = ARIMA(series, order=order)
            fitted_model = model.fit()
            forecast = fitted_model.forecast(steps=10)
            logger.info("ARIMA forecasting completed successfully.")
            return forecast.tolist()
        except Exception as e:
            logger.error(f"Error in ARIMA forecasting: {e}")
            return []

    def detect_trends(self, target_column: str, sensitivity: float=1.5) -> pd.DataFrame:
        """
        Detect trends by identifying periods of significant change in the target data.
        
        Uses a rolling window to calculate the mean and standard deviation,
        then classifies each period as 'up', 'down', or 'stable' based on a sensitivity threshold.
        
        Args:
            target_column (str): The column name of the target metric.
            sensitivity (float): Multiplier for the rolling standard deviation to define thresholds.
        
        Returns:
            pd.DataFrame: A DataFrame with columns 'date', target_column, and 'trend'.
        """
        logger.info("Detecting significant trends...")
        try:
            if not self.preprocess_data():
                raise ValueError("Data preprocessing failed.")

            self.historical_data['rolling_mean'] = self.historical_data[target_column].rolling(window=7).mean()
            self.historical_data['rolling_std'] = self.historical_data[target_column].rolling(window=7).std()
            threshold = sensitivity * self.historical_data['rolling_std']
            self.historical_data['trend'] = np.where(
                self.historical_data[target_column] > self.historical_data['rolling_mean'] + threshold,
                'up',
                np.where(
                    self.historical_data[target_column] < self.historical_data['rolling_mean'] - threshold,
                    'down',
                    'stable'
                )
            )
            trends = self.historical_data[['date', target_column, 'trend']].dropna()
            logger.info("Trend detection completed successfully.")
            return trends
        except Exception as e:
            logger.error(f"Error in trend detection: {e}")
            return pd.DataFrame()

    def generate_trend_report(self, target_column: str) -> Dict[str, Any]:
        """
        Generate a comprehensive trend analysis report including linear predictions,
        ARIMA forecast, and detected trends.
        
        Args:
            target_column (str): The target metric column to analyze (e.g., "revenue").
        
        Returns:
            Dict[str, Any]: A dictionary containing the trend report.
        """
        logger.info("Generating trend report...")
        try:
            self.preprocess_data()
            linear_predictions = self.linear_trend_prediction(target_column)
            arima_forecast = self.arima_forecasting(target_column)
            detected_trends = self.detect_trends(target_column)
            report = {
                "timestamp": datetime.now().isoformat(),
                "linear_predictions": linear_predictions,
                "arima_forecast": arima_forecast,
                "detected_trends": detected_trends.to_dict(orient='records')
            }
            logger.info("Trend report generated successfully.")
            return report
        except Exception as e:
            logger.error(f"Error generating trend report: {e}")
            return {"error": "Failed to generate report"}

# -------------------------------
# Additional Recommendations:
# -------------------------------
# 1. For more granular regional analysis, consider incorporating additional features such as location metadata.
# 2. Improve the ARIMA forecasting by fine-tuning the model order and incorporating seasonal adjustments if needed.
# 3. Implement caching or asynchronous processing for large datasets.
# 4. Consider integrating additional evaluation metrics (e.g., RMSE) for model validation.
# 5. Ensure proper unit testing across various scenarios and datasets.

# -------------------------------
# Standalone Testing Example:
# -------------------------------
if __name__ == "__main__":
    # Create sample historical data for demonstration.
    sample_data = pd.DataFrame({
        "date": pd.date_range(start="2025-01-01", periods=30, freq="D"),
        "revenue": np.random.randint(4000, 6000, size=30)
    })

    predictor = TrendPredictor(sample_data)
    
    # Test preprocessing
    if predictor.preprocess_data():
        print("Data preprocessed successfully.")

    # Test linear trend prediction
    linear_pred = predictor.linear_trend_prediction("revenue")
    print("Linear Predictions:", linear_pred)

    # Test ARIMA forecasting
    arima_forecast = predictor.arima_forecasting("revenue")
    print("ARIMA Forecast:", arima_forecast)

    # Test trend detection
    trends_df = predictor.detect_trends("revenue")
    print("Detected Trends:")
    print(trends_df)

    # Test generating a comprehensive trend report
    report = predictor.generate_trend_report("revenue")
    print("Trend Report:")
    print(report)

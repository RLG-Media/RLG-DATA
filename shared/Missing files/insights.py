import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import statsmodels.api as sm
from typing import Dict, Any, Optional


class InsightsEngine:
    def __init__(self, data: pd.DataFrame):
        """
        Initializes the InsightsEngine with the provided dataset.
        
        Args:
            data (pd.DataFrame): DataFrame containing historical data for analysis.
        """
        self.data = data

    def generate_summary_statistics(self) -> Dict[str, Any]:
        """
        Generates summary statistics for the dataset.

        Returns:
            Dict[str, Any]: Summary statistics including mean, median, std, and correlation.
        """
        summary_stats = {
            "mean": self.data.mean().to_dict(),
            "median": self.data.median().to_dict(),
            "std": self.data.std().to_dict(),
            "correlation": self.data.corr().to_dict(),
        }
        return summary_stats

    def perform_regression_analysis(self, target: str, features: Optional[list] = None) -> Dict[str, Any]:
        """
        Performs regression analysis using Statsmodels for interpretability.

        Args:
            target (str): The target column for the regression model.
            features (Optional[list]): List of feature columns to include in the model. If None, uses all features.

        Returns:
            Dict[str, Any]: Regression summary and coefficients.
        """
        if features is None:
            features = [col for col in self.data.columns if col != target]
        
        X = self.data[features]
        y = self.data[target]

        # Add constant for intercept
        X = sm.add_constant(X)

        model = sm.OLS(y, X).fit()
        regression_results = {
            "summary": model.summary().as_text(),
            "coefficients": model.params.to_dict(),
            "p_values": model.pvalues.to_dict(),
        }
        return regression_results

    def train_predictive_model(
        self,
        target: str,
        features: Optional[list] = None,
        model_type: str = "random_forest",
    ) -> Dict[str, Any]:
        """
        Trains a predictive model and evaluates its performance.

        Args:
            target (str): The target column for predictions.
            features (Optional[list]): List of feature columns. If None, uses all features.
            model_type (str): The type of model to train ("linear" or "random_forest").

        Returns:
            Dict[str, Any]: Model performance metrics and feature importances.
        """
        if features is None:
            features = [col for col in self.data.columns if col != target]

        X = self.data[features]
        y = self.data[target]

        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Standardize data
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

        # Select model
        if model_type == "linear":
            model = LinearRegression()
        elif model_type == "random_forest":
            model = RandomForestRegressor(random_state=42)
        else:
            raise ValueError("Invalid model_type. Choose 'linear' or 'random_forest'.")

        # Train the model
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        # Evaluate performance
        performance = {
            "mean_absolute_error": mean_absolute_error(y_test, y_pred),
            "mean_squared_error": mean_squared_error(y_test, y_pred),
            "r2_score": r2_score(y_test, y_pred),
        }

        # Feature importances (only for Random Forest)
        feature_importances = {}
        if model_type == "random_forest":
            feature_importances = {
                feature: importance for feature, importance in zip(features, model.feature_importances_)
            }

        return {"performance": performance, "feature_importances": feature_importances}

    def detect_anomalies(self, column: str, z_threshold: float = 3.0) -> pd.DataFrame:
        """
        Detects anomalies in the specified column using Z-scores.

        Args:
            column (str): The column to analyze for anomalies.
            z_threshold (float): The Z-score threshold for identifying anomalies.

        Returns:
            pd.DataFrame: DataFrame containing the anomalies.
        """
        mean_val = self.data[column].mean()
        std_dev = self.data[column].std()

        self.data["z_score"] = (self.data[column] - mean_val) / std_dev
        anomalies = self.data[np.abs(self.data["z_score"]) > z_threshold]
        return anomalies.drop(columns=["z_score"])

    def generate_trend_analysis(self, column: str, period: str = "M") -> pd.DataFrame:
        """
        Generates a trend analysis for a time-based column.

        Args:
            column (str): The column to analyze for trends.
            period (str): Resampling period (e.g., "M" for monthly, "W" for weekly).

        Returns:
            pd.DataFrame: DataFrame containing the trend analysis.
        """
        trend_data = self.data.copy()
        trend_data["timestamp"] = pd.to_datetime(trend_data["timestamp"])
        trend_data.set_index("timestamp", inplace=True)
        trend_trends = trend_data[column].resample(period).mean().reset_index()
        return trend_trends


# Example Usage
if __name__ == "__main__":
    # Example Data
    data = pd.DataFrame({
        "timestamp": pd.date_range(start="2023-01-01", periods=100, freq="D"),
        "feature_1": np.random.rand(100),
        "feature_2": np.random.rand(100) * 10,
        "target": np.random.rand(100) * 5,
    })

    insights = InsightsEngine(data)

    print("Summary Statistics:")
    print(insights.generate_summary_statistics())

    print("\nRegression Analysis:")
    print(insights.perform_regression_analysis(target="target"))

    print("\nPredictive Model (Random Forest):")
    print(insights.train_predictive_model(target="target"))

    print("\nAnomalies Detected:")
    print(insights.detect_anomalies(column="target"))

    print("\nTrend Analysis:")
    print(insights.generate_trend_analysis(column="target"))

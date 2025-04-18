import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_squared_error, classification_report, confusion_matrix
from sklearn.cluster import KMeans
from typing import Dict, List, Any

# Logging utility
def log_message(message: str):
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

class AnalyticsEngine:
    def __init__(self):
        """Initialize the AnalyticsEngine class."""
        log_message("AnalyticsEngine initialized.")

    def descriptive_statistics(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate descriptive statistics for the dataset.

        Args:
            data: Input DataFrame.

        Returns:
            DataFrame with descriptive statistics.
        """
        log_message("Generating descriptive statistics.")
        return data.describe()

    def correlation_analysis(self, data: pd.DataFrame, target_column: str = None) -> pd.DataFrame:
        """
        Perform correlation analysis on the dataset.

        Args:
            data: Input DataFrame.
            target_column: Specific column to analyze correlation with (optional).

        Returns:
            DataFrame with correlation coefficients.
        """
        log_message("Performing correlation analysis.")
        if target_column:
            return data.corr()[[target_column]].sort_values(by=target_column, ascending=False)
        return data.corr()

    def visualize_data_distribution(self, data: pd.DataFrame, column: str):
        """
        Visualize the distribution of a single column.

        Args:
            data: Input DataFrame.
            column: Column to visualize.
        """
        log_message(f"Visualizing data distribution for {column}.")
        plt.figure(figsize=(10, 6))
        sns.histplot(data[column], kde=True, bins=30)
        plt.title(f"Distribution of {column}")
        plt.xlabel(column)
        plt.ylabel("Frequency")
        plt.show()

    def train_test_split(self, data: pd.DataFrame, target_column: str, test_size: float = 0.2):
        """
        Split data into training and testing sets.

        Args:
            data: Input DataFrame.
            target_column: Column to be predicted.
            test_size: Proportion of the dataset to include in the test split.

        Returns:
            Tuple of train/test features and labels.
        """
        log_message("Splitting data into training and testing sets.")
        X = data.drop(columns=[target_column])
        y = data[target_column]
        return train_test_split(X, y, test_size=test_size, random_state=42)

    def train_model(self, X_train: pd.DataFrame, y_train: pd.Series, model_type: str = "classification") -> Any:
        """
        Train a machine learning model.

        Args:
            X_train: Training features.
            y_train: Training labels.
            model_type: Type of model to train - 'classification' or 'regression'.

        Returns:
            Trained model.
        """
        log_message(f"Training {model_type} model.")
        if model_type == "classification":
            model = RandomForestClassifier(random_state=42)
        else:
            model = RandomForestRegressor(random_state=42)
        model.fit(X_train, y_train)
        return model

    def evaluate_model(self, model: Any, X_test: pd.DataFrame, y_test: pd.Series, model_type: str = "classification"):
        """
        Evaluate a trained model.

        Args:
            model: Trained model.
            X_test: Testing features.
            y_test: True labels for testing data.
            model_type: Type of model - 'classification' or 'regression'.

        Returns:
            Dictionary with evaluation metrics.
        """
        log_message(f"Evaluating {model_type} model.")
        y_pred = model.predict(X_test)
        if model_type == "classification":
            accuracy = accuracy_score(y_test, y_pred)
            report = classification_report(y_test, y_pred, output_dict=True)
            cm = confusion_matrix(y_test, y_pred)
            return {"accuracy": accuracy, "classification_report": report, "confusion_matrix": cm}
        else:
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            return {"mse": mse, "rmse": rmse}

    def cluster_data(self, data: pd.DataFrame, n_clusters: int = 3) -> pd.DataFrame:
        """
        Perform KMeans clustering on the dataset.

        Args:
            data: Input DataFrame.
            n_clusters: Number of clusters.

        Returns:
            DataFrame with cluster labels.
        """
        log_message("Performing KMeans clustering.")
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        data['cluster'] = kmeans.fit_predict(data)
        return data

    def feature_importance(self, model: Any, feature_names: List[str]) -> pd.DataFrame:
        """
        Extract and display feature importance from a trained model.

        Args:
            model: Trained RandomForest model.
            feature_names: List of feature names.

        Returns:
            DataFrame with feature importances.
        """
        log_message("Extracting feature importances.")
        importances = model.feature_importances_
        importance_df = pd.DataFrame({"Feature": feature_names, "Importance": importances})
        importance_df = importance_df.sort_values(by="Importance", ascending=False)
        return importance_df

# Main execution
if __name__ == "__main__":
    engine = AnalyticsEngine()

    # Example DataFrame
    df = pd.DataFrame({
        "Feature1": np.random.rand(100),
        "Feature2": np.random.rand(100),
        "Feature3": np.random.randint(0, 2, 100),
        "Target": np.random.randint(0, 2, 100)
    })

    # Descriptive statistics
    stats = engine.descriptive_statistics(df)
    print(stats)

    # Correlation analysis
    correlation = engine.correlation_analysis(df, target_column="Target")
    print(correlation)

    # Train-test split
    X_train, X_test, y_train, y_test = engine.train_test_split(df, target_column="Target")

    # Train model
    model = engine.train_model(X_train, y_train, model_type="classification")

    # Evaluate model
    metrics = engine.evaluate_model(model, X_test, y_test, model_type="classification")
    print(metrics)

    # Clustering
    clustered_data = engine.cluster_data(df.drop(columns=["Target"]), n_clusters=3)
    print(clustered_data.head())

    # Feature importance
    importance_df = engine.feature_importance(model, feature_names=X_train.columns.tolist())
    print(importance_df)

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from typing import Optional, Dict, Any
import joblib
import os

# Constants for model storage
MODEL_DIR = "models/"
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)


class MachineLearningEngine:
    def __init__(self):
        """
        Initializes the MachineLearningEngine.
        """
        self.models = {}

    @staticmethod
    def preprocess_data(
        data: pd.DataFrame, features: list, target: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Prepares the data for ML models by scaling features and encoding categorical data.

        Args:
            data (pd.DataFrame): The input dataset.
            features (list): The list of feature column names.
            target (Optional[str]): The target column for supervised learning.

        Returns:
            Dict[str, Any]: A dictionary containing preprocessed data and optional target values.
        """
        scaler = StandardScaler()
        X = data[features]
        X_scaled = scaler.fit_transform(X)

        if target:
            y = data[target]
            if y.dtype == 'object':
                y = LabelEncoder().fit_transform(y)
            return {"X": X_scaled, "y": y}
        return {"X": X_scaled}

    def train_audience_segmentation_model(self, data: pd.DataFrame, features: list, n_clusters: int = 5) -> Dict[str, Any]:
        """
        Trains a KMeans clustering model for audience segmentation.

        Args:
            data (pd.DataFrame): The input dataset.
            features (list): List of feature columns.
            n_clusters (int): Number of clusters for segmentation.

        Returns:
            Dict[str, Any]: Information about the trained model and cluster centers.
        """
        preprocessed = self.preprocess_data(data, features)
        model = KMeans(n_clusters=n_clusters, random_state=42)
        data["cluster"] = model.fit_predict(preprocessed["X"])

        # Save the model
        model_path = os.path.join(MODEL_DIR, "audience_segmentation_model.pkl")
        joblib.dump(model, model_path)
        self.models["audience_segmentation"] = model

        return {"model_path": model_path, "cluster_centers": model.cluster_centers_}

    def train_trend_analysis_model(self, data: pd.DataFrame, features: list, target: str) -> Dict[str, Any]:
        """
        Trains a Gradient Boosting Regressor for trend analysis.

        Args:
            data (pd.DataFrame): The input dataset.
            features (list): List of feature columns.
            target (str): The target column for predictions.

        Returns:
            Dict[str, Any]: Model performance and feature importances.
        """
        preprocessed = self.preprocess_data(data, features, target)
        X_train, X_test, y_train, y_test = train_test_split(preprocessed["X"], preprocessed["y"], test_size=0.2, random_state=42)

        model = GradientBoostingRegressor(random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        # Evaluate performance
        performance = {
            "mean_squared_error": mean_squared_error(y_test, y_pred),
            "r2_score": r2_score(y_test, y_pred),
        }

        # Save the model
        model_path = os.path.join(MODEL_DIR, "trend_analysis_model.pkl")
        joblib.dump(model, model_path)
        self.models["trend_analysis"] = model

        return {"model_path": model_path, "performance": performance, "feature_importances": model.feature_importances_}

    def train_supervised_model(
        self, data: pd.DataFrame, features: list, target: str, model_type: str = "random_forest"
    ) -> Dict[str, Any]:
        """
        Trains a supervised learning model.

        Args:
            data (pd.DataFrame): The input dataset.
            features (list): List of feature columns.
            target (str): The target column for predictions.
            model_type (str): The type of supervised model to use ("random_forest" or "gradient_boosting").

        Returns:
            Dict[str, Any]: Model performance and other details.
        """
        preprocessed = self.preprocess_data(data, features, target)
        X_train, X_test, y_train, y_test = train_test_split(preprocessed["X"], preprocessed["y"], test_size=0.2, random_state=42)

        if model_type == "random_forest":
            model = RandomForestClassifier(random_state=42)
        elif model_type == "gradient_boosting":
            model = GradientBoostingRegressor(random_state=42)
        else:
            raise ValueError("Invalid model_type. Choose 'random_forest' or 'gradient_boosting'.")

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        # Evaluate performance
        if model_type == "random_forest":
            performance = classification_report(y_test, y_pred, output_dict=True)
        else:
            performance = {
                "mean_squared_error": mean_squared_error(y_test, y_pred),
                "r2_score": r2_score(y_test, y_pred),
            }

        # Save the model
        model_name = f"{model_type}_model.pkl"
        model_path = os.path.join(MODEL_DIR, model_name)
        joblib.dump(model, model_path)
        self.models[model_type] = model

        return {"model_path": model_path, "performance": performance}

    def predict(self, model_name: str, data: pd.DataFrame) -> np.ndarray:
        """
        Uses a trained model to make predictions.

        Args:
            model_name (str): Name of the model to use for predictions.
            data (pd.DataFrame): Preprocessed data for prediction.

        Returns:
            np.ndarray: Predictions made by the model.
        """
        if model_name not in self.models:
            model_path = os.path.join(MODEL_DIR, f"{model_name}.pkl")
            if os.path.exists(model_path):
                self.models[model_name] = joblib.load(model_path)
            else:
                raise ValueError(f"Model {model_name} not found.")

        model = self.models[model_name]
        return model.predict(data)

    def update_model(self, model_name: str, new_data: pd.DataFrame, features: list, target: Optional[str] = None):
        """
        Updates a model with new data for continuous learning.

        Args:
            model_name (str): Name of the model to update.
            new_data (pd.DataFrame): New data to train on.
            features (list): List of feature columns.
            target (Optional[str]): The target column for supervised models.
        """
        model = self.models.get(model_name)
        if not model:
            raise ValueError(f"Model {model_name} not found. Train the model first.")

        preprocessed = self.preprocess_data(new_data, features, target)
        X = preprocessed["X"]
        y = preprocessed["y"] if "y" in preprocessed else None

        if hasattr(model, "partial_fit"):
            model.partial_fit(X, y)
        else:
            raise ValueError(f"The model {model_name} does not support incremental learning.")


# Example Usage
if __name__ == "__main__":
    # Example dataset
    data = pd.DataFrame({
        "feature_1": np.random.rand(100),
        "feature_2": np.random.rand(100) * 10,
        "audience_size": np.random.randint(50, 500, size=100),
        "engagement_rate": np.random.rand(100) * 0.1,
        "trend_score": np.random.rand(100) * 5,
    })

    engine = MachineLearningEngine()

    print("Audience Segmentation:")
    print(engine.train_audience_segmentation_model(data, features=["feature_1", "feature_2"]))

    print("\nTrend Analysis:")
    print(engine.train_trend_analysis_model(data, features=["feature_1", "feature_2"], target="trend_score"))

    print("\nSupervised Learning (Random Forest):")
    print(engine.train_supervised_model(data, features=["feature_1", "feature_2"], target="audience_size"))

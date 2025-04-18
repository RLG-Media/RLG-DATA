import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.pipeline import Pipeline
import joblib


class ChurnPredictionModel:
    """
    A class for building, training, and evaluating a churn prediction model.
    """

    def __init__(self, model_path: str = "models/churn_model.pkl"):
        """
        Initialize the ChurnPredictionModel.

        Args:
            model_path: Path to save or load the trained model.
        """
        self.model_path = model_path
        self.model = None

    def preprocess_data(self, data: pd.DataFrame, target_column: str) -> tuple:
        """
        Preprocess the dataset for training and evaluation.

        Args:
            data: Input dataframe containing features and target.
            target_column: Name of the target column indicating churn.

        Returns:
            Tuple containing preprocessed X (features) and y (target).
        """
        # Handle missing values
        data.fillna(data.median(), inplace=True)

        # Encode categorical variables
        label_encoders = {}
        for column in data.select_dtypes(include=["object"]).columns:
            if column != target_column:
                encoder = LabelEncoder()
                data[column] = encoder.fit_transform(data[column])
                label_encoders[column] = encoder

        # Separate features and target
        X = data.drop(columns=[target_column])
        y = data[target_column]

        # Encode target variable
        target_encoder = LabelEncoder()
        y = target_encoder.fit_transform(y)

        return X, y, label_encoders, target_encoder

    def train_model(self, X: pd.DataFrame, y: pd.Series) -> None:
        """
        Train the churn prediction model.

        Args:
            X: Features dataframe.
            y: Target series.
        """
        # Split data into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Define the pipeline
        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight="balanced"
            )),
        ])

        # Train the model
        pipeline.fit(X_train, y_train)
        self.model = pipeline

        # Evaluate the model
        self.evaluate_model(X_test, y_test)

        # Save the trained model
        self.save_model()

    def evaluate_model(self, X_test: pd.DataFrame, y_test: pd.Series) -> None:
        """
        Evaluate the trained model.

        Args:
            X_test: Test features dataframe.
            y_test: Test target series.
        """
        if not self.model:
            raise ValueError("Model is not trained yet. Train the model before evaluation.")

        y_pred = self.model.predict(X_test)
        y_prob = self.model.predict_proba(X_test)[:, 1]

        print("Confusion Matrix:")
        print(confusion_matrix(y_test, y_pred))

        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))

        print("\nROC-AUC Score:")
        print(roc_auc_score(y_test, y_prob))

    def save_model(self) -> None:
        """
        Save the trained model to disk.
        """
        if not self.model:
            raise ValueError("Model is not trained yet. Train the model before saving.")
        joblib.dump(self.model, self.model_path)
        print(f"Model saved to {self.model_path}")

    def load_model(self) -> None:
        """
        Load a trained model from disk.
        """
        self.model = joblib.load(self.model_path)
        print(f"Model loaded from {self.model_path}")

    def predict(self, input_data: pd.DataFrame) -> np.ndarray:
        """
        Make predictions using the trained model.

        Args:
            input_data: Input dataframe with the same structure as training data.

        Returns:
            Predictions as a numpy array.
        """
        if not self.model:
            raise ValueError("Model is not trained yet. Train or load the model before prediction.")

        return self.model.predict(input_data)


# Example Usage
if __name__ == "__main__":
    # Load your dataset
    df = pd.read_csv("data/customer_data.csv")

    # Initialize the churn prediction model
    churn_model = ChurnPredictionModel()

    # Preprocess the data
    X, y, label_encoders, target_encoder = churn_model.preprocess_data(df, target_column="churn")

    # Train the model
    churn_model.train_model(X, y)

    # Save the model
    churn_model.save_model()

    # Predict on new data (example)
    sample_data = X.iloc[:5]
    predictions = churn_model.predict(sample_data)
    decoded_predictions = target_encoder.inverse_transform(predictions)

    print("Sample Predictions:")
    print(decoded_predictions)

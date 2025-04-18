# model_training.py

import os
import pickle
import logging
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.externals import joblib
from your_project_name.feature_engineering import generate_features
from your_project_name.config import MODEL_TRAINING_CONFIG
from your_project_name.data_ingestion import load_data
from your_project_name.error_handling import handle_error

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directory to save trained models
MODEL_PATH = MODEL_TRAINING_CONFIG['MODEL_PATH']
MODEL_FILE = 'trained_model.pkl'


def load_and_prepare_data():
    """
    Loads and prepares the data for model training.
    
    Returns:
        X_train (array-like): Features for training.
        y_train (array-like): Target labels for training.
    """
    try:
        # Load the raw data (this can be from a database, CSV, or any other source)
        logger.info("Loading and preparing data for training...")
        raw_data = load_data()  # Assume `load_data` fetches data in required format
        
        # Generate features using the feature engineering module
        features, target = generate_features(raw_data)  # Assume this function returns X, y
        
        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)
        
        logger.info(f"Data loaded and split into training and testing sets. Training size: {len(X_train)}, Testing size: {len(X_test)}")
        return X_train, X_test, y_train, y_test
    
    except Exception as e:
        handle_error(e)
        return None, None, None, None


def train_model(X_train, y_train):
    """
    Trains a machine learning model using the training data.
    
    Args:
        X_train (array-like): Features for training.
        y_train (array-like): Target labels for training.
    
    Returns:
        model: The trained machine learning model.
    """
    try:
        # Standardize the data (important for many machine learning algorithms)
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        
        # Initialize the model (Random Forest as an example, can be replaced with other models)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        
        # Train the model
        logger.info("Training the model...")
        model.fit(X_train_scaled, y_train)
        
        logger.info("Model trained successfully.")
        return model, scaler
    
    except Exception as e:
        handle_error(e)
        return None, None


def evaluate_model(model, scaler, X_test, y_test):
    """
    Evaluates the trained model on the test data.
    
    Args:
        model: The trained model to evaluate.
        scaler: The scaler used during training for data preprocessing.
        X_test (array-like): Features for testing.
        y_test (array-like): Target labels for testing.
    
    Returns:
        dict: Model evaluation metrics (accuracy, classification report).
    """
    try:
        # Scale the test data using the same scaler as the training data
        X_test_scaled = scaler.transform(X_test)
        
        # Make predictions using the trained model
        predictions = model.predict(X_test_scaled)
        
        # Evaluate the model
        accuracy = accuracy_score(y_test, predictions)
        class_report = classification_report(y_test, predictions)
        
        logger.info(f"Model Accuracy: {accuracy}")
        logger.info(f"Classification Report: \n{class_report}")
        
        return {
            'accuracy': accuracy,
            'classification_report': class_report
        }
    
    except Exception as e:
        handle_error(e)
        return None


def save_model(model, scaler):
    """
    Saves the trained model and scaler to disk.
    
    Args:
        model: The trained machine learning model.
        scaler: The scaler used for feature scaling.
    """
    try:
        # Save the trained model and scaler
        model_file_path = os.path.join(MODEL_PATH, MODEL_FILE)
        joblib.dump(model, model_file_path)
        
        # Save the scaler to be used during prediction
        scaler_file_path = os.path.join(MODEL_PATH, 'scaler.pkl')
        joblib.dump(scaler, scaler_file_path)
        
        logger.info(f"Model and scaler saved to {MODEL_PATH}.")
    
    except Exception as e:
        handle_error(e)


def retrain_model(new_data):
    """
    Retrains the model with new data.

    Args:
        new_data (dict): New training data (features and labels).
    
    Returns:
        model: The retrained machine learning model.
    """
    try:
        logger.info("Retraining model with new data...")
        
        # Extract features and target from new data
        features = new_data.get('features', [])
        target = new_data.get('target', [])
        
        # Split the new data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)
        
        # Train the model with the new data
        model, scaler = train_model(X_train, y_train)
        
        # Evaluate the retrained model
        evaluation_metrics = evaluate_model(model, scaler, X_test, y_test)
        
        # Save the retrained model and scaler
        save_model(model, scaler)
        
        return {
            'model': model,
            'evaluation_metrics': evaluation_metrics
        }
    
    except Exception as e:
        handle_error(e)
        return None


def load_trained_model():
    """
    Loads the most recently trained model from disk.
    
    Returns:
        model: The trained machine learning model.
        scaler: The scaler used for preprocessing.
    """
    try:
        model_file_path = os.path.join(MODEL_PATH, MODEL_FILE)
        scaler_file_path = os.path.join(MODEL_PATH, 'scaler.pkl')
        
        if os.path.exists(model_file_path) and os.path.exists(scaler_file_path):
            # Load the trained model and scaler
            model = joblib.load(model_file_path)
            scaler = joblib.load(scaler_file_path)
            logger.info("Loaded trained model and scaler.")
            return model, scaler
        else:
            raise FileNotFoundError("Trained model or scaler not found.")
    
    except Exception as e:
        handle_error(e)
        return None, None


def train_and_evaluate():
    """
    A wrapper function to load data, train, evaluate, and save the model.
    """
    try:
        # Load and prepare data
        X_train, X_test, y_train, y_test = load_and_prepare_data()
        
        if X_train is None or X_test is None:
            raise ValueError("Data preparation failed.")
        
        # Train the model
        model, scaler = train_model(X_train, y_train)
        
        # Evaluate the model
        evaluation_metrics = evaluate_model(model, scaler, X_test, y_test)
        
        # Save the model
        save_model(model, scaler)
        
        return evaluation_metrics
    
    except Exception as e:
        handle_error(e)
        return None


if __name__ == "__main__":
    # Example usage of training, evaluation, and saving the model
    logger.info("Starting model training...")
    metrics = train_and_evaluate()
    
    if metrics:
        logger.info(f"Model training and evaluation completed. Metrics: {metrics}")
    else:
        logger.error("Model training failed.")

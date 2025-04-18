# model_deployment.py

import os
import pickle
import logging
from sklearn.externals import joblib
from flask import Flask, request, jsonify
from your_project_name.config import MODEL_DEPLOYMENT_CONFIG
from your_project_name.feature_engineering import generate_features
from your_project_name.model_training import load_trained_model, retrain_model
from your_project_name.error_handling import handle_error
from your_project_name.analytics_dashboard import update_dashboard_with_model_metrics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app for serving the model
app = Flask(__name__)

# Model variables
MODEL_PATH = MODEL_DEPLOYMENT_CONFIG['MODEL_PATH']
CURRENT_MODEL_FILE = 'current_model.pkl'
MODEL_VERSION_FILE = 'model_version.txt'


def load_model():
    """
    Load the latest trained model from the model directory.

    Returns:
        model: The loaded model object.
    """
    try:
        model_file_path = os.path.join(MODEL_PATH, CURRENT_MODEL_FILE)

        if os.path.exists(model_file_path):
            logger.info(f"Loading model from {model_file_path}")
            model = joblib.load(model_file_path)
            logger.info("Model loaded successfully.")
            return model
        else:
            raise FileNotFoundError(f"Model file {CURRENT_MODEL_FILE} not found at {MODEL_PATH}.")
    
    except Exception as e:
        handle_error(e)
        return None


def deploy_model(model):
    """
    Deploy the trained model by saving it to the appropriate directory.

    Args:
        model: The trained model object to be deployed.
    """
    try:
        model_file_path = os.path.join(MODEL_PATH, CURRENT_MODEL_FILE)
        joblib.dump(model, model_file_path)
        logger.info(f"Model deployed and saved to {model_file_path}")

        # Update the model version file
        model_version = get_model_version() + 1
        with open(os.path.join(MODEL_PATH, MODEL_VERSION_FILE), 'w') as version_file:
            version_file.write(str(model_version))

        logger.info(f"Model version updated to {model_version}")

        # Optionally update dashboard or system with new model metrics
        update_dashboard_with_model_metrics(model)
    
    except Exception as e:
        handle_error(e)


def get_model_version():
    """
    Get the current version of the model.

    Returns:
        int: The current model version.
    """
    try:
        version_file_path = os.path.join(MODEL_PATH, MODEL_VERSION_FILE)

        if os.path.exists(version_file_path):
            with open(version_file_path, 'r') as version_file:
                return int(version_file.read())
        else:
            return 0  # Default model version if the file does not exist
    except Exception as e:
        handle_error(e)
        return 0


@app.route('/predict', methods=['POST'])
def predict():
    """
    API endpoint to handle predictions using the deployed model.

    Returns:
        json: The prediction result as a JSON response.
    """
    try:
        # Parse the input data
        data = request.get_json()

        if not data:
            return jsonify({"error": "No input data provided."}), 400
        
        # Generate features from the input data
        platform_data = data.get('platform_data', {})
        model = load_model()
        
        if model is None:
            return jsonify({"error": "Model not found."}), 500
        
        features = generate_features(platform_data=platform_data)
        
        # Perform prediction
        prediction = model.predict(features)
        
        return jsonify({"prediction": prediction.tolist()}), 200

    except Exception as e:
        handle_error(e)
        return jsonify({"error": "Prediction failed."}), 500


@app.route('/retrain', methods=['POST'])
def retrain():
    """
    API endpoint to trigger retraining of the model.

    Returns:
        json: Response indicating success or failure of retraining.
    """
    try:
        logger.info("Retraining the model...")

        # Load new data and retrain the model
        new_data = request.get_json()
        if not new_data:
            return jsonify({"error": "No training data provided."}), 400
        
        # Load the new training data (this could be from a database or new batch of features)
        training_data = new_data.get('training_data', {})
        retrained_model = retrain_model(training_data)
        
        # Deploy the retrained model
        deploy_model(retrained_model)

        return jsonify({"message": "Model retrained and deployed successfully."}), 200

    except Exception as e:
        handle_error(e)
        return jsonify({"error": "Retraining failed."}), 500


@app.route('/model_status', methods=['GET'])
def model_status():
    """
    API endpoint to check the current status of the deployed model.

    Returns:
        json: Model version and status.
    """
    try:
        model_version = get_model_version()
        model_status = "Deployed and Active"
        
        return jsonify({
            "model_version": model_version,
            "status": model_status
        }), 200

    except Exception as e:
        handle_error(e)
        return jsonify({"error": "Failed to retrieve model status."}), 500


def update_model_metrics():
    """
    Update model metrics and performance data after deployment.
    This function can be used to send performance metrics to the dashboard or a monitoring system.
    """
    try:
        # Here, we would fetch model performance metrics (e.g., accuracy, AUC, etc.) and update the dashboard
        logger.info("Updating model metrics in the dashboard.")
        # Replace with actual metrics and update function
        update_dashboard_with_model_metrics()
    
    except Exception as e:
        handle_error(e)


if __name__ == "__main__":
    # Run the Flask app for the model deployment API
    logger.info("Starting model deployment API server...")
    app.run(host='0.0.0.0', port=5000, debug=True)

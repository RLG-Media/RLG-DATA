import logging
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("content_classification_services.log"),
        logging.StreamHandler()
    ]
)

class ContentClassificationService:
    """
    Service for classifying content into predefined categories for RLG Data and RLG Fans.
    """

    def __init__(self, model_path: str = "content_classifier.pkl"):
        """
        Initialize the content classification service.

        Args:
            model_path: Path to save or load the trained classification model.
        """
        self.model_path = model_path
        self.model = self._load_model()

    def _load_model(self):
        """
        Load a pre-trained model if available, otherwise return None.

        Returns:
            The trained model or None if not found.
        """
        if os.path.exists(self.model_path):
            logging.info("Loading existing classification model from %s", self.model_path)
            return joblib.load(self.model_path)
        logging.warning("No pre-trained model found. You need to train a model first.")
        return None

    def train_model(self, data: List[str], labels: List[str]):
        """
        Train the classification model using the provided data and labels.

        Args:
            data: List of content strings to train on.
            labels: Corresponding labels for the content.
        """
        logging.info("Starting training process.")
        X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, random_state=42)

        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer()),
            ('classifier', MultinomialNB())
        ])

        pipeline.fit(X_train, y_train)

        # Evaluate the model
        y_pred = pipeline.predict(X_test)
        report = classification_report(y_test, y_pred)
        logging.info("Model training complete. Evaluation report:\n%s", report)

        # Save the trained model
        joblib.dump(pipeline, self.model_path)
        logging.info("Trained model saved to %s", self.model_path)
        self.model = pipeline

    def classify_content(self, content: str) -> Dict:
        """
        Classify a given piece of content.

        Args:
            content: The content to classify.

        Returns:
            A dictionary with the predicted category and probability.
        """
        if not self.model:
            logging.error("No trained model available. Train a model before classifying content.")
            return {"error": "No trained model available."}

        predicted_label = self.model.predict([content])[0]
        predicted_prob = self.model.predict_proba([content]).max()
        logging.info("Content classified as '%s' with probability %.2f", predicted_label, predicted_prob)
        return {"category": predicted_label, "probability": predicted_prob}

    def batch_classify(self, contents: List[str]) -> List[Dict]:
        """
        Classify a batch of content items.

        Args:
            contents: List of content strings to classify.

        Returns:
            A list of dictionaries with predicted categories and probabilities.
        """
        if not self.model:
            logging.error("No trained model available. Train a model before classifying content.")
            return [{"error": "No trained model available."}] * len(contents)

        predicted_labels = self.model.predict(contents)
        predicted_probs = self.model.predict_proba(contents).max(axis=1)
        results = []
        for label, prob in zip(predicted_labels, predicted_probs):
            results.append({"category": label, "probability": prob})
        logging.info("Batch classification completed for %d items.", len(contents))
        return results

# Example usage
if __name__ == "__main__":
    service = ContentClassificationService()

    # Example training data
    training_data = [
        "Breaking news about technology.",
        "Updates on sports events.",
        "Latest trends in fashion.",
        "Stock market analysis and finance news."
    ]
    training_labels = ["Technology", "Sports", "Fashion", "Finance"]

    # Train the model
    service.train_model(training_data, training_labels)

    # Classify a single piece of content
    result = service.classify_content("The newest smartphone model is released today.")
    print("Single classification result:", result)

    # Classify a batch of content
    batch_results = service.batch_classify([
        "The World Cup final is happening tomorrow.",
        "New clothing line launched for summer.",
        "Global economic summit held in London."
    ])
    print("Batch classification results:", batch_results)

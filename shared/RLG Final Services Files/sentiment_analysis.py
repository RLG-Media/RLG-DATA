import re
import string
import numpy as np
import pandas as pd
from textblob import TextBlob
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from joblib import dump, load

nltk.download('stopwords')
nltk.download('wordnet')

class SentimentAnalysis:
    """
    SentimentAnalysis class to handle text sentiment classification.
    """

    def __init__(self, dataset_path, use_tfidf=False):
        """
        Initializes the SentimentAnalysis class with a dataset for training.

        :param dataset_path: Path to the CSV file containing text data and labels.
        :param use_tfidf: Whether to use TF-IDF vectorization instead of CountVectorizer.
        """
        self.dataset_path = dataset_path
        self.vectorizer = (
            TfidfVectorizer(max_features=5000, stop_words='english')
            if use_tfidf
            else CountVectorizer(max_features=5000, stop_words='english')
        )
        self.le = LabelEncoder()
        self.model = MultinomialNB()
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.vectorized_text = None
        self.labels = None
        self.train_data = None
        self.test_data = None
        self.train_labels = None
        self.test_labels = None
        self.predictions = None

    def _clean_text(self, text):
        """
        Cleans the input text by removing special characters, punctuation, and stop words,
        and applying lemmatization.

        :param text: Raw text data.
        :return: Cleaned text.
        """
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
        text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
        text = re.sub(r'\d+', '', text)  # Remove numbers
        tokens = text.split()
        tokens = [
            self.lemmatizer.lemmatize(word)
            for word in tokens
            if word not in self.stop_words
        ]
        return ' '.join(tokens)

    def load_data(self):
        """
        Loads the dataset for sentiment analysis.
        """
        data = pd.read_csv(self.dataset_path)
        if 'text' not in data.columns or 'label' not in data.columns:
            raise ValueError("Dataset must contain 'text' and 'label' columns.")
        data['clean_text'] = data['text'].apply(self._clean_text)
        self.vectorized_text = self.vectorizer.fit_transform(data['clean_text'])
        self.labels = self.le.fit_transform(data['label'])
        return data

    def preprocess_data(self):
        """
        Prepares the data for training by splitting it into training and testing sets.
        """
        self.train_data, self.test_data, self.train_labels, self.test_labels = train_test_split(
            self.vectorized_text,
            self.labels,
            test_size=0.3,
            random_state=42,
        )

    def train_model(self):
        """
        Trains the sentiment analysis model using Naive Bayes.
        """
        self.model.fit(self.train_data, self.train_labels)

    def evaluate_model(self):
        """
        Evaluates the performance of the model on the testing data.
        """
        self.predictions = self.model.predict(self.test_data)
        accuracy = accuracy_score(self.test_labels, self.predictions)
        print(f"Accuracy: {accuracy}")
        print("Classification Report:")
        print(classification_report(self.test_labels, self.predictions))
        print("Confusion Matrix:")
        print(confusion_matrix(self.test_labels, self.predictions))
        return accuracy

    def predict_sentiment(self, text):
        """
        Predicts the sentiment of a given text.

        :param text: Text data to be analyzed.
        :return: Predicted sentiment (positive or negative).
        """
        clean_text = self._clean_text(text)
        vectorized_text = self.vectorizer.transform([clean_text])
        prediction = self.model.predict(vectorized_text)
        sentiment = self.le.inverse_transform(prediction)[0]
        return sentiment

    def save_model(self, model_path):
        """
        Saves the trained model and vectorizer to disk.

        :param model_path: Path to save the model.
        """
        dump((self.model, self.vectorizer, self.le), model_path)
        print(f"Model saved to {model_path}")

    def load_model(self, model_path):
        """
        Loads the trained model and vectorizer from disk.

        :param model_path: Path to the saved model.
        """
        self.model, self.vectorizer, self.le = load(model_path)
        print(f"Model loaded from {model_path}")


# Example usage:
# sa = SentimentAnalysis('path_to_your_dataset.csv', use_tfidf=True)
# sa.load_data()
# sa.preprocess_data()
# sa.train_model()
# sa.evaluate_model()
# print(sa.predict_sentiment("I love this product!"))

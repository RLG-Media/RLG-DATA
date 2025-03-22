from bs4 import BeautifulSoup
import requests
from sklearn.ensemble import RandomForestClassifier
import pickle
import os
import time

# Path where the model will be saved/loaded
MODEL_PATH = 'scraping_model.pkl'

def load_model():
    """
    Load a pre-trained model from disk, or train a new one if it doesn't exist.
    """
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, 'rb') as model_file:
            model = pickle.load(model_file)
        print("Loaded pre-trained model.")
    else:
        print("Training a new model...")
        model = train_new_model()  # We'll define this function to train a model
    return model

def train_new_model():
    """
    Train a new RandomForest model using dummy data and save it to disk.
    In production, you should train this with actual labeled web data.
    """
    # Example training data (features = [tag, text length, attribute count, ...])
    training_data = [
        ['div', 100, 3],  # Example feature: div with 100 characters and 3 attributes
        ['p', 50, 1],     # Example feature: paragraph with 50 characters
        ['span', 30, 0],  # Example feature: span with 30 characters and no attributes
        # Add more training examples here
    ]
    
    labels = ['mention', 'comment', 'mention']  # Example labels (you need real training data)

    model = RandomForestClassifier()
    model.fit(training_data, labels)

    # Save the trained model to disk
    with open(MODEL_PATH, 'wb') as model_file:
        pickle.dump(model, model_file)

    return model

def extract_features(element):
    """
    Extract relevant features from an HTML element for the prediction model.
    """
    return [
        element.name,  # Tag name (e.g., div, p, span)
        len(element.text),  # Length of the element's inner text
        len(element.attrs),  # Number of attributes (e.g., class, id)
        len(element.find_all())  # Number of child elements
    ]

def adaptive_scrape(url, model, delay=1):
    """
    Scrape a webpage and use the machine learning model to predict and identify mentions.
    Throttle the requests and handle errors.
    """
    try:
        # Ensure we are not overwhelming the target website
        time.sleep(delay)

        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        soup = BeautifulSoup(response.content, 'html.parser')

        predictions = []
        for element in soup.find_all():  # Go through all HTML elements
            features = extract_features(element)  # Extract features from each element
            label = model.predict([features])[0]  # Use the model to predict the label
            predictions.append({'element': element, 'label': label})

        # Filter the elements labeled as 'mention'
        return [p['element'] for p in predictions if p['label'] == 'mention']
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching {url}: {e}")
        return []

# Example usage:
if __name__ == '__main__':
    model = load_model()
    url_to_scrape = 'https://example.com'
    mentions = adaptive_scrape(url_to_scrape, model)
    
    if mentions:
        print(f"Found {len(mentions)} mentions:")
        for mention in mentions:
            print(mention.text)
    else:
        print("No mentions found.")

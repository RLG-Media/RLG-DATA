import logging
from typing import List, Dict, Any
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import OneClassSVM

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("misinformation_detection_services.log"),
        logging.StreamHandler()
    ]
)

class MisinformationDetectionService:
    """
    Service for detecting misinformation across various data sources and social media platforms.
    """

    def __init__(self, threshold: float = 0.5):
        """
        Initialize the MisinformationDetectionService.

        Args:
            threshold: The threshold for flagging content as potential misinformation.
        """
        self.threshold = threshold
        self.vectorizer = TfidfVectorizer()
        self.model = OneClassSVM(kernel='rbf', gamma='scale')

    def train_model(self, training_data: List[str]):
        """
        Train the misinformation detection model.

        Args:
            training_data: A list of verified truthful content.
        """
        logging.info("Training the misinformation detection model...")
        try:
            tfidf_matrix = self.vectorizer.fit_transform(training_data)
            self.model.fit(tfidf_matrix)
            logging.info("Model training completed successfully.")
        except Exception as e:
            logging.error("Error training the model: %s", e)

    def detect_misinformation(self, content: List[str]) -> List[Dict[str, Any]]:
        """
        Detect potential misinformation in the given content.

        Args:
            content: A list of text content to analyze.

        Returns:
            A list of dictionaries with detection results.
        """
        try:
            tfidf_matrix = self.vectorizer.transform(content)
            predictions = self.model.decision_function(tfidf_matrix)

            results = []
            for idx, score in enumerate(predictions):
                results.append({
                    "content": content[idx],
                    "misinformation_score": score,
                    "is_misinformation": score < self.threshold
                })

            logging.info("Misinformation detection completed for %d items.", len(content))
            return results
        except Exception as e:
            logging.error("Error detecting misinformation: %s", e)
            return []

    def fetch_content_from_social_media(self, platform: str, keyword: str, api_key: str) -> List[str]:
        """
        Fetch content from social media platforms.

        Args:
            platform: The social media platform (e.g., 'twitter', 'facebook').
            keyword: The keyword to search for.
            api_key: The API key for the platform.

        Returns:
            A list of content fetched from the platform.
        """
        try:
            if platform.lower() == 'twitter':
                url = f"https://api.twitter.com/2/tweets/search/recent?query={keyword}"
                headers = {"Authorization": f"Bearer {api_key}"}

                response = requests.get(url, headers=headers)
                response.raise_for_status()

                tweets = response.json().get("data", [])
                return [tweet["text"] for tweet in tweets]

            # Add other platforms like Facebook, Reddit, etc., here

            logging.warning("Platform %s is not yet supported.", platform)
            return []

        except Exception as e:
            logging.error("Error fetching content from %s: %s", platform, e)
            return []

    def analyze_platforms(self, platforms: List[Dict[str, str]], keyword: str) -> Dict[str, Any]:
        """
        Analyze content for misinformation across multiple platforms.

        Args:
            platforms: A list of dictionaries with platform details (e.g., name and API key).
            keyword: The keyword to search for.

        Returns:
            A dictionary with platform-specific results.
        """
        results = {}

        for platform in platforms:
            name = platform.get("name")
            api_key = platform.get("api_key")
            
            if not name or not api_key:
                logging.warning("Platform details missing for: %s", platform)
                continue

            content = self.fetch_content_from_social_media(name, keyword, api_key)
            detection_results = self.detect_misinformation(content)
            results[name] = detection_results

        return results

# Example usage
if __name__ == "__main__":
    service = MisinformationDetectionService(threshold=0.3)

    # Simulate training data
    training_data = [
        "The earth orbits the sun.",
        "Vaccines are effective in preventing diseases.",
        "Climate change is caused by human activities."
    ]

    service.train_model(training_data)

    # Simulate content for detection
    content_to_analyze = [
        "The earth is flat.",
        "Vaccines cause autism.",
        "Climate change is a hoax."
    ]

    detection_results = service.detect_misinformation(content_to_analyze)
    for result in detection_results:
        print(result)

    # Analyze across platforms
    platforms = [
        {"name": "twitter", "api_key": "your_twitter_api_key"}
    ]

    platform_results = service.analyze_platforms(platforms, keyword="misinformation")
    print(platform_results)

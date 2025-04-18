import logging
import os
from typing import List, Dict, Any
import json
from datetime import datetime
from shared.utils import preprocess_text, validate_data_format
from shared.config import TRAINING_DATA_DIRECTORY, SUPPORTED_PLATFORMS, DEFAULT_LANGUAGE
from nlp_library.text_cleaner import clean_text
from nlp_library.language_detector import detect_language

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/training_data_generator.log"),
    ],
)


class TrainingDataGenerator:
    """
    Generates training datasets for machine learning models across multiple domains
    and social media platforms for RLG Data and RLG Fans.
    """

    def __init__(self, output_directory: str = TRAINING_DATA_DIRECTORY):
        """
        Initialize the Training Data Generator.

        Args:
            output_directory: Directory where generated datasets will be saved.
        """
        self.output_directory = output_directory
        os.makedirs(self.output_directory, exist_ok=True)
        logging.info(f"TrainingDataGenerator initialized. Output directory: {self.output_directory}")

    def fetch_raw_data(self, platform: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch raw data from a specific social media platform or other data sources.

        Args:
            platform: Name of the platform (e.g., Facebook, Twitter).
            params: Parameters for the data fetch (e.g., keywords, date range).

        Returns:
            A list of raw data entries.
        """
        if platform not in SUPPORTED_PLATFORMS:
            raise ValueError(f"Platform '{platform}' is not supported.")

        try:
            logging.info(f"Fetching raw data from '{platform}' with parameters: {params}")
            # Simulate raw data fetch (replace with actual API integrations)
            raw_data = [
                {"id": 1, "content": "This is an example post!", "timestamp": "2025-01-01T12:00:00Z"},
                {"id": 2, "content": "Another great update from our platform!", "timestamp": "2025-01-02T14:30:00Z"},
            ]
            logging.info(f"Successfully fetched {len(raw_data)} records from '{platform}'.")
            return raw_data
        except Exception as e:
            logging.error(f"Error fetching data from '{platform}': {e}")
            raise

    def preprocess_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Preprocess raw data for training dataset generation.

        Args:
            raw_data: A list of raw data entries.

        Returns:
            A list of preprocessed data entries.
        """
        try:
            logging.info("Starting preprocessing of raw data...")
            preprocessed_data = []
            for entry in raw_data:
                text = entry.get("content", "")
                cleaned_text = clean_text(text)
                language = detect_language(cleaned_text) or DEFAULT_LANGUAGE

                preprocessed_entry = {
                    "id": entry.get("id"),
                    "content": cleaned_text,
                    "language": language,
                    "timestamp": entry.get("timestamp"),
                }
                preprocessed_data.append(preprocessed_entry)
            logging.info(f"Preprocessing completed. Processed {len(preprocessed_data)} records.")
            return preprocessed_data
        except Exception as e:
            logging.error(f"Error preprocessing data: {e}")
            raise

    def save_dataset(self, data: List[Dict[str, Any]], filename: str) -> str:
        """
        Save preprocessed data as a JSON file.

        Args:
            data: A list of preprocessed data entries.
            filename: Name of the file to save.

        Returns:
            The path to the saved file.
        """
        try:
            filepath = os.path.join(self.output_directory, filename)
            with open(filepath, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            logging.info(f"Dataset saved to '{filepath}'.")
            return filepath
        except Exception as e:
            logging.error(f"Error saving dataset to '{filename}': {e}")
            raise

    def generate_training_dataset(
        self, platform: str, params: Dict[str, Any], output_filename: str
    ) -> str:
        """
        Generate a training dataset for a specific platform.

        Args:
            platform: Name of the platform (e.g., Instagram, TikTok).
            params: Parameters for data fetch and processing.
            output_filename: Name of the output file.

        Returns:
            The path to the saved dataset file.
        """
        try:
            raw_data = self.fetch_raw_data(platform, params)
            preprocessed_data = self.preprocess_data(raw_data)
            dataset_path = self.save_dataset(preprocessed_data, output_filename)
            logging.info(f"Training dataset generated for '{platform}' and saved to '{dataset_path}'.")
            return dataset_path
        except Exception as e:
            logging.error(f"Failed to generate training dataset for '{platform}': {e}")
            raise

    def validate_dataset(self, filepath: str) -> bool:
        """
        Validate the format and content of a dataset file.

        Args:
            filepath: Path to the dataset file.

        Returns:
            True if the dataset is valid, False otherwise.
        """
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                data = json.load(file)
            if validate_data_format(data):
                logging.info(f"Dataset at '{filepath}' is valid.")
                return True
            else:
                logging.warning(f"Dataset at '{filepath}' failed validation.")
                return False
        except Exception as e:
            logging.error(f"Error validating dataset at '{filepath}': {e}")
            return False


# Example Usage
if __name__ == "__main__":
    generator = TrainingDataGenerator()

    # Generate a dataset for Twitter
    dataset_path = generator.generate_training_dataset(
        platform="Twitter",
        params={"keywords": ["AI", "technology"], "date_range": "2025-01-01 to 2025-01-31"},
        output_filename=f"twitter_training_dataset_{datetime.now().strftime('%Y%m%d%H%M%S')}.json",
    )
    print(f"Generated Dataset Path: {dataset_path}")

    # Validate the generated dataset
    is_valid = generator.validate_dataset(dataset_path)
    print(f"Dataset Valid: {is_valid}")

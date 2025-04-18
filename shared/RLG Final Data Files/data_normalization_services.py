import logging
from typing import List, Dict, Any
import unicodedata
import re
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("data_normalization_services.log"),
        logging.StreamHandler()
    ]
)

class DataNormalizationService:
    """
    Service for normalizing and standardizing data for RLG Data and RLG Fans.
    """

    def normalize_text(self, text: str) -> str:
        """
        Normalize a text string by removing special characters, extra spaces, and accents.

        Args:
            text: The input text string to normalize.

        Returns:
            A normalized string.
        """
        if not text:
            return ""

        logging.debug("Original text: %s", text)

        # Normalize Unicode characters
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8", "ignore")
        logging.debug("After Unicode normalization: %s", text)

        # Remove special characters
        text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
        logging.debug("After removing special characters: %s", text)

        # Convert to lowercase
        text = text.lower()
        logging.debug("After converting to lowercase: %s", text)

        # Remove extra spaces
        text = re.sub(r"\s+", " ", text).strip()
        logging.debug("After removing extra spaces: %s", text)

        logging.info("Normalized text: %s", text)
        return text

    def normalize_data_frame(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Normalize specific columns in a pandas DataFrame.

        Args:
            df: The pandas DataFrame to normalize.
            columns: A list of column names to normalize.

        Returns:
            The DataFrame with normalized columns.
        """
        logging.info("Starting normalization of DataFrame with %d rows.", len(df))

        for column in columns:
            if column in df.columns:
                logging.info("Normalizing column: %s", column)
                df[column] = df[column].apply(self.normalize_text)
            else:
                logging.warning("Column '%s' not found in DataFrame.", column)

        logging.info("DataFrame normalization complete.")
        return df

    def standardize_keys(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardize keys in a dictionary by normalizing and converting them to lowercase.

        Args:
            data: The dictionary to standardize.

        Returns:
            A dictionary with standardized keys.
        """
        logging.info("Standardizing dictionary keys.")

        standardized_data = {
            self.normalize_text(key): value for key, value in data.items()
        }

        logging.debug("Standardized dictionary: %s", standardized_data)
        return standardized_data

    def deduplicate_data(self, data: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
        """
        Remove duplicate records from a list of dictionaries based on a specific key.

        Args:
            data: The list of dictionaries to deduplicate.
            key: The key to check for duplicates.

        Returns:
            A list of dictionaries with duplicates removed.
        """
        logging.info("Starting deduplication based on key: %s", key)

        seen = set()
        unique_data = []

        for record in data:
            value = record.get(key)
            if value not in seen:
                unique_data.append(record)
                seen.add(value)
            else:
                logging.debug("Duplicate record skipped: %s", record)

        logging.info("Deduplication complete. Reduced from %d to %d records.", len(data), len(unique_data))
        return unique_data

# Example usage
if __name__ == "__main__":
    service = DataNormalizationService()

    # Normalize text
    text = "Héllo, Wørld! This is    a   test."
    print("Normalized text:", service.normalize_text(text))

    # Normalize DataFrame
    import pandas as pd
    df = pd.DataFrame({
        "Name": ["John   Doe", "Jane-Doe", "  Éric  Cartman"],
        "Address": ["123 Main St", "456 Elm St.", "789 Oak St"]
    })
    print("Original DataFrame:")
    print(df)

    normalized_df = service.normalize_data_frame(df, columns=["Name", "Address"])
    print("Normalized DataFrame:")
    print(normalized_df)

    # Standardize dictionary keys
    data = {"Namé": "John", "Áddress": "123 Main St"}
    standardized_data = service.standardize_keys(data)
    print("Standardized dictionary:", standardized_data)

    # Deduplicate data
    records = [
        {"id": 1, "name": "John"},
        {"id": 2, "name": "Jane"},
        {"id": 1, "name": "John"}
    ]
    unique_records = service.deduplicate_data(records, key="id")
    print("Deduplicated records:", unique_records)
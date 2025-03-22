import pandas as pd
import numpy as np
from typing import List, Dict, Union

# Logging utility
def log_message(message: str):
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

class DataCleaning:
    def __init__(self):
        """Initialize the DataCleaning class."""
        log_message("DataCleaning module initialized.")

    def handle_missing_values(self, data: pd.DataFrame, strategy: str = "mean", fill_values: Dict[str, Union[int, float, str]] = None) -> pd.DataFrame:
        """
        Handle missing values in the DataFrame.

        Args:
            data: The input DataFrame.
            strategy: The strategy to handle missing values - 'mean', 'median', 'mode', or 'custom'.
            fill_values: A dictionary of column names and their corresponding fill values (used when strategy is 'custom').

        Returns:
            DataFrame with missing values handled.
        """
        log_message("Handling missing values.")
        if strategy == "mean":
            return data.fillna(data.mean())
        elif strategy == "median":
            return data.fillna(data.median())
        elif strategy == "mode":
            return data.fillna(data.mode().iloc[0])
        elif strategy == "custom" and fill_values:
            return data.fillna(fill_values)
        else:
            log_message("Invalid strategy or missing fill_values for 'custom'. Returning original DataFrame.")
            return data

    def remove_duplicates(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicate rows from the DataFrame.

        Args:
            data: The input DataFrame.

        Returns:
            DataFrame with duplicate rows removed.
        """
        log_message("Removing duplicate rows.")
        return data.drop_duplicates()

    def convert_data_types(self, data: pd.DataFrame, type_mappings: Dict[str, str]) -> pd.DataFrame:
        """
        Convert data types of specified columns.

        Args:
            data: The input DataFrame.
            type_mappings: A dictionary mapping column names to target data types (e.g., 'int', 'float', 'category').

        Returns:
            DataFrame with updated data types.
        """
        log_message("Converting data types.")
        for column, dtype in type_mappings.items():
            try:
                data[column] = data[column].astype(dtype)
                log_message(f"Converted {column} to {dtype}.")
            except Exception as e:
                log_message(f"Error converting {column} to {dtype}: {e}")
        return data

    def normalize_column_names(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize column names by converting them to lowercase and replacing spaces with underscores.

        Args:
            data: The input DataFrame.

        Returns:
            DataFrame with normalized column names.
        """
        log_message("Normalizing column names.")
        data.columns = data.columns.str.lower().str.replace(" ", "_")
        return data

    def remove_outliers(self, data: pd.DataFrame, columns: List[str], method: str = "iqr", z_threshold: float = 3.0) -> pd.DataFrame:
        """
        Remove outliers from specified columns.

        Args:
            data: The input DataFrame.
            columns: List of column names to check for outliers.
            method: Method to detect outliers - 'iqr' (Interquartile Range) or 'zscore'.
            z_threshold: Z-score threshold (used if method='zscore').

        Returns:
            DataFrame with outliers removed.
        """
        log_message(f"Removing outliers using {method} method.")
        if method == "iqr":
            for column in columns:
                if column in data.columns:
                    q1 = data[column].quantile(0.25)
                    q3 = data[column].quantile(0.75)
                    iqr = q3 - q1
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr
                    data = data[(data[column] >= lower_bound) & (data[column] <= upper_bound)]
        elif method == "zscore":
            from scipy.stats import zscore
            for column in columns:
                if column in data.columns:
                    data = data[(np.abs(zscore(data[column])) < z_threshold)]
        return data

    def encode_categorical_columns(self, data: pd.DataFrame, columns: List[str], encoding_type: str = "onehot") -> pd.DataFrame:
        """
        Encode categorical columns.

        Args:
            data: The input DataFrame.
            columns: List of column names to encode.
            encoding_type: Type of encoding - 'onehot' or 'label'.

        Returns:
            DataFrame with encoded categorical columns.
        """
        log_message(f"Encoding categorical columns using {encoding_type} encoding.")
        if encoding_type == "onehot":
            return pd.get_dummies(data, columns=columns)
        elif encoding_type == "label":
            from sklearn.preprocessing import LabelEncoder
            for column in columns:
                if column in data.columns:
                    encoder = LabelEncoder()
                    data[column] = encoder.fit_transform(data[column])
        return data

    def standardize_numeric_columns(self, data: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Standardize numeric columns using z-score normalization.

        Args:
            data: The input DataFrame.
            columns: List of column names to standardize.

        Returns:
            DataFrame with standardized numeric columns.
        """
        log_message("Standardizing numeric columns.")
        for column in columns:
            if column in data.columns:
                data[column] = (data[column] - data[column].mean()) / data[column].std()
        return data

# Main execution
if __name__ == "__main__":
    cleaner = DataCleaning()

    # Example DataFrame
    df = pd.DataFrame({
        "Name": ["Alice", "Bob", "Charlie", "Alice"],
        "Age": [25, 30, np.nan, 25],
        "Salary": [50000, 60000, 70000, 50000],
        "City": ["New York", "Los Angeles", "New York", "New York"]
    })

    # Example usage
    df = cleaner.handle_missing_values(df, strategy="mean")
    df = cleaner.remove_duplicates(df)
    df = cleaner.convert_data_types(df, {"Age": "int", "Salary": "float"})
    df = cleaner.normalize_column_names(df)
    df = cleaner.remove_outliers(df, columns=["Salary"], method="iqr")
    df = cleaner.encode_categorical_columns(df, columns=["city"], encoding_type="onehot")
    df = cleaner.standardize_numeric_columns(df, columns=["salary"])
    print(df)

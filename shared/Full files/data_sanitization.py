# data_sanitization.py

import pandas as pd
import numpy as np
import re
from typing import Union

class DataSanitization:
    """
    Class to handle data sanitization, ensuring data is cleaned, normalized, 
    and prepared for analysis while adhering to privacy and accuracy requirements.
    """
    
    def __init__(self):
        pass

    def remove_duplicates(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Removes duplicate rows from the dataset.
        """
        try:
            clean_data = data.drop_duplicates()
            return clean_data
        except Exception as e:
            raise ValueError(f"Error in removing duplicates: {e}")

    def handle_missing_values(self, data: pd.DataFrame, method: str = 'mean') -> pd.DataFrame:
        """
        Handles missing values by either dropping rows or filling with mean/median/mode.
        """
        try:
            if method == 'drop':
                clean_data = data.dropna()
            elif method == 'mean':
                clean_data = data.fillna(data.mean())
            elif method == 'median':
                clean_data = data.fillna(data.median())
            elif method == 'mode':
                clean_data = data.fillna(data.mode().iloc[0])
            else:
                raise ValueError("Invalid method specified for handling missing values.")
            return clean_data
        except Exception as e:
            raise ValueError(f"Error in handling missing values: {e}")

    def normalize_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Normalizes the data to bring it into a standard scale.
        """
        try:
            normalized_data = (data - data.mean()) / data.std()
            return normalized_data
        except Exception as e:
            raise ValueError(f"Error in normalizing data: {e}")

    def clean_text_data(self, text_data: Union[str, pd.Series]) -> Union[str, pd.Series]:
        """
        Cleans text data by removing special characters, extra spaces, and converting to lowercase.
        """
        try:
            if isinstance(text_data, pd.Series):
                clean_text = text_data.apply(lambda x: re.sub(r'[^a-zA-Z0-9\s]', '', str(x)))
                clean_text = clean_text.apply(lambda x: ' '.join(x.split()))
                clean_text = clean_text.str.lower()
            elif isinstance(text_data, str):
                clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', text_data)
                clean_text = ' '.join(clean_text.split()).lower()
            else:
                raise ValueError("Input should be a string or a pandas Series.")
            return clean_text
        except Exception as e:
            raise ValueError(f"Error in cleaning text data: {e}")

    def detect_outliers(self, data: pd.DataFrame, threshold: float = 1.5) -> pd.DataFrame:
        """
        Detects outliers in the dataset using the IQR method.
        """
        try:
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            outlier_mask = ((data < (Q1 - threshold * IQR)) | (data > (Q3 + threshold * IQR))).any(axis=1)
            clean_data = data[~outlier_mask]
            return clean_data
        except Exception as e:
            raise ValueError(f"Error in detecting outliers: {e}")

# Example Usage
"""
if __name__ == "__main__":
    sample_data = pd.DataFrame({
        'A': [1, 2, 3, 4, 5, np.nan, 2, 3],
        'B': [10, 15, 12, 10, 15, 20, 12, 14],
        'C': ['Hello', 'world!', 'Python', 'Data', 'Sanitization', '!', '123', 'AI']
    })
    
    sanitization = DataSanitization()
    
    # Removing duplicates
    no_duplicates = sanitization.remove_duplicates(sample_data)
    print("No Duplicates:")
    print(no_duplicates)
    
    # Handling missing values
    no_missing_values = sanitization.handle_missing_values(sample_data, method='mean')
    print("No Missing Values:")
    print(no_missing_values)
    
    # Normalizing data
    normalized_data = sanitization.normalize_data(sample_data[['A', 'B']])
    print("Normalized Data:")
    print(normalized_data)
    
    # Cleaning text data
    clean_text_data = sanitization.clean_text_data(sample_data['C'])
    print("Clean Text Data:")
    print(clean_text_data)
    
    # Detecting outliers
    no_outliers = sanitization.detect_outliers(sample_data[['A', 'B']])
    print("No Outliers:")
    print(no_outliers)
"""

import pandas as pd
import numpy as np
import logging
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessing:
    """
    A class to handle data processing, cleaning, and validation.
    """

    def __init__(self):
        """
        Initialize data processing class with default configurations.
        """
        self.scaler = None

    def clean_data(self, df):
        """
        Cleans a pandas DataFrame by handling missing values, duplicates, and invalid data.
        
        :param df: pandas DataFrame to clean
        :return: Cleaned DataFrame
        """
        logger.info("Starting data cleaning process.")

        # Remove duplicates
        logger.debug("Removing duplicates.")
        df = df.drop_duplicates()

        # Handle missing values
        logger.debug("Handling missing values.")
        for column in df.columns:
            if df[column].dtype == np.number:
                df[column].fillna(df[column].mean(), inplace=True)
            else:
                df[column].fillna(df[column].mode()[0], inplace=True)

        # Remove invalid data (e.g., negative values for certain columns)
        logger.debug("Validating data for invalid entries.")
        for column in df.select_dtypes(include=[np.number]).columns:
            if df[column].min() < 0:
                df = df[df[column] >= 0]

        logger.info("Data cleaning process completed.")
        return df

    def normalize_data(self, df, columns):
        """
        Normalizes specified columns in the DataFrame using Min-Max Scaling.
        
        :param df: pandas DataFrame
        :param columns: List of column names to normalize
        :return: DataFrame with normalized columns
        """
        logger.info("Starting data normalization process.")

        self.scaler = MinMaxScaler()
        df[columns] = self.scaler.fit_transform(df[columns])

        logger.info("Data normalization completed.")
        return df

    def standardize_data(self, df, columns):
        """
        Standardizes specified columns in the DataFrame using Z-Score normalization.
        
        :param df: pandas DataFrame
        :param columns: List of column names to standardize
        :return: DataFrame with standardized columns
        """
        logger.info("Starting data standardization process.")

        scaler = StandardScaler()
        df[columns] = scaler.fit_transform(df[columns])

        logger.info("Data standardization completed.")
        return df

    def validate_data(self, df, schema):
        """
        Validates data against a predefined schema.
        
        :param df: pandas DataFrame to validate
        :param schema: Dictionary defining expected data types and constraints
        :return: Tuple (bool, errors) where bool indicates if the data is valid and errors is a list of validation issues
        """
        logger.info("Starting data validation process.")
        errors = []

        for column, rules in schema.items():
            if column not in df.columns:
                errors.append(f"Missing required column: {column}")
                continue

            # Check data type
            if not pd.api.types.is_dtype_equal(df[column].dtype, rules.get("dtype")):
                errors.append(f"Column '{column}' has incorrect data type. Expected: {rules.get('dtype')}, Found: {df[column].dtype}")

            # Check constraints
            if "min" in rules and df[column].min() < rules["min"]:
                errors.append(f"Column '{column}' has values below the minimum: {rules['min']}")

            if "max" in rules and df[column].max() > rules["max"]:
                errors.append(f"Column '{column}' has values above the maximum: {rules['max']}")

        if errors:
            logger.error(f"Data validation failed with errors: {errors}")
            return False, errors

        logger.info("Data validation passed.")
        return True, []

    def process_data_pipeline(self, df, schema=None, normalize_columns=None, standardize_columns=None):
        """
        Full data processing pipeline including cleaning, validation, and transformation.
        
        :param df: pandas DataFrame to process
        :param schema: Optional schema for validation
        :param normalize_columns: Optional list of columns to normalize
        :param standardize_columns: Optional list of columns to standardize
        :return: Processed DataFrame
        """
        logger.info("Starting full data processing pipeline.")

        # Step 1: Clean data
        df = self.clean_data(df)

        # Step 2: Validate data (optional)
        if schema:
            is_valid, errors = self.validate_data(df, schema)
            if not is_valid:
                raise ValueError(f"Data validation failed: {errors}")

        # Step 3: Normalize data (optional)
        if normalize_columns:
            df = self.normalize_data(df, normalize_columns)

        # Step 4: Standardize data (optional)
        if standardize_columns:
            df = self.standardize_data(df, standardize_columns)

        logger.info("Data processing pipeline completed.")
        return df


# Example Usage
if __name__ == "__main__":
    # Example dataset
    data = {
        "id": [1, 2, 3, 4, 5],
        "age": [25, None, 30, -5, 40],
        "income": [50000, 60000, None, 80000, 100000],
        "category": ["A", "B", "C", None, "E"]
    }

    df = pd.DataFrame(data)

    # Schema for validation
    schema = {
        "id": {"dtype": np.int64, "min": 1},
        "age": {"dtype": np.float64, "min": 0, "max": 120},
        "income": {"dtype": np.float64, "min": 0},
        "category": {"dtype": "object"}
    }

    processor = DataProcessing()
    processed_df = processor.process_data_pipeline(df, schema=schema, normalize_columns=["age", "income"])

    print(processed_df)

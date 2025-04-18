import pandas as pd
import numpy as np
from typing import Optional, List, Union, Dict
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, LabelEncoder

class DataCleaner:
    def __init__(self):
        """
        Initializes the DataCleaner.
        """
        self.scaler = StandardScaler()
        self.label_encoders = {}

    @staticmethod
    def remove_duplicates(data: pd.DataFrame) -> pd.DataFrame:
        """
        Removes duplicate rows from the dataset.

        Args:
            data (pd.DataFrame): The input dataset.

        Returns:
            pd.DataFrame: Dataset without duplicate rows.
        """
        initial_rows = len(data)
        data = data.drop_duplicates()
        final_rows = len(data)
        print(f"Removed {initial_rows - final_rows} duplicate rows.")
        return data

    @staticmethod
    def handle_missing_values(
        data: pd.DataFrame,
        strategy: str = "mean",
        columns: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Handles missing values in the dataset.

        Args:
            data (pd.DataFrame): The input dataset.
            strategy (str): Strategy for imputing missing values ("mean", "median", "most_frequent", "constant").
            columns (Optional[List[str]]): Columns to apply the missing value strategy. Defaults to all columns.

        Returns:
            pd.DataFrame: Dataset with missing values handled.
        """
        imputer = SimpleImputer(strategy=strategy)
        columns = columns if columns else data.columns
        for col in columns:
            if data[col].isnull().sum() > 0:
                data[col] = imputer.fit_transform(data[[col]])
                print(f"Imputed missing values in column '{col}' using strategy '{strategy}'.")
        return data

    @staticmethod
    def remove_outliers(data: pd.DataFrame, columns: List[str], z_thresh: float = 3.0) -> pd.DataFrame:
        """
        Removes outliers from the specified columns using Z-score thresholding.

        Args:
            data (pd.DataFrame): The input dataset.
            columns (List[str]): Columns to check for outliers.
            z_thresh (float): Z-score threshold for identifying outliers.

        Returns:
            pd.DataFrame: Dataset with outliers removed.
        """
        for col in columns:
            if col in data.columns:
                z_scores = (data[col] - data[col].mean()) / data[col].std()
                outliers = np.abs(z_scores) > z_thresh
                outlier_count = np.sum(outliers)
                if outlier_count > 0:
                    data = data[~outliers]
                    print(f"Removed {outlier_count} outliers from column '{col}'.")
        return data

    @staticmethod
    def standardize_column_names(data: pd.DataFrame) -> pd.DataFrame:
        """
        Standardizes column names to lowercase and replaces spaces with underscores.

        Args:
            data (pd.DataFrame): The input dataset.

        Returns:
            pd.DataFrame: Dataset with standardized column names.
        """
        data.columns = [col.strip().lower().replace(" ", "_") for col in data.columns]
        print("Standardized column names.")
        return data

    def scale_numeric_data(self, data: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Scales numeric data using StandardScaler.

        Args:
            data (pd.DataFrame): The input dataset.
            columns (List[str]): Numeric columns to scale.

        Returns:
            pd.DataFrame: Dataset with scaled numeric columns.
        """
        data[columns] = self.scaler.fit_transform(data[columns])
        print(f"Scaled numeric columns: {columns}.")
        return data

    def encode_categorical_data(self, data: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Encodes categorical data using Label Encoding.

        Args:
            data (pd.DataFrame): The input dataset.
            columns (List[str]): Categorical columns to encode.

        Returns:
            pd.DataFrame: Dataset with encoded categorical columns.
        """
        for col in columns:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
            data[col] = self.label_encoders[col].fit_transform(data[col].astype(str))
            print(f"Encoded categorical column: '{col}'.")
        return data

    @staticmethod
    def clean_text_data(data: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Cleans text data by removing leading/trailing whitespaces and special characters.

        Args:
            data (pd.DataFrame): The input dataset.
            columns (List[str]): Text columns to clean.

        Returns:
            pd.DataFrame: Dataset with cleaned text columns.
        """
        for col in columns:
            data[col] = data[col].str.strip().str.replace(r"[^a-zA-Z0-9\s]", "", regex=True)
            print(f"Cleaned text data in column: '{col}'.")
        return data

    @staticmethod
    def detect_and_remove_empty_columns(data: pd.DataFrame, threshold: float = 0.9) -> pd.DataFrame:
        """
        Removes columns that are mostly empty.

        Args:
            data (pd.DataFrame): The input dataset.
            threshold (float): Threshold for removing columns (percentage of missing values).

        Returns:
            pd.DataFrame: Dataset with mostly empty columns removed.
        """
        empty_cols = data.columns[data.isnull().mean() > threshold]
        data = data.drop(columns=empty_cols)
        print(f"Removed columns with more than {threshold*100}% missing values: {list(empty_cols)}.")
        return data

    def clean_data(
        self,
        data: pd.DataFrame,
        numeric_columns: Optional[List[str]] = None,
        categorical_columns: Optional[List[str]] = None,
        text_columns: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Comprehensive data cleaning pipeline.

        Args:
            data (pd.DataFrame): The input dataset.
            numeric_columns (Optional[List[str]]): Numeric columns to clean.
            categorical_columns (Optional[List[str]]): Categorical columns to clean.
            text_columns (Optional[List[str]]): Text columns to clean.

        Returns:
            pd.DataFrame: Fully cleaned dataset.
        """
        data = self.standardize_column_names(data)
        data = self.remove_duplicates(data)
        data = self.detect_and_remove_empty_columns(data)

        if numeric_columns:
            data = self.handle_missing_values(data, strategy="mean", columns=numeric_columns)
            data = self.remove_outliers(data, columns=numeric_columns)
            data = self.scale_numeric_data(data, numeric_columns)

        if categorical_columns:
            data = self.handle_missing_values(data, strategy="most_frequent", columns=categorical_columns)
            data = self.encode_categorical_data(data, categorical_columns)

        if text_columns:
            data = self.clean_text_data(data, text_columns)

        print("Data cleaning complete.")
        return data


# Example Usage
if __name__ == "__main__":
    # Example dataset
    df = pd.DataFrame({
        "Name": ["Alice ", "Bob", "Alice ", None],
        "Age": [25, 30, 25, None],
        "Salary": [50000, 60000, None, 55000],
        "Notes": ["Good!", "Excellent", "Needs improvement ", None]
    })

    cleaner = DataCleaner()
    cleaned_data = cleaner.clean_data(
        df,
        numeric_columns=["Age", "Salary"],
        categorical_columns=["Name"],
        text_columns=["Notes"],
    )
    print(cleaned_data)

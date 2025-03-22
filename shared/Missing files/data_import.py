import pandas as pd
import os
import json
import requests
from typing import Union, Dict, List, Optional
from sqlalchemy import create_engine
import pyodbc


class DataImporter:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initializes the DataImporter with optional API key for third-party integrations.

        Args:
            api_key (Optional[str]): API key for accessing third-party tools or services.
        """
        self.api_key = api_key

    @staticmethod
    def import_from_csv(file_path: str, chunksize: Optional[int] = None) -> pd.DataFrame:
        """
        Imports data from a CSV file.

        Args:
            file_path (str): Path to the CSV file.
            chunksize (Optional[int]): Number of rows to read per chunk for large files. Defaults to None (reads entire file).

        Returns:
            pd.DataFrame: DataFrame containing the imported data.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CSV file not found at {file_path}")

        if chunksize:
            print(f"Reading CSV in chunks of {chunksize} rows.")
            chunks = pd.read_csv(file_path, chunksize=chunksize)
            data = pd.concat(chunks, ignore_index=True)
        else:
            data = pd.read_csv(file_path)
        
        print(f"Imported data from {file_path} with {len(data)} rows and {len(data.columns)} columns.")
        return data

    @staticmethod
    def import_from_database(
        connection_string: str, query: str, db_type: str = "mysql"
    ) -> pd.DataFrame:
        """
        Imports data from a database using SQL queries.

        Args:
            connection_string (str): Database connection string.
            query (str): SQL query to execute.
            db_type (str): Type of database (e.g., "mysql", "mssql", "sqlite"). Defaults to "mysql".

        Returns:
            pd.DataFrame: DataFrame containing the imported data.
        """
        try:
            if db_type == "mssql":
                engine = pyodbc.connect(connection_string)
            else:
                engine = create_engine(connection_string)
            
            data = pd.read_sql(query, engine)
            print(f"Imported data from database with {len(data)} rows and {len(data.columns)} columns.")
            return data
        except Exception as e:
            print(f"Error importing data from database: {e}")
            raise

    def import_from_api(self, url: str, params: Optional[Dict] = None) -> pd.DataFrame:
        """
        Imports data from a third-party API.

        Args:
            url (str): API endpoint URL.
            params (Optional[Dict]): Dictionary of query parameters for the API call.

        Returns:
            pd.DataFrame: DataFrame containing the imported data.
        """
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()  # Raise an error for bad status codes
            data = response.json()
            
            # Convert JSON to DataFrame if possible
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict) and "data" in data:
                df = pd.DataFrame(data["data"])
            else:
                raise ValueError("Unexpected API response format.")
            
            print(f"Imported data from API with {len(df)} rows and {len(df.columns)} columns.")
            return df
        except requests.RequestException as e:
            print(f"Error accessing API: {e}")
            raise
        except ValueError as ve:
            print(f"Error processing API response: {ve}")
            raise

    @staticmethod
    def import_from_json(file_path: str) -> pd.DataFrame:
        """
        Imports data from a JSON file.

        Args:
            file_path (str): Path to the JSON file.

        Returns:
            pd.DataFrame: DataFrame containing the imported data.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"JSON file not found at {file_path}")

        with open(file_path, "r") as json_file:
            data = json.load(json_file)
        
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict) and "data" in data:
            df = pd.DataFrame(data["data"])
        else:
            raise ValueError("Unexpected JSON format.")
        
        print(f"Imported data from {file_path} with {len(df)} rows and {len(df.columns)} columns.")
        return df

    @staticmethod
    def validate_imported_data(data: pd.DataFrame) -> None:
        """
        Validates the imported data for basic sanity checks.

        Args:
            data (pd.DataFrame): DataFrame to validate.
        """
        if data.empty:
            raise ValueError("The imported data is empty.")
        
        missing_values = data.isnull().sum().sum()
        if missing_values > 0:
            print(f"Warning: Imported data contains {missing_values} missing values.")

    def import_data(
        self,
        source_type: str,
        source_details: Dict,
        chunksize: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        General method to import data from various sources.

        Args:
            source_type (str): Type of source ("csv", "database", "api", "json").
            source_details (Dict): Details required for importing from the source.
            chunksize (Optional[int]): Chunksize for importing large files. Defaults to None.

        Returns:
            pd.DataFrame: DataFrame containing the imported data.
        """
        if source_type == "csv":
            data = self.import_from_csv(source_details["file_path"], chunksize)
        elif source_type == "database":
            data = self.import_from_database(
                source_details["connection_string"],
                source_details["query"],
                source_details.get("db_type", "mysql"),
            )
        elif source_type == "api":
            data = self.import_from_api(source_details["url"], source_details.get("params"))
        elif source_type == "json":
            data = self.import_from_json(source_details["file_path"])
        else:
            raise ValueError(f"Unsupported source type: {source_type}")

        self.validate_imported_data(data)
        return data


# Example Usage
if __name__ == "__main__":
    importer = DataImporter(api_key="your_api_key_here")

    # Example CSV import
    try:
        csv_data = importer.import_data(
            "csv",
            {"file_path": "data.csv"},
            chunksize=1000,
        )
        print(csv_data.head())
    except Exception as e:
        print(f"Error importing CSV data: {e}")

    # Example API import
    try:
        api_data = importer.import_data(
            "api",
            {"url": "https://api.example.com/data"},
        )
        print(api_data.head())
    except Exception as e:
        print(f"Error importing API data: {e}")

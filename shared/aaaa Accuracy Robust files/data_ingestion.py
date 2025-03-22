import os
import requests
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
from typing import List, Dict, Union

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# Supported data sources
SUPPORTED_SOURCES = ["API", "CSV", "JSON", "DATABASE"]

# Logging utility
def log_message(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

class DataIngestion:
    def __init__(self):
        """Initialize database connection."""
        self.engine = create_engine(DATABASE_URL)
        log_message("Database engine initialized.")

    def fetch_from_api(self, url: str, headers: Dict[str, str] = None, params: Dict[str, str] = None) -> pd.DataFrame:
        """Fetch data from an API and return as a DataFrame."""
        try:
            log_message(f"Fetching data from API: {url}")
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            log_message(f"Data fetched successfully from API.")
            return pd.DataFrame(data)
        except requests.RequestException as e:
            log_message(f"Error fetching data from API: {e}")
            return pd.DataFrame()

    def fetch_from_csv(self, file_path: str) -> pd.DataFrame:
        """Fetch data from a CSV file."""
        try:
            log_message(f"Reading data from CSV file: {file_path}")
            return pd.read_csv(file_path)
        except Exception as e:
            log_message(f"Error reading CSV file: {e}")
            return pd.DataFrame()

    def fetch_from_json(self, file_path: str) -> pd.DataFrame:
        """Fetch data from a JSON file."""
        try:
            log_message(f"Reading data from JSON file: {file_path}")
            return pd.read_json(file_path)
        except Exception as e:
            log_message(f"Error reading JSON file: {e}")
            return pd.DataFrame()

    def fetch_from_database(self, query: str) -> pd.DataFrame:
        """Fetch data from a database using SQL query."""
        try:
            log_message(f"Executing database query: {query}")
            with self.engine.connect() as connection:
                return pd.read_sql_query(query, connection)
        except Exception as e:
            log_message(f"Error executing database query: {e}")
            return pd.DataFrame()

    def load_to_database(self, data: pd.DataFrame, table_name: str, if_exists: str = "append"):
        """Load DataFrame into a database table."""
        try:
            log_message(f"Loading data into table: {table_name}")
            with self.engine.connect() as connection:
                data.to_sql(table_name, connection, if_exists=if_exists, index=False)
            log_message("Data loaded successfully.")
        except Exception as e:
            log_message(f"Error loading data into database: {e}")

    def process_data(
        self, 
        source_type: str, 
        source_details: Union[str, Dict[str, str]], 
        table_name: str
    ):
        """
        General function to handle data ingestion from various sources.
        """
        log_message(f"Starting data ingestion for source type: {source_type}")
        if source_type.upper() not in SUPPORTED_SOURCES:
            log_message(f"Unsupported source type: {source_type}")
            return

        data = pd.DataFrame()
        if source_type.upper() == "API":
            data = self.fetch_from_api(**source_details)
        elif source_type.upper() == "CSV":
            data = self.fetch_from_csv(source_details)
        elif source_type.upper() == "JSON":
            data = self.fetch_from_json(source_details)
        elif source_type.upper() == "DATABASE":
            data = self.fetch_from_database(source_details)

        if not data.empty:
            self.load_to_database(data, table_name)
        else:
            log_message("No data to load.")

# Main execution
if __name__ == "__main__":
    ingestion = DataIngestion()

    # Example usage
    ingestion.process_data(
        source_type="API",
        source_details={
            "url": "https://api.example.com/data",
            "headers": {"Authorization": "Bearer your_api_token"},
            "params": {"date": "2025-01-09"}
        },
        table_name="api_data"
    )

    ingestion.process_data(
        source_type="CSV",
        source_details="/path/to/data.csv",
        table_name="csv_data"
    )

"""
data_ingestion_service.py
Handles data ingestion processes for RLG Data and RLG Fans.
Supports ingestion from various sources such as APIs, files, and databases.
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Union, Any
import pandas as pd
import requests

# Load environment variables and configurations
from config import ActiveConfig
from cache_manager import CacheManager

# Logger setup
logger = logging.getLogger(__name__)

# Supported file formats for ingestion
SUPPORTED_FILE_FORMATS = ["csv", "json", "xlsx"]
SUPPORTED_API_RESPONSE_FORMATS = ["json", "xml"]

# Base directory for temporary ingestion storage
TEMP_DIR = Path(ActiveConfig.TEMP_STORAGE_DIR)


class DataIngestionService:
    """
    Manages data ingestion for RLG Data and RLG Fans.
    """

    def __init__(self, temp_dir: Path = TEMP_DIR):
        self.temp_dir = temp_dir
        self.cache_manager = CacheManager()
        self._ensure_directories_exist()

    def _ensure_directories_exist(self):
        """
        Ensures required directories exist for data ingestion.
        """
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Temporary ingestion directory ensured: {self.temp_dir}")

    def ingest_from_file(self, file_path: Path, format: str) -> pd.DataFrame:
        """
        Ingests data from a local file.

        Args:
            file_path (Path): Path to the file to ingest.
            format (str): Format of the file (csv, json, xlsx).

        Returns:
            pd.DataFrame: DataFrame containing ingested data.
        """
        if format not in SUPPORTED_FILE_FORMATS:
            raise ValueError(f"Unsupported file format: {format}. Supported formats: {SUPPORTED_FILE_FORMATS}")

        logger.info(f"Ingesting data from file: {file_path}")

        if format == "csv":
            data = pd.read_csv(file_path)
        elif format == "json":
            data = pd.read_json(file_path)
        elif format == "xlsx":
            data = pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {format}")

        logger.info(f"File data ingestion successful. Records: {len(data)}")
        return data

    def ingest_from_api(self, endpoint: str, params: Dict[str, Any] = None, headers: Dict[str, str] = None) -> pd.DataFrame:
        """
        Ingests data from an API endpoint.

        Args:
            endpoint (str): API endpoint URL.
            params (Dict[str, Any], optional): Query parameters for the API request.
            headers (Dict[str, str], optional): Headers for the API request.

        Returns:
            pd.DataFrame: DataFrame containing ingested data.
        """
        logger.info(f"Fetching data from API: {endpoint}")
        response = requests.get(endpoint, params=params, headers=headers)

        if response.status_code != 200:
            logger.error(f"Failed to fetch data from API. Status Code: {response.status_code}, Response: {response.text}")
            response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")
        if "json" in content_type:
            data = response.json()
        elif "xml" in content_type:
            logger.error("XML format is not currently supported.")
            raise NotImplementedError("XML format is not supported yet.")
        else:
            logger.error(f"Unsupported API response format: {content_type}")
            raise ValueError(f"Unsupported API response format: {content_type}")

        logger.info(f"API data ingestion successful. Records: {len(data)}")
        return pd.DataFrame(data)

    def ingest_from_database(self, query: str, connection) -> pd.DataFrame:
        """
        Ingests data from a database using a SQL query.

        Args:
            query (str): SQL query to execute.
            connection: Database connection object.

        Returns:
            pd.DataFrame: DataFrame containing ingested data.
        """
        logger.info(f"Executing database query: {query}")
        data = pd.read_sql(query, connection)
        logger.info(f"Database data ingestion successful. Records: {len(data)}")
        return data

    def validate_data(self, data: pd.DataFrame, required_columns: List[str] = None) -> pd.DataFrame:
        """
        Validates ingested data to ensure required columns exist.

        Args:
            data (pd.DataFrame): DataFrame containing the data to validate.
            required_columns (List[str], optional): List of columns that must be present.

        Returns:
            pd.DataFrame: Validated DataFrame.
        """
        logger.info("Validating ingested data.")
        if required_columns:
            missing_columns = [col for col in required_columns if col not in data.columns]
            if missing_columns:
                logger.error(f"Missing required columns: {missing_columns}")
                raise ValueError(f"Missing required columns: {missing_columns}")

        logger.info("Data validation successful.")
        return data

    def save_to_cache(self, data: pd.DataFrame, cache_key: str, ttl: int = 3600):
        """
        Saves ingested data to the cache.

        Args:
            data (pd.DataFrame): DataFrame to cache.
            cache_key (str): Cache key for the data.
            ttl (int): Time-to-live for the cache in seconds.
        """
        logger.info(f"Caching data with key: {cache_key}")
        self.cache_manager.set(cache_key, data.to_dict(orient="records"), ttl)
        logger.info(f"Data cached successfully with key: {cache_key}")

    def cleanup_temp_files(self):
        """
        Cleans up temporary files from the ingestion directory.
        """
        logger.info("Starting cleanup of temporary files.")
        for temp_file in self.temp_dir.glob("*"):
            if temp_file.is_file():
                temp_file.unlink()
                logger.info(f"Deleted temporary file: {temp_file}")
        logger.info("Temporary file cleanup completed.")


# Entry point for scheduled ingestion
def ingestion_service():
    """
    Handles scheduled ingestion for RLG Data and RLG Fans.
    """
    service = DataIngestionService()
    data_sources = {
        "rlg_data_api": {
            "endpoint": "https://api.rlgdata.com/data",
            "params": {"type": "analytics"},
        },
        "rlg_fans_api": {
            "endpoint": "https://api.rlgfans.com/fans",
            "params": {"type": "engagement"},
        },
    }

    for source_name, config in data_sources.items():
        try:
            data = service.ingest_from_api(config["endpoint"], params=config.get("params"))
            service.save_to_cache(data, cache_key=source_name)
        except Exception as e:
            logger.exception(f"Error during ingestion for source: {source_name}. Error: {e}")

    logger.info("Scheduled ingestion service completed successfully.")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run ingestion service
    try:
        ingestion_service()
    except Exception as e:
        logger.exception(f"An error occurred during data ingestion: {e}")

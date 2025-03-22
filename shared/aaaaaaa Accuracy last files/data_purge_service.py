"""
data_purge_service.py
Handles secure and efficient data purging for RLG Data and RLG Fans.
Supports scheduled, on-demand, and automated data purging across various storage systems.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict
import os
import shutil
import psycopg2  # Example for PostgreSQL database
from sqlalchemy import create_engine

# Load configurations
from config import ActiveConfig
from cache_manager import CacheManager

# Logger setup
logger = logging.getLogger(__name__)

# Threshold configurations (default time-to-live in days)
DEFAULT_TTL_DAYS = ActiveConfig.DEFAULT_PURGE_TTL_DAYS
SUPPORTED_STORAGE_TYPES = ["local", "database", "cache"]


class DataPurgeService:
    """
    Manages data purging for RLG Data and RLG Fans.
    """

    def __init__(self):
        self.cache_manager = CacheManager()
        self.database_url = ActiveConfig.DATABASE_URL
        self.local_storage_dir = ActiveConfig.LOCAL_STORAGE_DIR
        self.default_ttl_days = DEFAULT_TTL_DAYS

    def purge_local_storage(self, directory: str = None, ttl_days: int = None):
        """
        Purges files from local storage older than the specified TTL.

        Args:
            directory (str): Directory to clean up.
            ttl_days (int): Time-to-live in days for the files.

        Returns:
            int: Number of files deleted.
        """
        directory = directory or self.local_storage_dir
        ttl_days = ttl_days or self.default_ttl_days
        purge_before_date = datetime.now() - timedelta(days=ttl_days)

        logger.info(f"Purging files in {directory} older than {ttl_days} days.")

        deleted_count = 0
        try:
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))

                    if file_mtime < purge_before_date:
                        os.remove(file_path)
                        deleted_count += 1
                        logger.info(f"Deleted file: {file_path}")

        except Exception as e:
            logger.error(f"Error purging local storage: {e}")
            raise

        logger.info(f"Completed local storage purge. Total files deleted: {deleted_count}")
        return deleted_count

    def purge_cache(self, keys: List[str] = None):
        """
        Purges data from the cache based on specific keys or TTL.

        Args:
            keys (List[str]): List of cache keys to purge. If None, purges expired cache entries.

        Returns:
            int: Number of cache entries deleted.
        """
        logger.info("Starting cache purge.")
        deleted_count = 0

        if keys:
            for key in keys:
                if self.cache_manager.delete(key):
                    deleted_count += 1
                    logger.info(f"Deleted cache key: {key}")
        else:
            logger.info("Purging expired cache entries.")
            deleted_count = self.cache_manager.purge_expired()

        logger.info(f"Completed cache purge. Total keys deleted: {deleted_count}")
        return deleted_count

    def purge_database(self, table_name: str, ttl_days: int = None, column: str = "updated_at"):
        """
        Purges data from a database table based on a TTL.

        Args:
            table_name (str): Name of the table to purge.
            ttl_days (int): Time-to-live in days for the records.
            column (str): Timestamp column to use for TTL filtering.

        Returns:
            int: Number of records deleted.
        """
        ttl_days = ttl_days or self.default_ttl_days
        purge_before_date = datetime.now() - timedelta(days=ttl_days)

        logger.info(f"Purging database table '{table_name}' where '{column}' < {purge_before_date}.")

        try:
            engine = create_engine(self.database_url)
            with engine.connect() as connection:
                delete_query = f"""
                    DELETE FROM {table_name}
                    WHERE {column} < :purge_date
                """
                result = connection.execute(delete_query, {"purge_date": purge_before_date})
                deleted_count = result.rowcount

            logger.info(f"Completed database purge. Total records deleted: {deleted_count}")
            return deleted_count

        except Exception as e:
            logger.error(f"Error purging database: {e}")
            raise

    def purge_all(self):
        """
        Performs a full purge across all storage types.
        """
        logger.info("Starting full purge process.")

        # Purge local storage
        self.purge_local_storage()

        # Purge cache
        self.purge_cache()

        # Purge database tables
        for table in ActiveConfig.PURGEABLE_TABLES:
            self.purge_database(table)

        logger.info("Full purge process completed successfully.")

    def schedule_purge(self, storage_type: str, interval: int, **kwargs):
        """
        Schedules a periodic purge for a specified storage type.

        Args:
            storage_type (str): The type of storage to schedule (local, database, cache).
            interval (int): Interval in seconds for the purge.

        Raises:
            ValueError: If the storage type is unsupported.
        """
        if storage_type not in SUPPORTED_STORAGE_TYPES:
            raise ValueError(f"Unsupported storage type: {storage_type}")

        logger.info(f"Scheduling purge for {storage_type} every {interval} seconds.")

        # Placeholder for integrating with a task scheduler (e.g., Celery)
        # Add actual implementation to periodically run the purge function
        pass


def run_purge_service():
    """
    Entry point for executing the purge service.
    """
    logger.info("Running data purge service.")
    service = DataPurgeService()

    # Perform full purge as part of the scheduled job
    try:
        service.purge_all()
    except Exception as e:
        logger.exception(f"An error occurred during the purge service: {e}")
    else:
        logger.info("Data purge service completed successfully.")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Execute the purge service
    try:
        run_purge_service()
    except Exception as e:
        logger.exception(f"Fatal error in the purge service: {e}")

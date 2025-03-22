import os
import logging
import threading
from typing import Callable, Dict, Any, Generator

import pymysql
import psycopg2
import pymongo
from sqlalchemy import create_engine
from boto3 import client
from botocore.exceptions import BotoCoreError, NoCredentialsError
from cryptography.fernet import Fernet

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class DataMigration:
    """
    Handles data migration between databases, file systems, and storage solutions.
    """

    def __init__(self):
        self.s3_client = client("s3")
        logging.info("DataMigration initialized.")

    # --- Database Migrations ---
    def migrate_sql_to_sql(
        self, source_conn: str, dest_conn: str, table_name: str, chunk_size: int = 1000
    ):
        """
        Migrates data between two SQL databases.
        :param source_conn: SQLAlchemy connection string for the source database.
        :param dest_conn: SQLAlchemy connection string for the destination database.
        :param table_name: Name of the table to migrate.
        :param chunk_size: Number of rows to migrate in each batch.
        """
        source_engine = create_engine(source_conn)
        dest_engine = create_engine(dest_conn)

        with source_engine.connect() as source, dest_engine.connect() as dest:
            logging.info(f"Starting migration for table: {table_name}")
            offset = 0
            while True:
                rows = source.execute(
                    f"SELECT * FROM {table_name} LIMIT {chunk_size} OFFSET {offset}"
                ).fetchall()
                if not rows:
                    break
                dest.execute(
                    table_name.insert(),
                    [dict(row.items()) for row in rows],
                )
                logging.info(f"Migrated {len(rows)} rows from table: {table_name}")
                offset += chunk_size

    def migrate_sql_to_nosql(self, sql_conn: str, nosql_conn: str, table_name: str, collection_name: str):
        """
        Migrates data from SQL to NoSQL database.
        :param sql_conn: SQLAlchemy connection string for the source database.
        :param nosql_conn: MongoDB connection string for the destination database.
        :param table_name: Name of the SQL table.
        :param collection_name: Name of the MongoDB collection.
        """
        sql_engine = create_engine(sql_conn)
        mongo_client = pymongo.MongoClient(nosql_conn)
        collection = mongo_client.get_database()[collection_name]

        with sql_engine.connect() as sql:
            rows = sql.execute(f"SELECT * FROM {table_name}")
            for row in rows:
                collection.insert_one(dict(row.items()))
                logging.info(f"Migrated row to MongoDB collection: {collection_name}")

    def migrate_nosql_to_sql(self, nosql_conn: str, sql_conn: str, collection_name: str, table_name: str):
        """
        Migrates data from NoSQL to SQL database.
        :param nosql_conn: MongoDB connection string for the source database.
        :param sql_conn: SQLAlchemy connection string for the destination database.
        :param collection_name: Name of the MongoDB collection.
        :param table_name: Name of the SQL table.
        """
        mongo_client = pymongo.MongoClient(nosql_conn)
        sql_engine = create_engine(sql_conn)
        collection = mongo_client.get_database()[collection_name]

        with sql_engine.connect() as sql:
            for document in collection.find():
                sql.execute(table_name.insert(), document)
                logging.info(f"Migrated document to SQL table: {table_name}")

    # --- File System Migrations ---
    def migrate_files_to_s3(self, source_dir: str, bucket_name: str, prefix: str = ""):
        """
        Uploads files from local storage to an S3 bucket.
        :param source_dir: Directory containing files to migrate.
        :param bucket_name: S3 bucket name.
        :param prefix: Prefix for S3 keys.
        """
        for root, _, files in os.walk(source_dir):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                s3_key = os.path.join(prefix, file_name)
                try:
                    self.s3_client.upload_file(file_path, bucket_name, s3_key)
                    logging.info(f"Uploaded {file_name} to S3 bucket {bucket_name}")
                except (BotoCoreError, NoCredentialsError) as e:
                    logging.error(f"Failed to upload {file_name}: {e}")

    def migrate_files_from_s3(self, bucket_name: str, dest_dir: str, prefix: str = ""):
        """
        Downloads files from an S3 bucket to local storage.
        :param bucket_name: S3 bucket name.
        :param dest_dir: Directory to save downloaded files.
        :param prefix: Prefix for S3 keys to download.
        """
        try:
            objects = self.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            for obj in objects.get("Contents", []):
                file_name = os.path.basename(obj["Key"])
                dest_path = os.path.join(dest_dir, file_name)
                self.s3_client.download_file(bucket_name, obj["Key"], dest_path)
                logging.info(f"Downloaded {file_name} from S3 bucket {bucket_name}")
        except (BotoCoreError, NoCredentialsError) as e:
            logging.error(f"Failed to download files: {e}")

    # --- Data Validation ---
    def validate_data(self, source_data: Any, target_data: Any, validator: Callable[[Any, Any], bool]):
        """
        Validates data integrity between source and target.
        :param source_data: Original data.
        :param target_data: Migrated data.
        :param validator: Custom validation function.
        :return: True if validation passes, False otherwise.
        """
        if validator(source_data, target_data):
            logging.info("Data validation passed.")
            return True
        else:
            logging.warning("Data validation failed.")
            return False

    # --- Utility Functions ---
    def chunked_processing(self, data: Generator, chunk_size: int):
        """
        Processes data in chunks for efficiency.
        :param data: Data generator.
        :param chunk_size: Number of items per chunk.
        :return: Generator yielding chunks of data.
        """
        chunk = []
        for item in data:
            chunk.append(item)
            if len(chunk) >= chunk_size:
                yield chunk
                chunk = []
        if chunk:
            yield chunk


# Example Usage
if __name__ == "__main__":
    migration = DataMigration()

    # Example: Migrate SQL to SQL
    migration.migrate_sql_to_sql(
        source_conn="mysql+pymysql://user:password@localhost/source_db",
        dest_conn="postgresql+psycopg2://user:password@localhost/destination_db",
        table_name="example_table",
    )

    # Example: Migrate Files to S3
    migration.migrate_files_to_s3(
        source_dir="/path/to/local/files",
        bucket_name="my-s3-bucket",
        prefix="backup/",
    )

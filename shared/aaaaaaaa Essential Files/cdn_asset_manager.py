import os
import logging
from typing import Dict, List, Optional
import boto3
from azure.storage.blob import BlobServiceClient
from google.cloud import storage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("cdn_asset_manager.log"),
        logging.StreamHandler()
    ]
)

class CDNAssetManager:
    """
    Manages assets for RLG Data and RLG Fans across multiple CDNs (AWS S3, Azure Blob Storage, Google Cloud Storage).
    """

    def __init__(self, config: Dict[str, Dict[str, str]]):
        """
        Initialize CDNAssetManager with configuration for each CDN.

        Args:
            config: A dictionary containing credentials and settings for AWS, Azure, and GCP.
        """
        self.aws_client = None
        self.azure_client = None
        self.gcp_client = None

        if "aws" in config:
            self.aws_client = boto3.client(
                's3',
                aws_access_key_id=config["aws"]["access_key"],
                aws_secret_access_key=config["aws"]["secret_key"],
                region_name=config["aws"].get("region", "us-east-1")
            )
            logging.info("AWS S3 client initialized.")

        if "azure" in config:
            self.azure_client = BlobServiceClient(
                account_url=f"https://{config['azure']['account_name']}.blob.core.windows.net",
                credential=config['azure']['account_key']
            )
            logging.info("Azure Blob Storage client initialized.")

        if "gcp" in config:
            self.gcp_client = storage.Client.from_service_account_json(config["gcp"]["service_account_json"])
            logging.info("Google Cloud Storage client initialized.")

    def upload_asset(self, platform: str, bucket_name: str, file_path: str, destination_path: str) -> str:
        """
        Upload an asset to the specified CDN.

        Args:
            platform: The CDN platform (aws, azure, gcp).
            bucket_name: The name of the bucket/container.
            file_path: The local path to the file to upload.
            destination_path: The path where the file will be stored in the CDN.

        Returns:
            The URL of the uploaded asset.
        """
        if platform == "aws" and self.aws_client:
            return self._upload_to_aws(bucket_name, file_path, destination_path)
        elif platform == "azure" and self.azure_client:
            return self._upload_to_azure(bucket_name, file_path, destination_path)
        elif platform == "gcp" and self.gcp_client:
            return self._upload_to_gcp(bucket_name, file_path, destination_path)
        else:
            raise ValueError(f"Unsupported platform or client not initialized: {platform}")

    def delete_asset(self, platform: str, bucket_name: str, file_path: str):
        """
        Delete an asset from the specified CDN.

        Args:
            platform: The CDN platform (aws, azure, gcp).
            bucket_name: The name of the bucket/container.
            file_path: The path of the file in the CDN to delete.
        """
        if platform == "aws" and self.aws_client:
            self.aws_client.delete_object(Bucket=bucket_name, Key=file_path)
            logging.info(f"Deleted asset from AWS S3: {file_path}")
        elif platform == "azure" and self.azure_client:
            container_client = self.azure_client.get_container_client(bucket_name)
            container_client.delete_blob(file_path)
            logging.info(f"Deleted asset from Azure Blob Storage: {file_path}")
        elif platform == "gcp" and self.gcp_client:
            bucket = self.gcp_client.bucket(bucket_name)
            blob = bucket.blob(file_path)
            blob.delete()
            logging.info(f"Deleted asset from Google Cloud Storage: {file_path}")
        else:
            raise ValueError(f"Unsupported platform or client not initialized: {platform}")

    def list_assets(self, platform: str, bucket_name: str) -> List[str]:
        """
        List all assets in the specified bucket/container for a CDN.

        Args:
            platform: The CDN platform (aws, azure, gcp).
            bucket_name: The name of the bucket/container.

        Returns:
            A list of asset paths.
        """
        if platform == "aws" and self.aws_client:
            response = self.aws_client.list_objects_v2(Bucket=bucket_name)
            assets = [item["Key"] for item in response.get("Contents", [])]
            logging.info(f"Listed assets in AWS S3 bucket {bucket_name}.")
            return assets
        elif platform == "azure" and self.azure_client:
            container_client = self.azure_client.get_container_client(bucket_name)
            assets = [blob.name for blob in container_client.list_blobs()]
            logging.info(f"Listed assets in Azure Blob Storage container {bucket_name}.")
            return assets
        elif platform == "gcp" and self.gcp_client:
            bucket = self.gcp_client.bucket(bucket_name)
            assets = [blob.name for blob in bucket.list_blobs()]
            logging.info(f"Listed assets in Google Cloud Storage bucket {bucket_name}.")
            return assets
        else:
            raise ValueError(f"Unsupported platform or client not initialized: {platform}")

    def _upload_to_aws(self, bucket_name: str, file_path: str, destination_path: str) -> str:
        self.aws_client.upload_file(file_path, bucket_name, destination_path)
        url = f"https://{bucket_name}.s3.amazonaws.com/{destination_path}"
        logging.info(f"Uploaded asset to AWS S3: {url}")
        return url

    def _upload_to_azure(self, container_name: str, file_path: str, destination_path: str) -> str:
        blob_client = self.azure_client.get_blob_client(container=container_name, blob=destination_path)
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        url = f"https://{self.azure_client.account_name}.blob.core.windows.net/{container_name}/{destination_path}"
        logging.info(f"Uploaded asset to Azure Blob Storage: {url}")
        return url

    def _upload_to_gcp(self, bucket_name: str, file_path: str, destination_path: str) -> str:
        bucket = self.gcp_client.bucket(bucket_name)
        blob = bucket.blob(destination_path)
        blob.upload_from_filename(file_path)
        url = f"https://storage.googleapis.com/{bucket_name}/{destination_path}"
        logging.info(f"Uploaded asset to Google Cloud Storage: {url}")
        return url

# Example usage
if __name__ == "__main__":
    config = {
        "aws": {
            "access_key": "your_aws_access_key",
            "secret_key": "your_aws_secret_key",
            "region": "us-east-1"
        },
        "azure": {
            "account_name": "your_azure_account_name",
            "account_key": "your_azure_account_key"
        },
        "gcp": {
            "service_account_json": "path/to/your/gcp/service_account.json"
        }
    }

    manager = CDNAssetManager(config)
    uploaded_url = manager.upload_asset("aws", "your-bucket-name", "local/file/path.txt", "remote/path.txt")
    print(f"Uploaded asset URL: {uploaded_url}")

    assets = manager.list_assets("aws", "your-bucket-name")
    print("Assets in bucket:", assets)

    manager.delete_asset("aws", "your-bucket-name", "remote/path.txt")

"""
data_archiving.py
Handles automated and manual data archiving processes for RLG Data and RLG Fans.
Ensures data retention policies are adhered to, while optimizing storage usage.
"""

import os
import shutil
import gzip
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

# Load environment variables
from config import ActiveConfig

# Logger setup
logger = logging.getLogger(__name__)

# Base directories
ARCHIVE_DIR = Path(ActiveConfig.BACKUP_STORAGE_DIR) / "archives"
DATA_DIR = Path(ActiveConfig.BASE_DIR) / "data"
RETENTION_DAYS = ActiveConfig.BACKUP_RETENTION_DAYS


class DataArchiver:
    """
    Manages data archiving operations.
    """

    def __init__(self, archive_dir: Path = ARCHIVE_DIR, retention_days: int = RETENTION_DAYS):
        self.archive_dir = archive_dir
        self.retention_days = retention_days
        self._ensure_directories_exist()

    def _ensure_directories_exist(self):
        """
        Ensures the archive directory exists.
        """
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Archive directory ensured: {self.archive_dir}")

    def archive_data(self, source_dirs: List[Path], compress: bool = True):
        """
        Archives data from the specified source directories.

        Args:
            source_dirs (List[Path]): List of directories to archive.
            compress (bool): Whether to compress archived data.
        """
        logger.info("Starting data archiving process.")
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        for source_dir in source_dirs:
            if not source_dir.exists() or not source_dir.is_dir():
                logger.warning(f"Source directory does not exist: {source_dir}")
                continue

            archive_name = f"{source_dir.name}_{timestamp}.tar"
            archive_path = self.archive_dir / archive_name

            # Create archive
            shutil.make_archive(base_name=str(archive_path.with_suffix("")), format="tar", root_dir=source_dir)
            logger.info(f"Archived {source_dir} to {archive_path}")

            # Compress archive if required
            if compress:
                self._compress_file(archive_path)
                archive_path = archive_path.with_suffix(".tar.gz")
                logger.info(f"Compressed archive to {archive_path}")

        logger.info("Data archiving process completed.")

    def _compress_file(self, file_path: Path):
        """
        Compresses a file using gzip.

        Args:
            file_path (Path): Path to the file to compress.
        """
        with open(file_path, "rb") as f_in:
            with gzip.open(f"{file_path}.gz", "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        file_path.unlink()  # Remove the original uncompressed file
        logger.debug(f"Compressed file {file_path} to {file_path}.gz")

    def cleanup_old_archives(self):
        """
        Deletes archives older than the retention period.
        """
        logger.info("Starting cleanup of old archives.")
        cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)

        for archive in self.archive_dir.glob("*"):
            if archive.is_file() and self._get_file_modification_time(archive) < cutoff_date:
                logger.info(f"Deleting old archive: {archive}")
                archive.unlink()

        logger.info("Cleanup of old archives completed.")

    @staticmethod
    def _get_file_modification_time(file_path: Path) -> datetime:
        """
        Retrieves the last modification time of a file.

        Args:
            file_path (Path): File path.

        Returns:
            datetime: Modification time of the file.
        """
        return datetime.utcfromtimestamp(file_path.stat().st_mtime)


# Utility functions
def archive_service():
    """
    Entry point for data archiving service.
    Handles automated and scheduled archiving for RLG Data and RLG Fans.
    """
    archiver = DataArchiver()
    data_directories = [DATA_DIR / "rlg_data", DATA_DIR / "rlg_fans"]

    logger.info("Initiating scheduled data archiving service.")
    archiver.archive_data(source_dirs=data_directories)
    archiver.cleanup_old_archives()
    logger.info("Data archiving service completed successfully.")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run archiving service
    try:
        archive_service()
    except Exception as e:
        logger.exception(f"An error occurred during data archiving: {e}")

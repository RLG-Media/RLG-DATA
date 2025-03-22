"""
backup_service.py
Handles data backup and restoration for RLG Data and RLG Fans.
"""

import os
import shutil
import datetime
from typing import Optional, List
from pathlib import Path
from fastapi import HTTPException
from config import settings
from logging_service import logger

# Constants
BACKUP_DIRECTORY = settings.BACKUP_DIRECTORY
DATABASE_FILE = settings.DATABASE_FILE
LOGS_DIRECTORY = settings.LOGS_DIRECTORY
DEFAULT_BACKUP_RETENTION_DAYS = 30


class BackupService:
    """
    Provides methods to create, restore, and manage backups.
    """

    @staticmethod
    def create_backup(backup_name: Optional[str] = None) -> str:
        """
        Creates a backup of the database and logs.

        Args:
            backup_name (Optional[str]): Custom name for the backup file.

        Returns:
            str: Path to the created backup file.
        """
        if not os.path.exists(BACKUP_DIRECTORY):
            os.makedirs(BACKUP_DIRECTORY)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = backup_name or f"backup_{timestamp}.zip"
        backup_path = os.path.join(BACKUP_DIRECTORY, backup_name)

        try:
            # Include database and logs in the backup
            with shutil.ZipFile(backup_path, "w") as zip_file:
                zip_file.write(DATABASE_FILE, arcname=os.path.basename(DATABASE_FILE))
                for log_file in Path(LOGS_DIRECTORY).rglob("*.*"):
                    zip_file.write(log_file, arcname=os.path.relpath(log_file, LOGS_DIRECTORY))
            logger.info(f"Backup created successfully: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to create backup: {e}")

    @staticmethod
    def restore_backup(backup_file: str) -> None:
        """
        Restores a backup by extracting the database and logs.

        Args:
            backup_file (str): Path to the backup file.

        Raises:
            HTTPException: If the restoration fails.
        """
        if not os.path.exists(backup_file):
            logger.error(f"Backup file not found: {backup_file}")
            raise HTTPException(status_code=404, detail="Backup file not found.")

        try:
            with shutil.ZipFile(backup_file, "r") as zip_file:
                zip_file.extractall(".")
            logger.info(f"Backup restored successfully from {backup_file}")
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to restore backup: {e}")

    @staticmethod
    def list_backups() -> List[str]:
        """
        Lists all available backup files in the backup directory.

        Returns:
            List[str]: List of backup file names.
        """
        if not os.path.exists(BACKUP_DIRECTORY):
            os.makedirs(BACKUP_DIRECTORY)

        backups = [
            os.path.join(BACKUP_DIRECTORY, file)
            for file in os.listdir(BACKUP_DIRECTORY)
            if file.endswith(".zip")
        ]
        logger.info(f"Available backups: {backups}")
        return backups

    @staticmethod
    def delete_old_backups(retention_days: int = DEFAULT_BACKUP_RETENTION_DAYS) -> None:
        """
        Deletes backup files older than the specified retention period.

        Args:
            retention_days (int): Number of days to retain backups.
        """
        if not os.path.exists(BACKUP_DIRECTORY):
            logger.warning("Backup directory does not exist. No backups to delete.")
            return

        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=retention_days)
        for file in os.listdir(BACKUP_DIRECTORY):
            file_path = os.path.join(BACKUP_DIRECTORY, file)
            if (
                os.path.isfile(file_path)
                and file.endswith(".zip")
                and datetime.datetime.fromtimestamp(os.path.getmtime(file_path)) < cutoff_date
            ):
                try:
                    os.remove(file_path)
                    logger.info(f"Deleted old backup: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to delete old backup: {e}")

    @staticmethod
    def schedule_automatic_backups(interval_hours: int) -> None:
        """
        Sets up automatic backups at a defined interval using a background task scheduler.

        Args:
            interval_hours (int): Time interval between automatic backups in hours.
        """
        from apscheduler.schedulers.background import BackgroundScheduler

        scheduler = BackgroundScheduler()
        scheduler.add_job(
            BackupService.create_backup,
            "interval",
            hours=interval_hours,
            id="automatic_backup",
            replace_existing=True,
        )
        scheduler.start()
        logger.info(f"Automatic backups scheduled every {interval_hours} hours.")


# Example usage (uncomment for testing purposes)
# if __name__ == "__main__":
#     BackupService.create_backup()
#     BackupService.list_backups()
#     BackupService.delete_old_backups()
#     BackupService.restore_backup("path_to_backup.zip")

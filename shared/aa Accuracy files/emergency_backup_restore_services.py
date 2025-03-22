import os
import shutil
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("backup_restore_services.log"),
        logging.StreamHandler()
    ]
)

class EmergencyBackupRestoreService:
    """
    A service to manage emergency backups and restore operations for RLG Data and RLG Fans.
    Ensures data reliability and disaster recovery.
    """

    def __init__(self, backup_dir="backups", data_dir="data"):
        """
        Initialize the backup and restore service.

        Args:
            backup_dir (str): Directory where backups will be stored.
            data_dir (str): Directory of the data to back up.
        """
        self.backup_dir = backup_dir
        self.data_dir = data_dir

        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            logging.info(f"Backup directory created at: {self.backup_dir}")

    def create_backup(self) -> str:
        """
        Create a backup of the data directory.

        Returns:
            str: Path to the created backup.
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.backup_dir, f"backup_{timestamp}")
            shutil.copytree(self.data_dir, backup_path)
            logging.info(f"Backup created successfully at: {backup_path}")
            return backup_path
        except Exception as e:
            logging.error(f"Failed to create backup: {e}")
            raise

    def restore_backup(self, backup_path: str):
        """
        Restore data from a specified backup.

        Args:
            backup_path (str): Path to the backup to restore from.
        """
        try:
            if not os.path.exists(backup_path):
                logging.error(f"Backup path does not exist: {backup_path}")
                raise FileNotFoundError(f"Backup path does not exist: {backup_path}")

            # Clear existing data directory
            if os.path.exists(self.data_dir):
                shutil.rmtree(self.data_dir)
                logging.info("Existing data directory cleared.")

            # Restore backup
            shutil.copytree(backup_path, self.data_dir)
            logging.info(f"Data restored successfully from: {backup_path}")
        except Exception as e:
            logging.error(f"Failed to restore backup: {e}")
            raise

    def list_backups(self) -> list:
        """
        List all available backups.

        Returns:
            list: A list of backup directory names.
        """
        try:
            backups = [f for f in os.listdir(self.backup_dir) if os.path.isdir(os.path.join(self.backup_dir, f))]
            logging.info(f"Available backups: {backups}")
            return backups
        except Exception as e:
            logging.error(f"Failed to list backups: {e}")
            raise

    def delete_backup(self, backup_name: str):
        """
        Delete a specific backup.

        Args:
            backup_name (str): Name of the backup to delete.
        """
        try:
            backup_path = os.path.join(self.backup_dir, backup_name)
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
                logging.info(f"Backup deleted successfully: {backup_name}")
            else:
                logging.error(f"Backup not found: {backup_name}")
                raise FileNotFoundError(f"Backup not found: {backup_name}")
        except Exception as e:
            logging.error(f"Failed to delete backup: {e}")
            raise

# Example Usage
if __name__ == "__main__":
    service = EmergencyBackupRestoreService()

    # Create a backup
    backup_path = service.create_backup()

    # List all backups
    backups = service.list_backups()
    print("Available backups:", backups)

    # Restore from the latest backup
    if backups:
        service.restore_backup(os.path.join(service.backup_dir, backups[-1]))

    # Delete an old backup
    if backups:
        service.delete_backup(backups[0])

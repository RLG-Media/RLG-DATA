import logging
from datetime import datetime
from typing import List, Dict, Optional

# Configure the logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("audit_logs.log"),
        logging.StreamHandler()
    ]
)

class AuditLogService:
    """
    Service class for managing audit logs for RLG Data and RLG Fans.
    Provides functionalities for recording, querying, and exporting logs.
    """

    def __init__(self, storage_backend: Optional[object] = None):
        """
        Initialize the AuditLogService with a storage backend.

        Args:
            storage_backend: Optional storage backend for saving logs (e.g., database, file system).
        """
        self.storage_backend = storage_backend
        logging.info("AuditLogService initialized.")

    def record_log(self, user_id: int, action: str, details: Dict):
        """
        Record a new audit log entry.

        Args:
            user_id: The ID of the user performing the action.
            action: The action being logged (e.g., 'LOGIN', 'DATA_EXPORT').
            details: Additional details about the action.
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "details": details
        }

        # Save the log entry
        self._save_log(log_entry)
        logging.info("Log recorded: %s", log_entry)

    def query_logs(self, user_id: Optional[int] = None, action: Optional[str] = None, date_range: Optional[Dict] = None) -> List[Dict]:
        """
        Query audit logs based on filters.

        Args:
            user_id: Optional filter by user ID.
            action: Optional filter by action type.
            date_range: Optional date range filter (e.g., {"start": "2025-01-01", "end": "2025-01-31"}).

        Returns:
            A list of log entries matching the filters.
        """
        filters = {
            "user_id": user_id,
            "action": action,
            "date_range": date_range
        }
        logging.info("Querying logs with filters: %s", filters)
        return self._retrieve_logs(filters)

    def export_logs(self, export_format: str = "csv", filters: Optional[Dict] = None) -> str:
        """
        Export audit logs to a specified format.

        Args:
            export_format: The format to export logs in ('csv' or 'json').
            filters: Optional filters to apply before exporting.

        Returns:
            The file path of the exported logs.
        """
        logs = self.query_logs(**(filters or {}))

        if export_format == "csv":
            return self._export_to_csv(logs)
        elif export_format == "json":
            return self._export_to_json(logs)
        else:
            logging.error("Unsupported export format: %s", export_format)
            raise ValueError("Unsupported export format. Use 'csv' or 'json'.")

    def _save_log(self, log_entry: Dict):
        """
        Save a log entry to the storage backend or file system.

        Args:
            log_entry: The log entry to save.
        """
        if self.storage_backend:
            self.storage_backend.save_log(log_entry)
        else:
            with open("audit_logs.log", "a") as log_file:
                log_file.write(f"{log_entry}\n")

    def _retrieve_logs(self, filters: Dict) -> List[Dict]:
        """
        Retrieve logs from the storage backend or file system based on filters.

        Args:
            filters: Filters to apply when retrieving logs.

        Returns:
            A list of log entries matching the filters.
        """
        if self.storage_backend:
            return self.storage_backend.query_logs(filters)
        else:
            with open("audit_logs.log", "r") as log_file:
                logs = [eval(line.strip()) for line in log_file]

            if filters.get("user_id"):
                logs = [log for log in logs if log.get("user_id") == filters["user_id"]]

            if filters.get("action"):
                logs = [log for log in logs if log.get("action") == filters["action"]]

            if filters.get("date_range"):
                start = filters["date_range"].get("start")
                end = filters["date_range"].get("end")
                logs = [log for log in logs if start <= log["timestamp"] <= end]

            return logs

    def _export_to_csv(self, logs: List[Dict]) -> str:
        """
        Export logs to a CSV file.

        Args:
            logs: The logs to export.

        Returns:
            The file path of the exported CSV file.
        """
        import csv
        file_path = "exported_logs.csv"
        with open(file_path, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=logs[0].keys())
            writer.writeheader()
            writer.writerows(logs)
        logging.info("Logs exported to CSV: %s", file_path)
        return file_path

    def _export_to_json(self, logs: List[Dict]) -> str:
        """
        Export logs to a JSON file.

        Args:
            logs: The logs to export.

        Returns:
            The file path of the exported JSON file.
        """
        import json
        file_path = "exported_logs.json"
        with open(file_path, "w") as jsonfile:
            json.dump(logs, jsonfile, indent=4)
        logging.info("Logs exported to JSON: %s", file_path)
        return file_path

# Example usage
if __name__ == "__main__":
    audit_service = AuditLogService()
    audit_service.record_log(1, "LOGIN", {"ip": "192.168.1.1"})
    audit_service.record_log(2, "DATA_EXPORT", {"file": "report.pdf"})
    print(audit_service.query_logs(user_id=1))
    audit_service.export_logs(export_format="csv")

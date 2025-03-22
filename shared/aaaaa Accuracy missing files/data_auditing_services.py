import logging
import datetime
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("data_auditing_services.log"),
        logging.StreamHandler()
    ]
)

class DataAuditingService:
    """
    Service class for auditing data activities and ensuring data integrity for RLG Data and RLG Fans.
    """

    def __init__(self):
        self.audit_log = []  # In-memory log (could be replaced with a database or external storage)
        logging.info("DataAuditingService initialized.")

    def log_event(self, event_type: str, user_id: str, details: Dict[str, Any]) -> None:
        """
        Log an auditing event.

        Args:
            event_type (str): Type of the event (e.g., "DATA_ACCESS", "DATA_MODIFICATION").
            user_id (str): ID of the user performing the action.
            details (Dict[str, Any]): Additional details about the event.
        """
        event = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "details": details
        }
        self.audit_log.append(event)
        logging.info("Event logged: %s", event)

    def get_audit_log(self, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """
        Retrieve audit logs within a specified date range.

        Args:
            start_date (str, optional): Start date in ISO format (YYYY-MM-DD).
            end_date (str, optional): End date in ISO format (YYYY-MM-DD).

        Returns:
            List[Dict[str, Any]]: A list of audit log entries within the date range.
        """
        if not start_date and not end_date:
            return self.audit_log

        filtered_logs = []
        for entry in self.audit_log:
            log_date = datetime.datetime.fromisoformat(entry["timestamp"]).date()
            if start_date and log_date < datetime.date.fromisoformat(start_date):
                continue
            if end_date and log_date > datetime.date.fromisoformat(end_date):
                continue
            filtered_logs.append(entry)

        logging.info("Retrieved %d audit logs between %s and %s", len(filtered_logs), start_date, end_date)
        return filtered_logs

    def validate_data_integrity(self, data: List[Dict[str, Any]]) -> List[str]:
        """
        Validate the integrity of data and detect potential issues.

        Args:
            data (List[Dict[str, Any]]): List of data records to validate.

        Returns:
            List[str]: List of integrity issues detected.
        """
        issues = []
        for index, record in enumerate(data):
            if "id" not in record or not record["id"]:
                issues.append(f"Record {index} is missing a unique ID.")
            if "timestamp" in record:
                try:
                    datetime.datetime.fromisoformat(record["timestamp"])
                except ValueError:
                    issues.append(f"Record {index} has an invalid timestamp format.")

        logging.info("Data integrity validation completed with %d issue(s).", len(issues))
        return issues

    def generate_audit_report(self, user_id: str = None) -> Dict[str, Any]:
        """
        Generate a summary report of auditing events.

        Args:
            user_id (str, optional): Filter events by a specific user ID.

        Returns:
            Dict[str, Any]: Summary report of auditing events.
        """
        user_logs = [log for log in self.audit_log if log["user_id"] == user_id] if user_id else self.audit_log

        report = {
            "total_events": len(user_logs),
            "event_types": {},
            "latest_event": user_logs[-1] if user_logs else None
        }

        for log in user_logs:
            event_type = log["event_type"]
            if event_type not in report["event_types"]:
                report["event_types"][event_type] = 0
            report["event_types"][event_type] += 1

        logging.info("Audit report generated: %s", report)
        return report

# Example usage
if __name__ == "__main__":
    auditing_service = DataAuditingService()

    # Log some events
    auditing_service.log_event("DATA_ACCESS", "user123", {"resource": "analytics_data", "action": "view"})
    auditing_service.log_event("DATA_MODIFICATION", "user456", {"resource": "reports", "action": "edit", "report_id": "report789"})

    # Retrieve logs
    logs = auditing_service.get_audit_log()
    print("Audit Logs:", logs)

    # Validate data integrity
    sample_data = [
        {"id": "1", "timestamp": "2025-01-23T10:00:00Z"},
        {"id": "", "timestamp": "invalid-timestamp"}
    ]
    issues = auditing_service.validate_data_integrity(sample_data)
    print("Data Integrity Issues:", issues)

    # Generate audit report
    report = auditing_service.generate_audit_report()
    print("Audit Report:", report)

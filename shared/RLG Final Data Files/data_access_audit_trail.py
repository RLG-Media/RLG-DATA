import os
import json
import hashlib
import logging
import sqlite3
from datetime import datetime
from typing import Dict, Optional

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("data_access_audit.log"), logging.StreamHandler()]
)

# Database File
DB_FILE = "data_access_audit.db"

class DataAccessAuditTrail:
    """
    Logs and tracks all data access events for RLG Data & RLG Fans.
    Ensures compliance with security regulations and provides tamper-proof audit trails.
    """

    def __init__(self):
        """Initialize the audit trail system and create database if not exists."""
        self._initialize_db()

    def _initialize_db(self):
        """Create the audit log database if it does not exist."""
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    username TEXT NOT NULL,
                    role TEXT NOT NULL,
                    action TEXT NOT NULL,
                    data_id TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    ip_address TEXT NOT NULL,
                    region TEXT NOT NULL,
                    hash TEXT NOT NULL
                )
            """)
            conn.commit()
        logging.info("Audit log database initialized.")

    def _generate_hash(self, log_entry: Dict) -> str:
        """Generate a cryptographic hash for data integrity."""
        log_string = json.dumps(log_entry, sort_keys=True)
        return hashlib.sha256(log_string.encode()).hexdigest()

    def log_access(
        self, user_id: str, username: str, role: str, action: str, 
        data_id: str, data_type: str, reason: str, ip_address: str, region: str
    ):
        """
        Log a data access event.

        Args:
            user_id (str): Unique identifier of the user.
            username (str): Username of the person accessing the data.
            role (str): Role of the user (admin, analyst, viewer, etc.).
            action (str): Action performed (view, edit, delete, export, etc.).
            data_id (str): The unique identifier of the data being accessed.
            data_type (str): Type of data (user data, report, analytics, etc.).
            reason (str): The reason for accessing the data.
            ip_address (str): IP address of the user accessing the data.
            region (str): Geographic region of the user.

        Returns:
            None
        """
        timestamp = datetime.utcnow().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "user_id": user_id,
            "username": username,
            "role": role,
            "action": action,
            "data_id": data_id,
            "data_type": data_type,
            "reason": reason,
            "ip_address": ip_address,
            "region": region
        }
        log_hash = self._generate_hash(log_entry)

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_log (timestamp, user_id, username, role, action, 
                data_id, data_type, reason, ip_address, region, hash) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp, user_id, username, role, action, data_id, data_type, reason, 
                ip_address, region, log_hash
            ))
            conn.commit()
        logging.info(f"Logged data access event for user {username} ({role}) on {data_type}.")

    def get_logs(self, limit: Optional[int] = 100) -> list:
        """
        Retrieve audit logs.

        Args:
            limit (Optional[int]): Number of logs to fetch (default 100).

        Returns:
            list: A list of dictionaries containing log entries.
        """
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timestamp, user_id, username, role, action, data_id, 
                data_type, reason, ip_address, region, hash 
                FROM audit_log ORDER BY timestamp DESC LIMIT ?
            """, (limit,))
            logs = cursor.fetchall()

        return [
            {
                "timestamp": log[0],
                "user_id": log[1],
                "username": log[2],
                "role": log[3],
                "action": log[4],
                "data_id": log[5],
                "data_type": log[6],
                "reason": log[7],
                "ip_address": log[8],
                "region": log[9],
                "hash": log[10]
            }
            for log in logs
        ]

    def detect_tampering(self) -> list:
        """
        Detect any tampered audit logs.

        Returns:
            list: A list of tampered records.
        """
        tampered_logs = []
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timestamp, user_id, username, role, action, data_id, 
                data_type, reason, ip_address, region, hash 
                FROM audit_log
            """)
            logs = cursor.fetchall()

        for log in logs:
            log_entry = {
                "timestamp": log[0],
                "user_id": log[1],
                "username": log[2],
                "role": log[3],
                "action": log[4],
                "data_id": log[5],
                "data_type": log[6],
                "reason": log[7],
                "ip_address": log[8],
                "region": log[9]
            }
            recalculated_hash = self._generate_hash(log_entry)

            if recalculated_hash != log[10]:
                tampered_logs.append(log_entry)

        if tampered_logs:
            logging.warning(f"⚠️ Detected {len(tampered_logs)} tampered records!")
        else:
            logging.info("✅ No tampered records detected.")

        return tampered_logs


# Example Usage
if __name__ == "__main__":
    audit_trail = DataAccessAuditTrail()

    # Log a sample data access event
    audit_trail.log_access(
        user_id="U123456",
        username="admin_user",
        role="admin",
        action="view",
        data_id="RLG-REPORT-2024",
        data_type="report",
        reason="Performance analysis",
        ip_address="192.168.1.1",
        region="South Africa"
    )

    # Retrieve latest logs
    logs = audit_trail.get_logs(limit=5)
    print(json.dumps(logs, indent=4))

    # Detect tampered logs
    tampered = audit_trail.detect_tampering()
    if tampered:
        print("\n⚠️ Tampered Records Found:")
        print(json.dumps(tampered, indent=4))

import json
import logging
import time
from datetime import datetime
from queue import Queue
from threading import Thread
from database import Database
from email_notification import EmailNotification
from moderation_ai import ModerationAI
from config import ABUSE_REPORT_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class AbuseReporting:
    """Handles user-reported abuse, automates flagging, and integrates with compliance tools."""

    def __init__(self):
        self.db = Database()
        self.email_notifier = EmailNotification()
        self.moderation_ai = ModerationAI()
        self.report_queue = Queue()
        self.moderation_threshold = ABUSE_REPORT_CONFIG.get("moderation_threshold", 0.85)
        self.auto_flag_severe = ABUSE_REPORT_CONFIG.get("auto_flag_severe", True)
        self.admin_email = ABUSE_REPORT_CONFIG.get("admin_email", "security@rlgdata.com")

    def validate_report(self, report):
        """Validates required fields in an abuse report."""
        required_fields = ["report_id", "user_id", "content_id", "category", "details", "timestamp"]
        for field in required_fields:
            if field not in report:
                return False
        return True

    def process_report(self):
        """Continuously processes abuse reports from the queue."""
        while True:
            if not self.report_queue.empty():
                report = self.report_queue.get()
                self.handle_report(report)
            time.sleep(1)  # Avoid excessive CPU usage

    def handle_report(self, report):
        """Processes an abuse report with AI moderation and compliance checks."""
        if not self.validate_report(report):
            logging.error(f"Invalid report format: {report}")
            return

        logging.info(f"Processing abuse report: {report['report_id']}")

        # AI Moderation - Evaluates severity
        severity_score = self.moderation_ai.evaluate_content(report["details"])
        flagged = severity_score >= self.moderation_threshold

        # Update report in database
        self.db.insert("abuse_reports", {
            "report_id": report["report_id"],
            "user_id": report["user_id"],
            "content_id": report["content_id"],
            "category": report["category"],
            "details": report["details"],
            "severity_score": severity_score,
            "flagged": flagged,
            "status": "Flagged" if flagged else "Under Review",
            "timestamp": report["timestamp"]
        })

        # Notify Admin if flagged
        if flagged and self.auto_flag_severe:
            self.email_notifier.send_email(
                [self.admin_email],
                "🚨 High-Risk Abuse Report Alert 🚨",
                f"Report ID: {report['report_id']}\n"
                f"Category: {report['category']}\n"
                f"Severity Score: {severity_score}\n"
                f"Details: {report['details']}\n"
                f"Timestamp: {report['timestamp']}"
            )

        logging.info(f"Abuse report processed: {report['report_id']} | Flagged: {flagged}")

    def submit_report(self, user_id, content_id, category, details):
        """Allows users to submit an abuse report."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        report_id = f"{user_id}-{content_id}-{timestamp}"
        report = {
            "report_id": report_id,
            "user_id": user_id,
            "content_id": content_id,
            "category": category,
            "details": details,
            "timestamp": timestamp
        }
        self.report_queue.put(report)
        logging.info(f"New abuse report submitted: {report_id}")

# Start report processing in a background thread
abuse_reporting = AbuseReporting()
report_thread = Thread(target=abuse_reporting.process_report, daemon=True)
report_thread.start()

# Example Usage
if __name__ == "__main__":
    abuse_reporting.submit_report(
        user_id="user123",
        content_id="post789",
        category="Hate Speech",
        details="This post contains harmful speech against a certain group."
    )

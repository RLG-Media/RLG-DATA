import logging
import traceback
import smtplib
from email.mime.text import MIMEText
from typing import Dict, Any
import requests
import os
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("error_reporting.log"),
        logging.StreamHandler()
    ]
)

class ErrorReporter:
    """
    Handles error reporting, logging, and notification for the application.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.slack_webhook_url = config.get("slack_webhook_url")
        self.sentry_dsn = config.get("sentry_dsn")
        self.email_settings = config.get("email_settings")
        logging.info("ErrorReporter initialized.")

    # --- Error Logging ---
    def log_error(self, error_message: str, context: Dict[str, Any] = None):
        """
        Logs an error message with optional context.
        :param error_message: Error message to log.
        :param context: Additional context about the error.
        """
        logging.error(f"Error: {error_message}")
        if context:
            logging.error(f"Context: {json.dumps(context, indent=2)}")

    # --- Real-Time Alerts ---
    def send_email_alert(self, subject: str, body: str):
        """
        Sends an email alert for critical errors.
        :param subject: Subject of the email.
        :param body: Body of the email.
        """
        try:
            email_settings = self.email_settings
            if not email_settings:
                logging.warning("Email settings not configured.")
                return

            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = email_settings["sender"]
            msg["To"] = ", ".join(email_settings["recipients"])

            with smtplib.SMTP(email_settings["smtp_server"], email_settings["smtp_port"]) as server:
                server.starttls()
                server.login(email_settings["username"], email_settings["password"])
                server.sendmail(email_settings["sender"], email_settings["recipients"], msg.as_string())
            logging.info("Email alert sent successfully.")
        except Exception as e:
            logging.error(f"Failed to send email alert: {e}")

    def send_slack_alert(self, message: str):
        """
        Sends an alert to Slack for critical errors.
        :param message: Message to send to Slack.
        """
        if not self.slack_webhook_url:
            logging.warning("Slack webhook URL not configured.")
            return

        try:
            response = requests.post(
                self.slack_webhook_url,
                json={"text": message},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                logging.info("Slack alert sent successfully.")
            else:
                logging.error(f"Failed to send Slack alert: {response.status_code} - {response.text}")
        except Exception as e:
            logging.error(f"Error sending Slack alert: {e}")

    # --- Integration with Monitoring Tools ---
    def report_to_sentry(self, exception: Exception, context: Dict[str, Any] = None):
        """
        Reports an exception to Sentry.
        :param exception: Exception to report.
        :param context: Additional context to include.
        """
        if not self.sentry_dsn:
            logging.warning("Sentry DSN not configured.")
            return

        try:
            import sentry_sdk
            sentry_sdk.init(self.sentry_dsn)
            with sentry_sdk.push_scope() as scope:
                if context:
                    for key, value in context.items():
                        scope.set_context(key, value)
                sentry_sdk.capture_exception(exception)
            logging.info("Exception reported to Sentry.")
        except ImportError:
            logging.error("Sentry SDK not installed. Please install sentry-sdk to enable this feature.")
        except Exception as e:
            logging.error(f"Error reporting to Sentry: {e}")

    # --- User Feedback ---
    def collect_user_feedback(self, feedback: str, user_info: Dict[str, Any]):
        """
        Collects user feedback about errors or issues.
        :param feedback: User's feedback message.
        :param user_info: Information about the user providing feedback.
        """
        feedback_entry = {
            "feedback": feedback,
            "user_info": user_info,
            "timestamp": logging.Formatter().formatTime(logging.LogRecord("", "", "", "", "", None, None))
        }
        logging.info(f"User feedback collected: {feedback_entry}")

    # --- Retry Mechanism ---
    def retry_operation(self, func, retries: int = 3, *args, **kwargs):
        """
        Retries an operation a specified number of times in case of failure.
        :param func: Function to retry.
        :param retries: Number of retry attempts.
        :param args: Arguments for the function.
        :param kwargs: Keyword arguments for the function.
        :return: Result of the function if successful.
        """
        for attempt in range(retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == retries - 1:
                    raise
                else:
                    logging.info("Retrying operation...")

    # --- Error Aggregation ---
    def aggregate_errors(self, error_list: list):
        """
        Aggregates a list of errors and identifies duplicates.
        :param error_list: List of error messages.
        :return: Dictionary with error counts.
        """
        error_counts = {}
        for error in error_list:
            if error not in error_counts:
                error_counts[error] = 0
            error_counts[error] += 1
        logging.info(f"Aggregated errors: {error_counts}")
        return error_counts


# Example Usage
if __name__ == "__main__":
    config = {
        "slack_webhook_url": "https://hooks.slack.com/services/...",
        "sentry_dsn": "https://examplePublicKey@o0.ingest.sentry.io/0",
        "email_settings": {
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "username": "user@example.com",
            "password": "password",
            "sender": "noreply@example.com",
            "recipients": ["admin@example.com"]
        }
    }

    reporter = ErrorReporter(config)

    try:
        # Simulate an error
        1 / 0
    except Exception as e:
        error_context = {"module": "example_module", "operation": "example_operation"}
        reporter.log_error(str(e), error_context)
        reporter.send_email_alert("Critical Error Detected", f"Error: {str(e)}\nContext: {error_context}")
        reporter.send_slack_alert(f"Critical Error: {str(e)}")
        reporter.report_to_sentry(e, error_context)

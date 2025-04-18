import datetime
import json
import logging
from flask import Flask, request, jsonify

# Configure logging: logs will be sent to both a file and the console.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("chatbot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Chatbot:
    """
    Khoto Zulu: Intelligent Chatbot for the RLG Tool.
    
    This class processes user messages, provides responses, logs queries for support, 
    and generates daily/weekly reports of user interactions. It is designed to be robust,
    scalable, and extendable to support additional NLP features and region-specific customization.
    """
    
    def __init__(self):
        # Stores user interactions (list of log entries)
        self.logs = []
        # Stores daily and weekly summary reports for the backend team
        self.daily_reports = []
        self.weekly_reports = []
        logger.info("Chatbot initialized.")

    def handle_user_message(self, user_message: str, user_id: str) -> str:
        """
        Process a user message and generate an appropriate response.
        
        Args:
            user_message (str): The user's input message.
            user_id (str): Unique identifier for the user.
        
        Returns:
            str: The chatbot's response.
        """
        response = "I'm here to assist you! What can I help you with today?"
        lower_message = user_message.lower()

        # Check for keywords to determine the appropriate response.
        if "problem" in lower_message or "error" in lower_message:
            response = "Can you provide more details about the issue you're facing? I'll log it for resolution."
            self.log_query(user_id, user_message, "issue")
        elif "help" in lower_message:
            response = (
                "Here are some things I can help you with:\n"
                "1. Understanding the tool.\n"
                "2. Logging complaints or issues.\n"
                "3. Checking the status of an issue.\n"
                "4. General assistance.\n"
                "Let me know what you'd like to do!"
            )
        elif "status" in lower_message:
            response = "Please provide the issue ID or description, and I'll check the status for you."
        elif "thank you" in lower_message:
            response = "You're welcome! I'm here whenever you need assistance."
        else:
            response = "I'm sorry, I didn't quite understand that. Could you rephrase your query?"
        
        logger.info("Handled message from user %s: %s", user_id, user_message)
        return response

    def log_query(self, user_id: str, user_message: str, query_type: str) -> None:
        """
        Logs a user query for future follow-up or troubleshooting.
        
        Args:
            user_id (str): Unique identifier for the user.
            user_message (str): The user's input message.
            query_type (str): Type of query (e.g., "issue", "feedback").
        """
        log_entry = {
            "user_id": user_id,
            "message": user_message,
            "query_type": query_type,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "logged"
        }
        self.logs.append(log_entry)
        logger.info("Logged query for user %s: %s", user_id, log_entry)

    def generate_report(self, frequency: str = "daily") -> dict:
        """
        Generates a report of user queries based on the specified frequency.
        
        Args:
            frequency (str): "daily" or "weekly".
        
        Returns:
            dict: A report summary including total, resolved, and unresolved issues,
                  common issues, and user query counts.
        """
        try:
            if frequency == "daily":
                today = datetime.datetime.now().date()
                report_logs = [log for log in self.logs 
                               if datetime.datetime.fromisoformat(log["timestamp"]).date() == today]
            elif frequency == "weekly":
                start_of_week = datetime.datetime.now() - datetime.timedelta(days=7)
                report_logs = [log for log in self.logs 
                               if datetime.datetime.fromisoformat(log["timestamp"]) >= start_of_week]
            else:
                logger.error("Invalid frequency provided for report generation.")
                return {}

            report = {
                "timestamp": datetime.datetime.now().isoformat(),
                "total_issues": len(report_logs),
                "resolved_issues": len([log for log in report_logs if log["status"] == "resolved"]),
                "unresolved_issues": len([log for log in report_logs if log["status"] == "logged"]),
                "common_issues": self._identify_common_issues(report_logs),
                "user_data": self._get_user_data(report_logs)
            }

            if frequency == "daily":
                self.daily_reports.append(report)
            elif frequency == "weekly":
                self.weekly_reports.append(report)

            logger.info("Generated %s report: %s", frequency, report)
            return report
        except Exception as e:
            logger.error("Error generating %s report: %s", frequency, e)
            return {}

    def _identify_common_issues(self, logs: list) -> list:
        """
        Identifies the most common issues from the logged queries.
        
        Args:
            logs (list): List of log entries.
        
        Returns:
            list: Top 5 common issues and their counts.
        """
        issues = [log["message"] for log in logs if log["query_type"] == "issue"]
        issue_summary = {}
        for issue in issues:
            issue_summary[issue] = issue_summary.get(issue, 0) + 1
        sorted_issues = sorted(issue_summary.items(), key=lambda x: x[1], reverse=True)
        return sorted_issues[:5]

    def _get_user_data(self, logs: list) -> dict:
        """
        Aggregates user query counts from the logs.
        
        Args:
            logs (list): List of log entries.
        
        Returns:
            dict: Dictionary mapping user IDs to the number of queries they logged.
        """
        user_summary = {}
        for log in logs:
            user_summary[log["user_id"]] = user_summary.get(log["user_id"], 0) + 1
        return user_summary

# -------------------------------
# Flask Integration
# -------------------------------
app = Flask(__name__)
chatbot = Chatbot()

@app.route("/chat", methods=["POST"])
def chat():
    """
    API endpoint for handling user chat messages.
    Expects JSON with "message" and "user_id".
    Returns a JSON response with the chatbot's reply.
    """
    data = request.get_json()
    user_message = data.get("message")
    user_id = data.get("user_id")
    if not user_message or not user_id:
        logger.error("Missing 'message' or 'user_id' in chat request.")
        return jsonify({"error": "Missing 'message' or 'user_id'"}), 400
    response = chatbot.handle_user_message(user_message, user_id)
    return jsonify({"response": response})

@app.route("/generate_report", methods=["GET"])
def generate_report():
    """
    API endpoint for generating a report of user queries.
    Accepts a query parameter "frequency" ("daily" or "weekly").
    Returns the report as JSON.
    """
    frequency = request.args.get("frequency", "daily")
    report = chatbot.generate_report(frequency=frequency)
    return jsonify(report)

if __name__ == "__main__":
    # Run the Flask development server (disable debug mode in production).
    app.run(debug=True)

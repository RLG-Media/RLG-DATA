import os
import logging
import json
import datetime
import requests
from typing import Dict, Optional
from uuid import uuid4

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bug_reports.log"),
        logging.StreamHandler()
    ],
)

class BugReportingToolkit:
    """
    A comprehensive bug reporting system for RLG Data and RLG Fans.
    Supports multi-platform bug tracking, automated logging, and third-party integrations.
    """

    def __init__(self, integrations: Optional[Dict[str, str]] = None):
        """
        Initialize the Bug Reporting Toolkit.

        Args:
            integrations (dict): Optional third-party integrations (Jira, Slack, GitHub).
        """
        self.bug_reports_dir = "bug_reports"
        os.makedirs(self.bug_reports_dir, exist_ok=True)
        self.integrations = integrations or {}

    def generate_bug_id(self) -> str:
        """Generate a unique bug report ID."""
        return str(uuid4())

    def log_bug(self, title: str, description: str, severity: str, platform: str,
                steps_to_reproduce: str, user_info: Dict[str, str], attachments: Optional[Dict] = None) -> str:
        """
        Log a new bug report.

        Args:
            title (str): Brief bug title.
            description (str): Detailed description of the bug.
            severity (str): Bug severity level (Critical, High, Medium, Low).
            platform (str): Affected platform (Web, Mobile, Backend).
            steps_to_reproduce (str): Step-by-step guide to reproduce the bug.
            user_info (dict): Info about the user reporting the bug.
            attachments (dict, optional): Screenshots or log files.

        Returns:
            str: Bug report ID.
        """
        bug_id = self.generate_bug_id()
        timestamp = datetime.datetime.utcnow().isoformat()

        bug_report = {
            "bug_id": bug_id,
            "title": title,
            "description": description,
            "severity": severity,
            "platform": platform,
            "steps_to_reproduce": steps_to_reproduce,
            "user_info": user_info,
            "timestamp": timestamp,
            "attachments": attachments or {}
        }

        # Save report to file
        report_path = os.path.join(self.bug_reports_dir, f"{bug_id}.json")
        with open(report_path, "w") as f:
            json.dump(bug_report, f, indent=4)

        logging.info(f"Bug logged successfully: {bug_id}")

        # Notify third-party integrations
        self.notify_integrations(bug_report)

        return bug_id

    def notify_integrations(self, bug_report: Dict):
        """
        Send bug report to third-party integrations.

        Args:
            bug_report (dict): The bug report details.
        """
        if "slack_webhook" in self.integrations:
            self.send_slack_notification(bug_report)

        if "jira_api_url" in self.integrations:
            self.create_jira_ticket(bug_report)

        if "github_repo" in self.integrations:
            self.create_github_issue(bug_report)

    def send_slack_notification(self, bug_report: Dict):
        """
        Send a bug report notification to Slack.

        Args:
            bug_report (dict): The bug report details.
        """
        webhook_url = self.integrations.get("slack_webhook")
        message = {
            "text": f":bug: *New Bug Reported!* :bug:\n"
                    f"*Title:* {bug_report['title']}\n"
                    f"*Severity:* {bug_report['severity']}\n"
                    f"*Platform:* {bug_report['platform']}\n"
                    f"*Reported by:* {bug_report['user_info'].get('name', 'Unknown')}"
        }
        try:
            requests.post(webhook_url, json=message)
            logging.info("Bug report sent to Slack successfully.")
        except Exception as e:
            logging.error(f"Failed to send Slack notification: {e}")

    def create_jira_ticket(self, bug_report: Dict):
        """
        Create a bug ticket in Jira.

        Args:
            bug_report (dict): The bug report details.
        """
        jira_url = self.integrations.get("jira_api_url")
        auth = (self.integrations.get("jira_username"), self.integrations.get("jira_api_token"))

        payload = {
            "fields": {
                "project": {"key": self.integrations.get("jira_project_key", "BUGS")},
                "summary": bug_report["title"],
                "description": bug_report["description"],
                "issuetype": {"name": "Bug"},
                "priority": {"name": bug_report["severity"]}
            }
        }

        try:
            response = requests.post(f"{jira_url}/rest/api/2/issue", json=payload, auth=auth)
            response.raise_for_status()
            logging.info("Bug report successfully created in Jira.")
        except Exception as e:
            logging.error(f"Failed to create Jira ticket: {e}")

    def create_github_issue(self, bug_report: Dict):
        """
        Create a bug report as a GitHub issue.

        Args:
            bug_report (dict): The bug report details.
        """
        github_repo = self.integrations.get("github_repo")
        github_token = self.integrations.get("github_token")

        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        payload = {
            "title": bug_report["title"],
            "body": f"**Severity:** {bug_report['severity']}\n"
                    f"**Platform:** {bug_report['platform']}\n"
                    f"**Steps to Reproduce:**\n{bug_report['steps_to_reproduce']}\n"
                    f"**Description:**\n{bug_report['description']}",
            "labels": ["bug", bug_report["platform"], bug_report["severity"].lower()]
        }

        try:
            response = requests.post(f"https://api.github.com/repos/{github_repo}/issues", json=payload, headers=headers)
            response.raise_for_status()
            logging.info("Bug report successfully created in GitHub.")
        except Exception as e:
            logging.error(f"Failed to create GitHub issue: {e}")

# Example usage
if __name__ == "__main__":
    integrations = {
        "slack_webhook": "https://hooks.slack.com/services/your/webhook/url",
        "jira_api_url": "https://your-jira-instance.atlassian.net",
        "jira_username": "your-email@example.com",
        "jira_api_token": "your-jira-api-token",
        "jira_project_key": "BUGS",
        "github_repo": "your-org/your-repo",
        "github_token": "your-github-token"
    }

    bug_toolkit = BugReportingToolkit(integrations=integrations)

    bug_id = bug_toolkit.log_bug(
        title="Page crashes when clicking 'Submit'",
        description="When a user clicks submit on the checkout page, the site crashes with a 500 error.",
        severity="High",
        platform="Web",
        steps_to_reproduce="1. Go to checkout page\n2. Fill in details\n3. Click 'Submit'\n4. See crash",
        user_info={"name": "John Doe", "email": "johndoe@example.com"}
    )

    print(f"Bug report successfully created with ID: {bug_id}")

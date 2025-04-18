import os
import json
import requests
import logging
import subprocess
import pkg_resources
from datetime import datetime
from bs4 import BeautifulSoup
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import smtplib
from email.message import EmailMessage

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("sdk_version_checker.log"), logging.StreamHandler()]
)

# Slack API Configuration
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
slack_client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

# Email Notification Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# SDKs to Monitor
SDK_LIST = {
    "openai": "https://pypi.org/pypi/openai/json",
    "requests": "https://pypi.org/pypi/requests/json",
    "facebook-sdk": "https://pypi.org/pypi/facebook-sdk/json",
    "instaloader": "https://pypi.org/pypi/instaloader/json",
    "youtube-dl": "https://pypi.org/pypi/youtube-dl/json",
    "twython": "https://pypi.org/pypi/twython/json",
    "praw": "https://pypi.org/pypi/praw/json",  # Reddit API
    "snapchat": "https://pypi.org/pypi/snapchat/json",
    "deepseek": "https://pypi.org/pypi/deepseek/json",
}

# Get Installed Version of SDK
def get_installed_version(sdk_name):
    """Fetches the installed version of a given SDK."""
    try:
        return pkg_resources.get_distribution(sdk_name).version
    except pkg_resources.DistributionNotFound:
        return None

# Get Latest SDK Version
def get_latest_version(sdk_name, url):
    """Fetches the latest SDK version from PyPI or external sources."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data["info"]["version"]
    except Exception as e:
        logging.error(f"⚠️ Error fetching latest version for {sdk_name}: {e}")
    return None

# Compare Versions
def check_sdk_versions():
    """Compares installed SDK versions with the latest versions."""
    updates_needed = []
    for sdk, url in SDK_LIST.items():
        installed_version = get_installed_version(sdk)
        latest_version = get_latest_version(sdk, url)
        if installed_version and latest_version and installed_version != latest_version:
            updates_needed.append({
                "sdk": sdk,
                "installed": installed_version,
                "latest": latest_version,
                "update_command": f"pip install --upgrade {sdk}"
            })
            logging.warning(f"⚠️ {sdk} update available: {installed_version} → {latest_version}")
    
    return updates_needed

# Send Slack Notification
def send_slack_alert(updates):
    """Sends an update notification to Slack."""
    if not SLACK_WEBHOOK_URL or not updates:
        return
    message = "🚀 *SDK Updates Available!*\n"
    for update in updates:
        message += f"🔹 *{update['sdk']}*: {update['installed']} → {update['latest']}\n"
        message += f"   *Update Command:* `{update['update_command']}`\n"
    
    try:
        slack_client.chat_postMessage(channel="#dev-alerts", text=message)
        logging.info("✅ Slack alert sent successfully.")
    except SlackApiError as e:
        logging.error(f"⚠️ Slack Error: {e.response['error']}")

# Send Email Notification
def send_email_alert(updates):
    """Sends an SDK update alert via email."""
    if not SMTP_USER or not updates:
        return
    msg = EmailMessage()
    msg["Subject"] = "🚀 SDK Update Alerts"
    msg["From"] = SMTP_USER
    msg["To"] = "admin@example.com"
    msg.set_content("\n".join([f"{u['sdk']}: {u['installed']} → {u['latest']} ({u['update_command']})" for u in updates]))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        logging.info("✅ Email alert sent successfully.")
    except Exception as e:
        logging.error(f"⚠️ Email Error: {e}")

# Fetch SDK Release Notes
def fetch_sdk_release_notes(sdk_name):
    """Scrapes release notes for the latest SDK updates."""
    release_notes_url = f"https://pypi.org/project/{sdk_name}/#history"
    try:
        response = requests.get(release_notes_url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            changes = soup.find("div", class_="release__changes")
            return changes.get_text(strip=True) if changes else "No release notes available."
    except Exception as e:
        logging.error(f"⚠️ Error fetching release notes for {sdk_name}: {e}")
    return "No release notes available."

# Generate Update Report
def generate_update_report(updates):
    """Generates a detailed SDK update report."""
    report = "🚀 *SDK Update Report - {}*\n\n".format(datetime.utcnow().strftime("%Y-%m-%d"))
    for update in updates:
        notes = fetch_sdk_release_notes(update["sdk"])
        report += f"🔹 *{update['sdk']}*: {update['installed']} → {update['latest']}\n"
        report += f"   *Update Command:* `{update['update_command']}`\n"
        report += f"   *Release Notes:* {notes}\n\n"
    
    with open("sdk_update_report.txt", "w") as file:
        file.write(report)
    
    logging.info("✅ SDK update report generated.")

# Run SDK Version Check
def run_sdk_version_checker():
    """Runs the full SDK version checking process."""
    logging.info("🔍 Checking SDK versions...")
    updates = check_sdk_versions()
    if updates:
        send_slack_alert(updates)
        send_email_alert(updates)
        generate_update_report(updates)
        logging.info("✅ SDK version check completed with updates available.")
    else:
        logging.info("✅ All SDKs are up to date!")

if __name__ == "__main__":
    run_sdk_version_checker()

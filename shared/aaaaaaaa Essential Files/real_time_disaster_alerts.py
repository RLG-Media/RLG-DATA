import logging
import requests
import json
from datetime import datetime
from typing import List, Dict, Optional
from shared.utils import log_info, log_error, send_notification
from shared.config import (
    DISASTER_ALERT_API_URL,
    DISASTER_ALERT_API_KEY,
    SUPPORTED_SOCIAL_MEDIA_PLATFORMS,
    NOTIFICATION_RECIPIENTS,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/real_time_disaster_alerts.log"),
    ],
)

class RealTimeDisasterAlerts:
    def __init__(self):
        self.api_url = DISASTER_ALERT_API_URL
        self.api_key = DISASTER_ALERT_API_KEY
        self.supported_platforms = SUPPORTED_SOCIAL_MEDIA_PLATFORMS

    def fetch_disaster_alerts(self, region: Optional[str] = None) -> List[Dict]:
        """
        Fetch real-time disaster alerts from the API.

        Args:
            region: Optional. Filter alerts by a specific region or country.

        Returns:
            A list of disaster alerts.
        """
        try:
            params = {"apiKey": self.api_key, "region": region} if region else {"apiKey": self.api_key}
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()

            alerts = response.json().get("alerts", [])
            log_info(f"Fetched {len(alerts)} disaster alerts.")
            return alerts
        except requests.RequestException as e:
            log_error(f"Failed to fetch disaster alerts: {e}")
            return []

    def analyze_alerts(self, alerts: List[Dict]) -> List[Dict]:
        """
        Analyze disaster alerts to determine severity and prioritize actions.

        Args:
            alerts: List of disaster alerts.

        Returns:
            A list of analyzed alerts with prioritization metadata.
        """
        analyzed_alerts = []
        try:
            for alert in alerts:
                severity = alert.get("severity", "unknown").lower()
                priority = (
                    "high" if severity in ["critical", "severe"] else "medium" if severity == "moderate" else "low"
                )

                analyzed_alerts.append(
                    {
                        "title": alert.get("title", "No Title"),
                        "description": alert.get("description", "No Description"),
                        "severity": severity,
                        "priority": priority,
                        "location": alert.get("location", "Unknown"),
                        "timestamp": alert.get("timestamp", datetime.utcnow().isoformat()),
                    }
                )

            log_info(f"Analyzed {len(analyzed_alerts)} disaster alerts.")
            return analyzed_alerts
        except Exception as e:
            log_error(f"Error analyzing alerts: {e}")
            return []

    def distribute_alerts(self, alerts: List[Dict]) -> None:
        """
        Distribute disaster alerts to social media platforms and notification recipients.

        Args:
            alerts: List of disaster alerts to distribute.
        """
        try:
            for alert in alerts:
                # Notify recipients via email or SMS
                for recipient in NOTIFICATION_RECIPIENTS:
                    send_notification(
                        recipient=recipient,
                        subject=f"Disaster Alert: {alert['title']}",
                        message=f"Location: {alert['location']}\nSeverity: {alert['severity'].capitalize()}\n"
                        f"Description: {alert['description']}\nTime: {alert['timestamp']}",
                    )
                log_info(f"Distributed alert '{alert['title']}' to recipients.")

                # Post to supported social media platforms
                for platform in self.supported_platforms:
                    self.post_to_social_media(platform, alert)

        except Exception as e:
            log_error(f"Error distributing alerts: {e}")

    def post_to_social_media(self, platform: str, alert: Dict) -> None:
        """
        Post a disaster alert to a social media platform.

        Args:
            platform: The social media platform to post to.
            alert: The disaster alert data.
        """
        try:
            if platform not in self.supported_platforms:
                log_error(f"Platform {platform} is not supported.")
                return

            # Simulate posting to the platform (replace with actual API call)
            log_info(
                f"Posted to {platform}: Title: {alert['title']}, Location: {alert['location']}, "
                f"Severity: {alert['severity']}"
            )
        except Exception as e:
            log_error(f"Error posting to {platform}: {e}")

    def monitor_disaster_alerts(self, region: Optional[str] = None) -> None:
        """
        Monitor disaster alerts in real time, analyze, and distribute them.

        Args:
            region: Optional. Region to monitor for disaster alerts.
        """
        try:
            alerts = self.fetch_disaster_alerts(region)
            if not alerts:
                log_info("No disaster alerts found.")
                return

            analyzed_alerts = self.analyze_alerts(alerts)
            self.distribute_alerts(analyzed_alerts)
        except Exception as e:
            log_error(f"Error monitoring disaster alerts: {e}")

# Example usage
if __name__ == "__main__":
    alert_manager = RealTimeDisasterAlerts()

    # Monitor disaster alerts globally
    alert_manager.monitor_disaster_alerts()

    # Monitor disaster alerts for a specific region
    alert_manager.monitor_disaster_alerts(region="Africa")

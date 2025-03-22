import logging
import os
from typing import Dict, List, Optional
from datetime import datetime
import re
import requests
import json
from shared.utils import log_info, log_error, send_alert
from shared.config import (
    SECURITY_LOG_FILE,
    ALERT_EMAILS,
    SUSPICIOUS_IP_LIST_URL,
    FIREWALL_API_KEY,
    ENABLE_FIREWALL_BLOCK,
    SOCIAL_MEDIA_PLATFORMS,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/security_threat_detection.log"),
    ],
)


class SecurityThreatDetection:
    """
    Class to detect, analyze, and mitigate security threats for RLG Data and RLG Fans.
    """

    def __init__(self):
        self.suspicious_ip_cache = set()
        self.suspicious_patterns = [
            re.compile(r"(DROP\s+TABLE|DELETE\s+FROM)", re.IGNORECASE),
            re.compile(r"(SELECT.*FROM.*WHERE.*;)", re.IGNORECASE),
        ]
        self.firewall_enabled = ENABLE_FIREWALL_BLOCK

    def detect_sql_injection(self, query: str) -> bool:
        """
        Detect potential SQL injection patterns in a query.

        Args:
            query: The SQL query to analyze.

        Returns:
            True if a potential SQL injection pattern is detected, otherwise False.
        """
        for pattern in self.suspicious_patterns:
            if pattern.search(query):
                log_info(f"Potential SQL injection detected: {query}")
                return True
        return False

    def monitor_logs_for_suspicious_activity(self) -> List[Dict]:
        """
        Monitor security logs for suspicious activities.

        Returns:
            A list of detected suspicious activities.
        """
        detected_threats = []
        try:
            if not os.path.exists(SECURITY_LOG_FILE):
                log_error(f"Security log file not found: {SECURITY_LOG_FILE}")
                return detected_threats

            with open(SECURITY_LOG_FILE, "r") as log_file:
                for line in log_file:
                    if any(pattern.search(line) for pattern in self.suspicious_patterns):
                        log_info(f"Suspicious activity detected in log: {line.strip()}")
                        detected_threats.append({"timestamp": datetime.now(), "log": line.strip()})

            return detected_threats
        except Exception as e:
            log_error(f"Error monitoring logs for suspicious activity: {e}")
            return detected_threats

    def fetch_suspicious_ips(self) -> List[str]:
        """
        Fetch the latest list of suspicious IPs from an external source.

        Returns:
            A list of suspicious IP addresses.
        """
        try:
            response = requests.get(SUSPICIOUS_IP_LIST_URL)
            response.raise_for_status()
            ip_list = response.json()
            self.suspicious_ip_cache.update(ip_list)
            log_info(f"Fetched {len(ip_list)} suspicious IPs from external source.")
            return list(self.suspicious_ip_cache)
        except Exception as e:
            log_error(f"Error fetching suspicious IP list: {e}")
            return []

    def block_ip(self, ip_address: str) -> bool:
        """
        Block a suspicious IP address using a firewall API.

        Args:
            ip_address: The IP address to block.

        Returns:
            True if the IP address was successfully blocked, otherwise False.
        """
        if not self.firewall_enabled:
            log_info(f"Firewall blocking is disabled. Skipping block for IP: {ip_address}")
            return False

        try:
            response = requests.post(
                "https://firewall.example.com/block",
                headers={"Authorization": f"Bearer {FIREWALL_API_KEY}"},
                json={"ip": ip_address},
            )
            if response.status_code == 200:
                log_info(f"Successfully blocked IP: {ip_address}")
                return True
            else:
                log_error(f"Failed to block IP {ip_address}: {response.text}")
                return False
        except Exception as e:
            log_error(f"Error blocking IP {ip_address}: {e}")
            return False

    def analyze_social_media_threats(self) -> List[Dict]:
        """
        Analyze social media platforms for potential threats or malicious activities.

        Returns:
            A list of detected threats across social media platforms.
        """
        detected_threats = []
        for platform in SOCIAL_MEDIA_PLATFORMS:
            try:
                # Simulate API interaction for threat detection
                response = requests.get(f"https://api.{platform}.com/threats", timeout=10)
                response.raise_for_status()
                threats = response.json()
                detected_threats.extend(threats)
                log_info(f"Detected {len(threats)} threats on {platform}.")
            except Exception as e:
                log_error(f"Error analyzing threats on {platform}: {e}")

        return detected_threats

    def send_alerts(self, detected_threats: List[Dict]) -> None:
        """
        Send alerts for detected security threats.

        Args:
            detected_threats: A list of detected threats.
        """
        if not detected_threats:
            log_info("No threats detected. No alerts sent.")
            return

        for email in ALERT_EMAILS:
            try:
                message = f"Detected {len(detected_threats)} security threats. Please review immediately."
                send_alert(email, "Security Threat Alert", message)
                log_info(f"Alert sent to {email}.")
            except Exception as e:
                log_error(f"Error sending alert to {email}: {e}")


# Example Usage
if __name__ == "__main__":
    detector = SecurityThreatDetection()

    # Monitor logs for suspicious activity
    threats_in_logs = detector.monitor_logs_for_suspicious_activity()
    detector.send_alerts(threats_in_logs)

    # Detect SQL injection in a query
    query = "SELECT * FROM users WHERE username = 'admin'; DROP TABLE users;"
    if detector.detect_sql_injection(query):
        log_error(f"SQL injection detected in query: {query}")

    # Fetch and block suspicious IPs
    suspicious_ips = detector.fetch_suspicious_ips()
    for ip in suspicious_ips:
        detector.block_ip(ip)

    # Analyze threats on social media
    social_media_threats = detector.analyze_social_media_threats()
    detector.send_alerts(social_media_threats)

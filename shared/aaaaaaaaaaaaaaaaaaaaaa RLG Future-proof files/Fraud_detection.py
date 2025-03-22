import os
import logging
import json
import time
import requests
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
from config import FRAUD_DETECTION_CONFIG
from geolocation_service import get_user_location
from api_limits_and_throttling import rate_limit_check
from anti_scraping_protection import detect_scraping_activity
from sklearn.ensemble import IsolationForest

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class FraudDetection:
    """AI-powered fraud detection system for RLG Data and RLG Fans."""

    def __init__(self):
        self.blacklist_ips = set(FRAUD_DETECTION_CONFIG.get("blacklist_ips", []))
        self.whitelist_ips = set(FRAUD_DETECTION_CONFIG.get("whitelist_ips", []))
        self.anomaly_model = self._load_model()
        self.user_activity_log = defaultdict(list)
        self.suspicious_users = set()

    def _load_model(self):
        """Loads or trains an anomaly detection model."""
        model_path = FRAUD_DETECTION_CONFIG.get("anomaly_model_path", "fraud_model.pkl")
        if os.path.exists(model_path):
            return joblib.load(model_path)
        else:
            return IsolationForest(contamination=0.02, random_state=42)

    def update_model(self, data):
        """Updates the fraud detection model with new data."""
        df = pd.DataFrame(data)
        self.anomaly_model.fit(df)
        joblib.dump(self.anomaly_model, FRAUD_DETECTION_CONFIG.get("anomaly_model_path", "fraud_model.pkl"))

    def is_fraudulent_request(self, user_id, ip, transaction_amount, request_type, user_agent):
        """Determines if a request is fraudulent based on multiple security layers."""
        # 1. Check IP against blacklist & whitelist
        if ip in self.blacklist_ips:
            logging.warning(f"Fraud detected: Blacklisted IP {ip}")
            return True
        if ip in self.whitelist_ips:
            return False

        # 2. Check for geolocation inconsistencies
        location_data = get_user_location(ip)
        if location_data and location_data["country"] not in FRAUD_DETECTION_CONFIG["allowed_countries"]:
            logging.warning(f"Fraud detected: Unauthorized region {location_data['country']}")
            return True

        # 3. Check for high-risk user behavior (ML-based)
        user_data = np.array([[transaction_amount, len(self.user_activity_log[user_id]), time.time()]])
        anomaly_score = self.anomaly_model.predict(user_data)
        if anomaly_score[0] == -1:
            logging.warning(f"Fraud detected: Anomalous transaction behavior for user {user_id}")
            self.suspicious_users.add(user_id)
            return True

        # 4. API Rate-Limiting (Prevents bot attacks)
        if rate_limit_check(user_id):
            logging.warning(f"Fraud detected: User {user_id} exceeded rate limits")
            return True

        # 5. Anti-Scraping Measures
        if detect_scraping_activity(ip, user_agent):
            logging.warning(f"Fraud detected: Suspicious scraping activity detected for IP {ip}")
            return True

        # 6. Logging user activity
        self.user_activity_log[user_id].append({
            "timestamp": time.time(),
            "ip": ip,
            "transaction_amount": transaction_amount,
            "request_type": request_type
        })

        return False

    def report_fraud(self, user_id, ip):
        """Manually report and blacklist fraudulent users."""
        self.suspicious_users.add(user_id)
        self.blacklist_ips.add(ip)
        logging.warning(f"User {user_id} and IP {ip} added to blacklist.")

    def remove_from_blacklist(self, ip):
        """Removes an IP from the blacklist (if false positive detected)."""
        if ip in self.blacklist_ips:
            self.blacklist_ips.remove(ip)
            logging.info(f"IP {ip} removed from blacklist.")

    def get_suspicious_users(self):
        """Returns a list of flagged suspicious users."""
        return list(self.suspicious_users)

# Example Usage
if __name__ == "__main__":
    fraud_detector = FraudDetection()
    
    user_id = "12345"
    ip_address = "192.168.1.100"
    transaction_amount = 5000
    request_type = "subscription"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

    is_fraud = fraud_detector.is_fraudulent_request(user_id, ip_address, transaction_amount, request_type, user_agent)
    
    if is_fraud:
        fraud_detector.report_fraud(user_id, ip_address)
    else:
        print("Transaction approved.")

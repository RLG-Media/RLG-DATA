import os
import logging
import json
import time
import random
import requests
import threading
import subprocess
from datetime import datetime
from flask import Flask, request, jsonify
from locust import HttpUser, task, between
from multiprocessing import Process

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("load_testing.log"), logging.StreamHandler()]
)

# Flask App for Test Control
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

# Load Testing Configuration
LOAD_TEST_CONFIG = {
    "users": 1000,
    "spawn_rate": 50,
    "test_duration": "10m",
    "api_endpoints": [
        "/api/v1/data",
        "/api/v1/social-media",
        "/api/v1/analytics",
        "/api/v1/reports",
        "/api/v1/search",
    ],
    "regions": ["US", "EU", "SA", "ASIA"],
    "report_file": "load_test_results.json"
}

class RLGUser(HttpUser):
    """
    Simulated User Load for RLG Data & RLG Fans.
    """
    wait_time = between(1, 3)

    @task(3)
    def get_dashboard_data(self):
        self.client.get("/api/v1/data")

    @task(2)
    def perform_search(self):
        self.client.get("/api/v1/search", params={"query": "latest trends"})

    @task(1)
    def fetch_reports(self):
        self.client.get("/api/v1/reports")

    @task(1)
    def social_media_integration(self):
        self.client.get("/api/v1/social-media")

def run_locust_test():
    """Runs Locust load testing"""
    logging.info("Starting Locust Load Test...")
    subprocess.run(["locust", "-f", "load_testing_framework.py", "--headless", "-u", str(LOAD_TEST_CONFIG["users"]), "-r", str(LOAD_TEST_CONFIG["spawn_rate"]), "--run-time", LOAD_TEST_CONFIG["test_duration"]])

def run_k6_test():
    """Runs k6 load testing"""
    logging.info("Starting k6 Load Test...")
    k6_script = f"""
        import http from 'k6/http';
        import {{ sleep }} from 'k6';

        export let options = {{
            vus: {LOAD_TEST_CONFIG["users"] // 2},
            duration: '{LOAD_TEST_CONFIG["test_duration"]}'
        }};

        export default function() {{
            http.get('{random.choice(LOAD_TEST_CONFIG["api_endpoints"])}');
            sleep(1);
        }}
    """
    with open("k6_test.js", "w") as f:
        f.write(k6_script)

    subprocess.run(["k6", "run", "k6_test.js"])

@app.route("/load-test/start", methods=["POST"])
def start_load_test():
    """API Endpoint to trigger load testing"""
    test_type = request.json.get("test_type", "locust")
    process = None

    if test_type == "locust":
        process = Process(target=run_locust_test)
    elif test_type == "k6":
        process = Process(target=run_k6_test)

    if process:
        process.start()
        return jsonify({"status": "Load test started", "test_type": test_type})
    return jsonify({"error": "Invalid test type"}), 400

@app.route("/load-test/report", methods=["GET"])
def get_report():
    """API Endpoint to fetch test results"""
    if os.path.exists(LOAD_TEST_CONFIG["report_file"]):
        with open(LOAD_TEST_CONFIG["report_file"], "r") as f:
            return jsonify(json.load(f))
    return jsonify({"error": "No report available"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)

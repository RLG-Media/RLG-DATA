import os
import json
import requests
import hashlib
from datetime import datetime
from virus_total_apis import PublicApi as VirusTotalAPI
from abuseipdb import AbuseIPDB
from cryptography.fernet import Fernet

# API Keys from Environment Variables
VIRUS_TOTAL_API_KEY = os.getenv("VIRUS_TOTAL_API_KEY")
ABUSEIPDB_API_KEY = os.getenv("ABUSEIPDB_API_KEY")
SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")
HAVEIBENPWNED_API_KEY = os.getenv("HAVEIBENPWNED_API_KEY")

# Threat Intelligence Sources
THREAT_INTEL_SOURCES = ["VirusTotal", "AbuseIPDB", "Shodan", "HaveIBeenPwned"]

class CyberThreatAnalysis:
    def __init__(self):
        self.vt_api = VirusTotalAPI(VIRUS_TOTAL_API_KEY)
        self.abuse_ipdb = AbuseIPDB(ABUSEIPDB_API_KEY)
        self.encryption_key = Fernet.generate_key()  # For encrypting threat reports

    def scan_url(self, url):
        """
        Scans a URL for potential threats using VirusTotal.
        """
        print(f"Scanning URL: {url} with VirusTotal...")
        response = self.vt_api.get_url_report(url)
        return response

    def scan_file_hash(self, file_path):
        """
        Computes file hash and checks it against VirusTotal.
        """
        print(f"Scanning file: {file_path} for malware threats...")
        with open(file_path, "rb") as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()

        response = self.vt_api.get_file_report(file_hash)
        return response

    def check_ip_threat(self, ip_address):
        """
        Checks if an IP address is blacklisted using AbuseIPDB.
        """
        print(f"Checking IP threat intelligence for: {ip_address}")
        response = self.abuse_ipdb.check_ip(ip_address)
        return response

    def check_shodan_vulnerabilities(self, ip_address):
        """
        Uses Shodan to check open ports and vulnerabilities of an IP.
        """
        print(f"Fetching vulnerability report from Shodan for: {ip_address}")
        url = f"https://api.shodan.io/shodan/host/{ip_address}?key={SHODAN_API_KEY}"
        response = requests.get(url)
        return response.json()

    def check_data_breach(self, email):
        """
        Checks if an email has been leaked in data breaches using HaveIBeenPwned.
        """
        print(f"Checking data breach history for email: {email}")
        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
        headers = {"hibp-api-key": HAVEIBENPWNED_API_KEY, "User-Agent": "RLG-Data-Threat-Analyzer"}
        
        response = requests.get(url, headers=headers)
        return response.json()

    def encrypt_threat_report(self, report):
        """
        Encrypts the threat intelligence report.
        """
        fernet = Fernet(self.encryption_key)
        encrypted_report = fernet.encrypt(json.dumps(report).encode())
        return encrypted_report

    def analyze_threats(self, target, target_type="url"):
        """
        Performs a full cybersecurity threat analysis based on the target type.
        """
        results = {}
        if target_type == "url":
            results["virus_total"] = self.scan_url(target)
        elif target_type == "file":
            results["virus_total"] = self.scan_file_hash(target)
        elif target_type == "ip":
            results["abuse_ipdb"] = self.check_ip_threat(target)
            results["shodan"] = self.check_shodan_vulnerabilities(target)
        elif target_type == "email":
            results["haveibeenpwned"] = self.check_data_breach(target)
        
        # Encrypt the report
        encrypted_results = self.encrypt_threat_report(results)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "target": target,
            "target_type": target_type,
            "encrypted_results": encrypted_results
        }

if __name__ == "__main__":
    cta = CyberThreatAnalysis()
    test_ip = "8.8.8.8"
    analysis_report = cta.analyze_threats(test_ip, "ip")
    print("Threat Analysis Completed:", analysis_report)

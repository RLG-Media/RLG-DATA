import os
import json
import requests
from datetime import datetime
from langdetect import detect
from bs4 import BeautifulSoup
from legal_compliance_checker import LegalComplianceChecker

# API Keys from Environment Variables
GPT_API_KEY = os.getenv("OPENAI_API_KEY")
REGULATORY_API_KEY = os.getenv("REGULATORY_COMPLIANCE_API_KEY")

# Supported Social Media & Web Platforms
PLATFORMS = [
    "Twitter", "Facebook", "Instagram", "LinkedIn", "TikTok", "Pinterest",
    "Reddit", "Snapchat", "Threads", "YouTube", "News Websites", "Blogs"
]

# Compliance Standards to Check
COMPLIANCE_STANDARDS = {
    "GDPR": "European Union Data Protection",
    "POPIA": "South Africa’s Protection of Personal Information Act",
    "CCPA": "California Consumer Privacy Act",
    "HIPAA": "Health Insurance Portability and Accountability Act",
    "COPPA": "Children’s Online Privacy Protection Act"
}

class AutomatedLegalAudit:
    def __init__(self):
        self.legal_checker = LegalComplianceChecker()

    def fetch_terms_and_policies(self, platform):
        """
        Fetches the latest Terms of Service and Privacy Policies from the official website.
        """
        policy_urls = {
            "Twitter": "https://twitter.com/en/tos",
            "Facebook": "https://www.facebook.com/policies",
            "Instagram": "https://help.instagram.com/581066165581870",
            "LinkedIn": "https://www.linkedin.com/legal/privacy-policy",
            "TikTok": "https://www.tiktok.com/legal/privacy-policy",
            "Pinterest": "https://policy.pinterest.com/en/privacy-policy",
            "Reddit": "https://www.redditinc.com/policies/privacy-policy",
            "Snapchat": "https://www.snap.com/en-US/privacy/privacy-policy",
            "Threads": "https://help.instagram.com/769983657850450",
            "YouTube": "https://www.youtube.com/t/terms"
        }

        url = policy_urls.get(platform)
        if not url:
            return "No policy URL available for this platform."

        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                return soup.get_text()
            else:
                return f"Failed to fetch policy for {platform}"
        except Exception as e:
            return f"Error fetching policy for {platform}: {e}"

    def check_compliance(self, policy_text, region="global"):
        """
        Checks the provided policy text against different compliance standards.
        """
        results = {}
        for standard, description in COMPLIANCE_STANDARDS.items():
            compliance_result = self.legal_checker.analyze_text(policy_text, standard)
            results[standard] = compliance_result
        
        return {
            "region": region,
            "compliance_check": results,
            "timestamp": datetime.utcnow().isoformat()
        }

    def analyze_platform_legality(self, platform, region="global"):
        """
        Fetches terms & policies for a given platform and performs a compliance check.
        """
        policy_text = self.fetch_terms_and_policies(platform)
        if "Failed" in policy_text or "Error" in policy_text:
            return {"error": policy_text}

        compliance_report = self.check_compliance(policy_text, region)
        return {
            "platform": platform,
            "region": region,
            "report": compliance_report
        }

    def detect_language(self, text):
        """
        Detect the language of the given text.
        """
        try:
            return detect(text)
        except Exception:
            return "unknown"

    def generate_audit_summary(self, platforms=PLATFORMS, region="global"):
        """
        Runs an automated legal audit for all supported platforms.
        """
        audit_results = []
        for platform in platforms:
            audit_results.append(self.analyze_platform_legality(platform, region))
        
        return {
            "audit_timestamp": datetime.utcnow().isoformat(),
            "region": region,
            "audit_results": audit_results
        }

if __name__ == "__main__":
    auditor = AutomatedLegalAudit()
    full_audit = auditor.generate_audit_summary(region="South Africa")
    print(json.dumps(full_audit, indent=4))

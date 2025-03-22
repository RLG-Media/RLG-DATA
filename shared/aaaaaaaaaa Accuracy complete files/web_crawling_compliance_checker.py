import requests
import re
from urllib.parse import urljoin, urlparse
import time

class WebCrawlingComplianceChecker:
    def __init__(self):
        self.user_agent = "RLGDataBot/1.0 (+https://rlgdata.com/bot-info)"
        self.robots_cache = {}
        self.compliance_violations = []

    def fetch_robots_txt(self, url):
        """
        Fetches and parses the robots.txt file of a given domain.
        """
        domain = urlparse(url).netloc
        if domain in self.robots_cache:
            return self.robots_cache[domain]

        robots_url = urljoin(url, "/robots.txt")
        try:
            response = requests.get(robots_url, headers={"User-Agent": self.user_agent}, timeout=5)
            if response.status_code == 200:
                rules = self.parse_robots_txt(response.text)
                self.robots_cache[domain] = rules
                return rules
        except requests.exceptions.RequestException:
            pass
        
        return {}

    def parse_robots_txt(self, robots_txt):
        """
        Parses robots.txt and extracts disallowed paths.
        """
        rules = {"User-agent": {}, "Crawl-delay": {}}
        current_user_agent = None

        for line in robots_txt.split("\n"):
            line = line.strip()
            if line.startswith("#") or not line:
                continue

            if line.lower().startswith("user-agent:"):
                current_user_agent = line.split(":")[1].strip()
                rules["User-agent"][current_user_agent] = []
            elif line.lower().startswith("disallow:") and current_user_agent:
                disallowed_path = line.split(":")[1].strip()
                rules["User-agent"][current_user_agent].append(disallowed_path)
            elif line.lower().startswith("crawl-delay:") and current_user_agent:
                rules["Crawl-delay"][current_user_agent] = int(line.split(":")[1].strip())

        return rules

    def is_crawling_allowed(self, url):
        """
        Checks if the given URL is allowed to be crawled.
        """
        domain = urlparse(url).netloc
        rules = self.fetch_robots_txt(url)

        if "User-agent" in rules:
            disallowed_paths = rules["User-agent"].get("*", [])
            for path in disallowed_paths:
                if urlparse(url).path.startswith(path):
                    self.compliance_violations.append(f"⚠️ Crawling disallowed for: {url}")
                    return False

        return True

    def get_crawl_delay(self, url):
        """
        Retrieves the crawl delay specified in robots.txt.
        """
        domain = urlparse(url).netloc
        rules = self.fetch_robots_txt(url)

        return rules["Crawl-delay"].get("*", 0)

    def check_compliance(self, url):
        """
        Runs a full compliance check on the given URL.
        """
        if not self.is_crawling_allowed(url):
            return {"status": "Disallowed", "reason": "robots.txt restrictions"}

        delay = self.get_crawl_delay(url)
        if delay:
            time.sleep(delay)  # Respect crawl delay

        return {"status": "Allowed", "crawl-delay": delay}

    def log_violations(self):
        """
        Logs all compliance violations found during crawling.
        """
        if self.compliance_violations:
            print("\n".join(self.compliance_violations))
        else:
            print("✅ No compliance violations detected.")

if __name__ == "__main__":
    checker = WebCrawlingComplianceChecker()

    urls_to_check = [
        "https://www.example.com",
        "https://www.reddit.com",
        "https://www.twitter.com"
    ]

    for url in urls_to_check:
        result = checker.check_compliance(url)
        print(f"Checked {url}: {result}")

    checker.log_violations()

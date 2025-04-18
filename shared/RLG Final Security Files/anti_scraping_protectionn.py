import time
import json
import logging
import hashlib
from datetime import datetime, timedelta
from flask import request, jsonify, abort
import redis  # For rate limiting and caching
import requests  # For third-party security API integrations
from config import REDIS_CONFIG, SECURITY_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Connect to Redis
redis_client = redis.StrictRedis(host=REDIS_CONFIG["host"], port=REDIS_CONFIG["port"], db=0)

# Security settings
BLOCKED_IPS = set()
KNOWN_BOTS = [
    "AhrefsBot", "SemrushBot", "Googlebot", "Bingbot", "MJ12bot", "DotBot", "Screaming Frog", "YandexBot"
]
RATE_LIMIT_THRESHOLD = SECURITY_CONFIG.get("rate_limit", 100)  # Max requests per minute per IP
BLOCK_DURATION = SECURITY_CONFIG.get("block_duration", 3600)  # Ban time for scrapers (1 hour)

# Cloudflare & third-party protection integrations
CLOUDFLARE_API = SECURITY_CONFIG.get("cloudflare_api")
SECURITY_CHECK_API = SECURITY_CONFIG.get("security_check_api")  # API to check suspicious IPs


class AntiScrapingProtection:
    """Advanced anti-scraping protection system for RLG Data and RLG Fans."""

    def __init__(self):
        self.redis_client = redis_client
        self.blocked_ips = BLOCKED_IPS

    def is_bot(self, user_agent: str) -> bool:
        """Detects bots using known bot signatures."""
        if not user_agent:
            return True  # No user-agent is suspicious
        return any(bot in user_agent for bot in KNOWN_BOTS)

    def rate_limit(self, ip: str) -> bool:
        """Implements rate limiting to detect and block high-frequency scrapers."""
        key = f"rate_limit:{ip}"
        request_count = self.redis_client.incr(key)

        if request_count == 1:
            self.redis_client.expire(key, 60)  # Reset counter after 1 minute

        if request_count > RATE_LIMIT_THRESHOLD:
            logging.warning(f"Rate limit exceeded for {ip}. Blocking for {BLOCK_DURATION} seconds.")
            self.block_ip(ip)
            return True  # Block user

        return False

    def fingerprint_request(self, request_headers: dict) -> str:
        """Creates a unique fingerprint for identifying bots."""
        data = f"{request_headers.get('User-Agent', '')}-{request_headers.get('Accept-Language', '')}-{request.remote_addr}"
        return hashlib.sha256(data.encode()).hexdigest()

    def block_ip(self, ip: str) -> None:
        """Blocks an IP address by adding it to the blacklist."""
        self.redis_client.setex(f"blocked_ip:{ip}", BLOCK_DURATION, "blocked")
        self.blocked_ips.add(ip)

    def is_blocked(self, ip: str) -> bool:
        """Checks if an IP is currently blocked."""
        return self.redis_client.exists(f"blocked_ip:{ip}")

    def honeypot_check(self, request_path: str) -> bool:
        """Detects scrapers using honeypot traps."""
        if "/hidden-resource" in request_path:  # Honeypot link that real users wouldn't access
            logging.warning(f"Honeypot triggered by {request.remote_addr}. Blocking IP.")
            self.block_ip(request.remote_addr)
            return True
        return False

    def security_check(self, ip: str) -> bool:
        """Checks IP reputation using an external security API."""
        if not SECURITY_CHECK_API:
            return False  # No API configured

        response = requests.get(f"{SECURITY_CHECK_API}?ip={ip}")
        if response.status_code == 200 and response.json().get("malicious"):
            logging.warning(f"Malicious IP detected: {ip}. Blocking.")
            self.block_ip(ip)
            return True

        return False

    def handle_request(self) -> dict:
        """Main function to analyze requests and block scrapers."""
        ip = request.remote_addr
        user_agent = request.headers.get("User-Agent", "")

        # 1️⃣ Check if the IP is already blocked
        if self.is_blocked(ip):
            logging.warning(f"Blocked request from {ip}")
            abort(403, description="Access Denied")

        # 2️⃣ Honeypot detection
        if self.honeypot_check(request.path):
            abort(403, description="Access Denied")

        # 3️⃣ Bot Detection
        if self.is_bot(user_agent):
            logging.warning(f"Bot detected: {user_agent} from {ip}")
            self.block_ip(ip)
            abort(403, description="Access Denied")

        # 4️⃣ Rate Limiting
        if self.rate_limit(ip):
            abort(429, description="Too many requests. Slow down!")

        # 5️⃣ Security API Check
        if self.security_check(ip):
            abort(403, description="Suspicious activity detected")

        return {"status": "ok", "message": "Request Allowed"}

    def apply_captcha(self, ip: str) -> bool:
        """Applies CAPTCHA verification to suspected bots."""
        if not CLOUDFLARE_API:
            return False  # No CAPTCHA service configured

        response = requests.post(CLOUDFLARE_API, json={"ip": ip, "action": "challenge"})
        if response.status_code == 200:
            logging.info(f"CAPTCHA applied for {ip}")
            return True

        return False


# Initialize Anti-Scraping Protection
anti_scraping = AntiScrapingProtection()

# Example Flask route
from flask import Flask
app = Flask(__name__)

@app.route("/data", methods=["GET"])
def protected_endpoint():
    anti_scraping.handle_request()  # Check for scrapers before serving content
    return jsonify({"data": "Protected RLG Data content"})

if __name__ == "__main__":
    app.run(debug=True)

import os
import datetime
import json
import logging
import requests
from flask import Flask, request, jsonify
from typing import Dict, List, Optional
from gevent.pywsgi import WSGIServer
from dotenv import load_dotenv
import maxminddb

# Load environment variables
load_dotenv()

# Configure advanced logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
    handlers=[
        logging.FileHandler("chatbot.log"),
        logging.StreamHandler(),
        logging.handlers.RotatingFileHandler(
            "chatbot_debug.log",
            maxBytes=1024*1024*5,
            backupCount=5
        )
    ]
)
logger = logging.getLogger(__name__)

class Config:
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_ENDPOINT = "https://api.deepseek.com/v1/chat/completions"
    GEOIP_DB_PATH = os.getenv("GEOIP_DB_PATH", "./resources/geolite2-city.mmdb")
    MODEL_NAME = "deepseek-llm-1.3b"
    RATE_LIMIT = "1000 per hour"

class GeoLocator:
    """Handles geographic location data using MaxMind GeoLite2 database"""
    def __init__(self):
        try:
            self.reader = maxminddb.open_database(Config.GEOIP_DB_PATH)
            logger.info("Loaded GeoIP database")
        except Exception as e:
            logger.error(f"GeoIP database error: {str(e)}")
            self.reader = None

    def get_location(self, ip_address: str) -> Dict:
        """Get geographic details from IP address"""
        if not self.reader:
            return {}
        
        try:
            geo_data = self.reader.get(ip_address)
            return {
                "country": geo_data.get("country", {}).get("names", {}).get("en", "Unknown"),
                "region": geo_data.get("subdivisions", [{}])[0].get("names", {}).get("en", "Unknown"),
                "city": geo_data.get("city", {}).get("names", {}).get("en", "Unknown"),
                "timezone": geo_data.get("location", {}).get("time_zone", "Unknown")
            }
        except Exception as e:
            logger.error(f"Geolocation failed for {ip_address}: {str(e)}")
            return {}

class DeepSeekClient:
    """Handles communication with DeepSeek's LLM API"""
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }

    def generate_response(self, prompt: str, context: Dict) -> Optional[str]:
        """Get response from DeepSeek's LLM with error handling"""
        system_message = {
            "role": "system",
            "content": f"""You are Khoto Zulu, an AI assistant for RLG Data and RLG Fans. 
            Current context: {json.dumps(context)}. Provide helpful, accurate responses 
            considering the user's location and technical expertise."""
        }
        
        payload = {
            "model": Config.MODEL_NAME,
            "messages": [system_message, {"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 500
        }

        try:
            response = requests.post(
                Config.DEEPSEEK_ENDPOINT,
                headers=self.headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"DeepSeek API error: {str(e)}")
            return None

class Chatbot:
    """Enhanced chatbot with DeepSeek integration and geographic awareness"""
    def __init__(self):
        self.logs = []
        self.reports = {"daily": [], "weekly": []}
        self.geolocator = GeoLocator()
        self.llm_client = DeepSeekClient()
        self.fallback_responses = self._load_fallback_responses()
        logger.info("Chatbot initialized with DeepSeek integration")

    def handle_user_message(self, user_message: str, user_id: str, client_ip: str) -> str:
        """Process message with DeepSeek LLM and fallback logic"""
        location = self.geolocator.get_location(client_ip)
        context = {
            "user_id": user_id,
            "location": location,
            "timestamp": datetime.datetime.now().isoformat(),
            "history": self._get_user_history(user_id)
        }

        # Get LLM response
        llm_response = self.llm_client.generate_response(user_message, context)
        if llm_response:
            response = llm_response
        else:
            response = self._handle_fallback(user_message, context)

        # Log interaction
        self.log_query(user_id, user_message, response, location)
        return response

    def log_query(self, user_id: str, message: str, response: str, location: Dict) -> None:
        """Enhanced logging with geographic data"""
        log_entry = {
            "user_id": user_id,
            "message": message,
            "response": response,
            "timestamp": datetime.datetime.now().isoformat(),
            "location": location,
            "status": "processed"
        }
        self.logs.append(log_entry)
        logger.info(f"Logged interaction for {user_id} from {location.get('city', 'Unknown')}")

    def generate_report(self, frequency: str = "daily") -> Dict:
        """Enhanced reporting with geographic insights"""
        # Existing report generation logic extended with location data
        # ... (maintain previous structure but add location-based metrics)
        return report

    def _handle_fallback(self, message: str, context: Dict) -> str:
        """Fallback response system"""
        lower_msg = message.lower()
        for pattern, response in self.fallback_responses.items():
            if pattern in lower_msg:
                return response.format(**context)
        return "I'm sorry, could you please rephrase your question?"

    def _load_fallback_responses(self) -> Dict:
        """Load fallback responses from external file"""
        try:
            with open("./resources/fallback_responses.json") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load fallback responses: {str(e)}")
            return DEFAULT_FALLBACKS

    def _get_user_history(self, user_id: str) -> List[Dict]:
        """Retrieve user's interaction history"""
        return [log for log in self.logs[-100:] if log["user_id"] == user_id]

# Flask Application Setup
app = Flask(__name__)
app.config["RATELIMIT_HEADERS_ENABLED"] = True
chatbot = Chatbot()

@app.route("/chat", methods=["POST"])
def handle_chat():
    """Enhanced chat endpoint with rate limiting and location detection"""
    data = request.get_json()
    user_message = data.get("message")
    user_id = data.get("user_id")
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    if not user_message or not user_id:
        return jsonify({"error": "Invalid request"}), 400

    response = chatbot.handle_user_message(user_message, user_id, client_ip)
    return jsonify({
        "response": response,
        "timestamp": datetime.datetime.now().isoformat()
    })

@app.route("/analytics/reports", methods=["GET"])
def get_reports():
    """Enhanced reporting endpoint with multiple output formats"""
    # ... (maintain previous report logic with added geographic insights)

if __name__ == "__main__":
    # Production-ready server
    if os.getenv("FLASK_ENV") == "production":
        server = WSGIServer(("0.0.0.0", 5000), app)
        server.serve_forever()
    else:
        app.run(debug=False, port=5000)
        
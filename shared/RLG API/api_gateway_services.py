import logging
import time
from flask import Flask, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("api_gateway_services.log"),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)

# API Gateway configurations
RATE_LIMIT = 100  # Number of requests allowed per minute per IP
CACHE_TTL = 300   # Time-to-live for cached responses in seconds
SUPPORTED_SERVICES = {
    "twitter": "http://twitter_service:5000",
    "facebook": "http://facebook_service:5000",
    "instagram": "http://instagram_service:5000",
    "linkedin": "http://linkedin_service:5000",
    "tiktok": "http://tiktok_service:5000",
    "pinterest": "http://pinterest_service:5000",
    "reddit": "http://reddit_service:5000",
    "snapchat": "http://snapchat_service:5000",
    "threads": "http://threads_service:5000",
    "reporting": "http://reporting_service:5000",
    "analytics": "http://analytics_service:5000"
}

# In-memory store for rate limiting and caching
rate_limit_store = {}
cached_responses = {}

@app.before_request
def enforce_rate_limiting():
    client_ip = request.remote_addr
    current_time = time.time()

    if client_ip not in rate_limit_store:
        rate_limit_store[client_ip] = []

    request_times = rate_limit_store[client_ip]
    request_times = [t for t in request_times if current_time - t < 60]

    if len(request_times) >= RATE_LIMIT:
        logging.warning(f"Rate limit exceeded for IP: {client_ip}")
        return jsonify({"error": "Rate limit exceeded. Try again later."}), 429

    request_times.append(current_time)
    rate_limit_store[client_ip] = request_times

@app.route("/gateway/<service_name>/<path:subpath>", methods=["GET", "POST", "PUT", "DELETE"])
def gateway(service_name, subpath):
    if service_name not in SUPPORTED_SERVICES:
        logging.error(f"Service '{service_name}' is not supported.")
        return jsonify({"error": f"Service '{service_name}' not supported."}), 404

    service_url = SUPPORTED_SERVICES[service_name]
    target_url = f"{service_url}/{subpath}"

    # Check for cached responses (GET only)
    cache_key = f"{service_name}:{subpath}:{request.method}:{request.query_string}"
    if request.method == "GET" and cache_key in cached_responses:
        cached_response, cached_time = cached_responses[cache_key]
        if time.time() - cached_time < CACHE_TTL:
            logging.info(f"Cache hit for {cache_key}")
            return jsonify(cached_response)

    # Forward the request to the target service
    try:
        if request.method == "GET":
            response = requests.get(target_url, params=request.args)
        elif request.method == "POST":
            response = requests.post(target_url, json=request.json)
        elif request.method == "PUT":
            response = requests.put(target_url, json=request.json)
        elif request.method == "DELETE":
            response = requests.delete(target_url, params=request.args)
        else:
            logging.error("Unsupported HTTP method.")
            return jsonify({"error": "Unsupported HTTP method."}), 405

        # Cache the response (GET only)
        if request.method == "GET" and response.status_code == 200:
            cached_responses[cache_key] = (response.json(), time.time())

        return jsonify(response.json()), response.status_code
    except Exception as e:
        logging.error(f"Failed to proxy request to {target_url}: {e}")
        return jsonify({"error": "Failed to process the request."}), 500

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "API Gateway is running."}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

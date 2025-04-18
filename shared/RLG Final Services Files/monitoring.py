import os
import time
import psutil
import platform
from flask import Flask, jsonify, request
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CollectorRegistry,
)
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

# Initialize Sentry for error tracking
if os.getenv("ENABLE_SENTRY", "false").lower() == "true":
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[FlaskIntegration()],
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", 1.0)),
    )

# Prometheus Metrics
REGISTRY = CollectorRegistry()

REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP Requests", ["method", "endpoint"], registry=REGISTRY
)
REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds", "Latency of HTTP Requests", ["method", "endpoint"], registry=REGISTRY
)
CPU_USAGE = Gauge("system_cpu_usage_percent", "System CPU Usage", registry=REGISTRY)
MEMORY_USAGE = Gauge("system_memory_usage_percent", "System Memory Usage", registry=REGISTRY)
DISK_USAGE = Gauge("system_disk_usage_percent", "System Disk Usage", registry=REGISTRY)

def monitor_system():
    """
    Collects system-level metrics like CPU, memory, and disk usage.
    """
    CPU_USAGE.set(psutil.cpu_percent(interval=1))
    MEMORY_USAGE.set(psutil.virtual_memory().percent)
    DISK_USAGE.set(psutil.disk_usage("/").percent)

def prometheus_metrics():
    """
    Endpoint for Prometheus to scrape metrics.
    """
    monitor_system()
    return generate_latest(REGISTRY), 200, {"Content-Type": "text/plain"}

def setup_monitoring(app: Flask):
    """
    Sets up monitoring for the Flask application.

    Args:
        app (Flask): The Flask application instance.
    """

    @app.before_request
    def start_timer():
        """
        Records the start time of each request.
        """
        request.start_time = time.time()

    @app.after_request
    def log_request_metrics(response):
        """
        Logs request metrics after each request.
        """
        if hasattr(request, "start_time"):
            request_latency = time.time() - request.start_time
            REQUEST_LATENCY.labels(method=request.method, endpoint=request.path).observe(request_latency)
            REQUEST_COUNT.labels(method=request.method, endpoint=request.path).inc()
        return response

    @app.route("/health", methods=["GET"])
    def health_check():
        """
        Health check endpoint for the application.
        """
        status = {
            "status": "healthy",
            "uptime": time.time() - psutil.boot_time(),
            "system": {
                "cpu": psutil.cpu_percent(),
                "memory": psutil.virtual_memory().percent,
                "disk": psutil.disk_usage("/").percent,
                "platform": platform.system(),
                "version": platform.version(),
                "python_version": platform.python_version(),
            },
        }
        return jsonify(status), 200

    @app.route("/metrics", methods=["GET"])
    def metrics():
        """
        Metrics endpoint for Prometheus scraping.
        """
        return prometheus_metrics()

    # Log application startup
    app.logger.info("Monitoring setup complete. Metrics available at /metrics and health check at /health.")


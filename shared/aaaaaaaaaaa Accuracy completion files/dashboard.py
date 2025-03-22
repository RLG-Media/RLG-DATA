"""
dashboard.py

This module defines a Flask blueprint that serves the main dashboard page for the RLG Platform,
aggregating key metrics from both RLG Data (media articles) and RLG Fans (social posts).

It queries the database using DatabaseManager, computes summary statistics, and renders a dashboard
template with these metrics.
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime

# Import our DatabaseManager from the previously defined module.
from database_manager import DatabaseManager

# Configure logging for the dashboard module.
logger = logging.getLogger("Dashboard")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

# Create a Flask blueprint for the dashboard.
dashboard_bp = Blueprint("dashboard", __name__, template_folder="templates", url_prefix="/dashboard")

# Instantiate the database manager (ensure the database is properly configured).
db_manager = DatabaseManager()

@dashboard_bp.route("/", methods=["GET"])
def show_dashboard():
    """
    Dashboard route that aggregates key metrics and renders the dashboard page.
    
    Aggregation includes:
      - RLG Data: Total articles and sentiment distribution (positive, neutral, negative).
      - RLG Fans: Total fan posts and average engagement.
      - Last update timestamp.
    
    Returns:
      Rendered dashboard template with aggregated metrics.
    """
    try:
        # Query RLG Data records (optionally, a region filter can be applied).
        rlg_data_records = db_manager.query_rlg_data(region="default")
        total_articles = len(rlg_data_records)

        # Initialize sentiment counters.
        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}

        # Count sentiments in RLG Data. If sentiment is not one of the keys, default to "neutral".
        for record in rlg_data_records:
            sentiment = record.sentiment.lower() if record.sentiment else "neutral"
            if sentiment in sentiment_counts:
                sentiment_counts[sentiment] += 1
            else:
                sentiment_counts["neutral"] += 1

        # Query RLG Fans records.
        rlg_fans_records = db_manager.query_rlg_fans(region="default")
        total_fans = len(rlg_fans_records)

        # Calculate average engagement from RLG Fans records.
        total_engagement = sum(record.engagement for record in rlg_fans_records)
        avg_engagement = total_engagement / total_fans if total_fans > 0 else 0

        # Prepare the dashboard metrics dictionary.
        dashboard_metrics = {
            "rlg_data": {
                "total_articles": total_articles,
                "positive": sentiment_counts.get("positive", 0),
                "neutral": sentiment_counts.get("neutral", 0),
                "negative": sentiment_counts.get("negative", 0)
            },
            "rlg_fans": {
                "total_fans": total_fans,
                "average_engagement": round(avg_engagement, 2)
            },
            "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        }

        logger.info("Dashboard metrics computed successfully: %s", dashboard_metrics)
        # Render the dashboard template (e.g., dashboard.html) and pass the metrics.
        return render_template("dashboard.html", metrics=dashboard_metrics)
    except Exception as e:
        logger.error("Error generating dashboard: %s", e)
        flash("Error generating dashboard.", "danger")
        return redirect(url_for("index"))

# Standalone testing of the dashboard blueprint.
if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    app.secret_key = "supersecretkey"  # For development purposes.
    app.register_blueprint(dashboard_bp)
    
    # Minimal route for home (redirecting to dashboard).
    @app.route("/")
    def index():
        return redirect(url_for("dashboard.show_dashboard"))
    
    app.run(host="0.0.0.0", port=5005, debug=True)

import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import psycopg2  # PostgreSQL for storing analytics data
from pymongo import MongoClient  # Optional MongoDB for large-scale analytics
import redis  # Caching for performance
import requests  # For third-party integrations
from config import DATABASE_CONFIG, MONGO_CONFIG, REDIS_CONFIG, API_KEYS

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Connect to PostgreSQL for structured analytics data
pg_conn = psycopg2.connect(**DATABASE_CONFIG)
pg_cursor = pg_conn.cursor()

# Connect to MongoDB for NoSQL-based analytics (optional)
mongo_client = MongoClient(MONGO_CONFIG["uri"])
mongo_db = mongo_client[MONGO_CONFIG["database"]]
mongo_collection = mongo_db["analytics"]

# Connect to Redis for caching
redis_client = redis.StrictRedis(host=REDIS_CONFIG["host"], port=REDIS_CONFIG["port"], db=0)

# Define analytics event types
EVENT_TYPES = [
    "page_view", "click", "form_submission", "purchase",
    "api_request", "data_scrape", "user_registration",
    "login", "logout", "subscription_change"
]

# Third-party integrations
INTEGRATIONS = {
    "google_analytics": API_KEYS.get("GOOGLE_ANALYTICS"),
    "slack": API_KEYS.get("SLACK_WEBHOOK"),
    "zapier": API_KEYS.get("ZAPIER_WEBHOOK")
}


class AnalyticsService:
    """Analytics service to track, process, and report user activities."""

    def __init__(self):
        self.pg_conn = pg_conn
        self.pg_cursor = pg_cursor
        self.mongo_collection = mongo_collection
        self.redis_client = redis_client

    def track_event(self, user_id: str, event_type: str, metadata: Dict[str, Any] = None) -> None:
        """Tracks a user event in both SQL and NoSQL databases."""
        if event_type not in EVENT_TYPES:
            logging.warning(f"Invalid event type: {event_type}")
            return

        timestamp = datetime.utcnow()
        metadata = metadata or {}

        # Store in PostgreSQL
        self.pg_cursor.execute("""
            INSERT INTO analytics (user_id, event_type, metadata, timestamp)
            VALUES (%s, %s, %s, %s)
        """, (user_id, event_type, json.dumps(metadata), timestamp))
        self.pg_conn.commit()

        # Store in MongoDB for large-scale analytics
        self.mongo_collection.insert_one({
            "user_id": user_id,
            "event_type": event_type,
            "metadata": metadata,
            "timestamp": timestamp
        })

        # Store in Redis for caching recent events
        redis_key = f"analytics:{user_id}:{event_type}"
        self.redis_client.setex(redis_key, timedelta(hours=1), json.dumps(metadata))

        logging.info(f"Tracked event: {event_type} for user {user_id}")

    def get_user_activity(self, user_id: str, period_days: int = 7) -> List[Dict[str, Any]]:
        """Retrieves user activity from analytics data."""
        start_date = datetime.utcnow() - timedelta(days=period_days)

        self.pg_cursor.execute("""
            SELECT event_type, metadata, timestamp
            FROM analytics
            WHERE user_id = %s AND timestamp >= %s
        """, (user_id, start_date))

        results = self.pg_cursor.fetchall()
        return [{"event_type": row[0], "metadata": json.loads(row[1]), "timestamp": row[2]} for row in results]

    def get_trending_events(self, period_days: int = 7) -> Dict[str, int]:
        """Returns the most popular events in the system."""
        start_date = datetime.utcnow() - timedelta(days=period_days)

        self.pg_cursor.execute("""
            SELECT event_type, COUNT(*) as count
            FROM analytics
            WHERE timestamp >= %s
            GROUP BY event_type
            ORDER BY count DESC
        """, (start_date,))

        results = self.pg_cursor.fetchall()
        return {row[0]: row[1] for row in results}

    def generate_report(self, user_id: str, period_days: int = 30) -> Dict[str, Any]:
        """Generates a detailed analytics report for a user."""
        user_activity = self.get_user_activity(user_id, period_days)
        total_events = len(user_activity)
        event_breakdown = {}

        for event in user_activity:
            event_type = event["event_type"]
            event_breakdown[event_type] = event_breakdown.get(event_type, 0) + 1

        return {
            "user_id": user_id,
            "total_events": total_events,
            "event_breakdown": event_breakdown,
            "report_generated_at": datetime.utcnow().isoformat()
        }

    def integrate_with_third_party(self, event_data: Dict[str, Any]) -> None:
        """Sends analytics data to third-party platforms (Google Analytics, Slack, Zapier)."""
        if INTEGRATIONS["google_analytics"]:
            requests.post(INTEGRATIONS["google_analytics"], json=event_data)

        if INTEGRATIONS["slack"]:
            requests.post(INTEGRATIONS["slack"], json={"text": f"New Event: {event_data}"})

        if INTEGRATIONS["zapier"]:
            requests.post(INTEGRATIONS["zapier"], json=event_data)

        logging.info("Event data sent to third-party integrations.")

    def cleanup_old_data(self, retention_days: int = 90) -> None:
        """Deletes old analytics data from the database to save storage."""
        delete_before = datetime.utcnow() - timedelta(days=retention_days)

        self.pg_cursor.execute("""
            DELETE FROM analytics WHERE timestamp < %s
        """, (delete_before,))
        self.pg_conn.commit()

        mongo_query = {"timestamp": {"$lt": delete_before}}
        self.mongo_collection.delete_many(mongo_query)

        logging.info(f"Deleted analytics data older than {retention_days} days.")


# Initialize the analytics service
analytics_service = AnalyticsService()

if __name__ == "__main__":
    # Example usage
    analytics_service.track_event(user_id="12345", event_type="page_view", metadata={"page": "dashboard"})
    report = analytics_service.generate_report(user_id="12345")
    print(json.dumps(report, indent=2))

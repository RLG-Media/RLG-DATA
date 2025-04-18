import os
import json
import logging
import time
import requests
import hashlib
import redis
import threading
import pandas as pd
from datetime import datetime
from kafka import KafkaProducer, KafkaConsumer
from celery import Celery
from typing import Dict, List, Optional
from sqlalchemy import create_engine

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("data_aggregation.log"), logging.StreamHandler()]
)

# Configuration
KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "rlg_data_aggregation"
REDIS_HOST = "localhost"
REDIS_PORT = 6379
CELERY_BROKER = "redis://localhost:6379/0"
DATABASE_URI = "postgresql://user:password@localhost/rlg_data"

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# Initialize Redis
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)

# Initialize Celery
celery_app = Celery("data_aggregation", broker=CELERY_BROKER)

# Database Connection
engine = create_engine(DATABASE_URI)

# Data Sources
DATA_SOURCES = {
    "twitter": "https://api.twitter.com/2/tweets/search/recent",
    "facebook": "https://graph.facebook.com/v17.0",
    "instagram": "https://graph.instagram.com",
    "linkedin": "https://api.linkedin.com/v2/",
    "newsapi": "https://newsapi.org/v2/everything",
    "reddit": "https://www.reddit.com/r/all.json",
    "tiktok": "https://www.tiktok.com/api",
    "pinterest": "https://api.pinterest.com/v5/search",
}

# API Keys (Ensure they are securely stored in environment variables)
API_KEYS = {
    "twitter": os.getenv("TWITTER_API_KEY"),
    "facebook": os.getenv("FACEBOOK_API_KEY"),
    "instagram": os.getenv("INSTAGRAM_API_KEY"),
    "linkedin": os.getenv("LINKEDIN_API_KEY"),
    "newsapi": os.getenv("NEWS_API_KEY"),
    "reddit": os.getenv("REDDIT_API_KEY"),
    "tiktok": os.getenv("TIKTOK_API_KEY"),
    "pinterest": os.getenv("PINTEREST_API_KEY"),
}

class DataAggregationPipeline:
    """
    Aggregates, processes, and stores data from multiple sources for RLG Data and RLG Fans.
    """

    def fetch_data(self, source: str, params: Optional[Dict] = None) -> Dict:
        """Fetches data from the specified source API."""
        if source not in DATA_SOURCES:
            logging.error(f"❌ Unsupported data source: {source}")
            return {}

        url = DATA_SOURCES[source]
        headers = {"Authorization": f"Bearer {API_KEYS.get(source, '')}"}
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            logging.info(f"✅ Successfully fetched data from {source}")
            return response.json()
        except requests.RequestException as e:
            logging.error(f"⚠️ Failed to fetch data from {source}: {e}")
            return {}

    def normalize_data(self, raw_data: Dict, source: str) -> List[Dict]:
        """Normalizes raw data into a consistent format."""
        normalized_data = []
        timestamp = datetime.utcnow().isoformat()
        for item in raw_data.get("data", []):
            normalized_entry = {
                "id": hashlib.md5(item.get("id", "").encode()).hexdigest(),
                "source": source,
                "content": item.get("text") or item.get("content") or "",
                "author": item.get("user", {}).get("username", "Unknown"),
                "timestamp": timestamp,
                "region": "Global",
            }
            normalized_data.append(normalized_entry)
        return normalized_data

    def store_data(self, data: List[Dict]):
        """Stores normalized data in PostgreSQL."""
        if not data:
            return

        df = pd.DataFrame(data)
        df.to_sql("aggregated_data", con=engine, if_exists="append", index=False)
        logging.info(f"✅ Stored {len(data)} records in database.")

    def push_to_kafka(self, data: List[Dict]):
        """Pushes data to Kafka for distributed processing."""
        for record in data:
            producer.send(KAFKA_TOPIC, value=record)
        logging.info(f"📡 Pushed {len(data)} records to Kafka topic {KAFKA_TOPIC}")

    def cache_data(self, data: List[Dict]):
        """Caches data in Redis for quick retrieval."""
        for record in data:
            redis_client.set(record["id"], json.dumps(record))
        logging.info(f"🚀 Cached {len(data)} records in Redis.")

    def aggregate_from_all_sources(self):
        """Aggregates data from all configured sources."""
        for source in DATA_SOURCES.keys():
            raw_data = self.fetch_data(source)
            normalized_data = self.normalize_data(raw_data, source)
            self.store_data(normalized_data)
            self.push_to_kafka(normalized_data)
            self.cache_data(normalized_data)


@celery_app.task
def run_data_aggregation():
    """Celery task for scheduled aggregation."""
    pipeline = DataAggregationPipeline()
    pipeline.aggregate_from_all_sources()


def start_kafka_consumer():
    """Kafka consumer to process incoming data from the aggregation pipeline."""
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        auto_offset_reset="earliest",
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    )

    for message in consumer:
        data = message.value
        logging.info(f"🔄 Processing Kafka message: {data}")
        redis_client.set(data["id"], json.dumps(data))
        logging.info(f"✅ Data stored in Redis cache: {data['id']}")


if __name__ == "__main__":
    pipeline = DataAggregationPipeline()
    
    # Schedule Aggregation Every 30 Minutes
    schedule_thread = threading.Thread(target=run_data_aggregation)
    schedule_thread.start()

    # Start Kafka Consumer
    kafka_thread = threading.Thread(target=start_kafka_consumer)
    kafka_thread.start()

    logging.info("✅ Data Aggregation Pipeline Running...")

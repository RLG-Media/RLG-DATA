import os
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from kafka import KafkaConsumer
import redis

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("real_time_user_behavior_analysis.log"), logging.StreamHandler()]
)

# Database Connection
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///user_behavior.db")
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# Redis Connection for Fast Caching
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

# Kafka Consumer for Real-Time Data Ingestion
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC = "user_behavior"
consumer = KafkaConsumer(KAFKA_TOPIC, bootstrap_servers=KAFKA_BROKER, auto_offset_reset="latest")

# User Behavior Model
class UserBehavior(Base):
    __tablename__ = "user_behavior"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    action = Column(String, nullable=False)
    session_duration = Column(Float, default=0.0)
    click_rate = Column(Float, default=0.0)
    engagement_score = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)

# Fetch Recent User Behavior Data
def fetch_user_behavior():
    """Retrieves the last 90 days of user behavior data."""
    query = session.query(UserBehavior).order_by(UserBehavior.timestamp.desc()).limit(5000).all()
    return pd.DataFrame([{col.name: getattr(row, col.name) for col in row.__table__.columns} for row in query])

# Preprocess Data for Analysis
def preprocess_data(data):
    """Prepares and normalizes user behavior data for machine learning models."""
    data.fillna(0, inplace=True)
    data["timestamp"] = pd.to_datetime(data["timestamp"])
    data["session_duration"] = data["session_duration"].astype(float)
    data["click_rate"] = data["click_rate"].astype(float)
    data["engagement_score"] = data["engagement_score"].astype(float)
    return data

# Train User Segmentation Model
def train_user_segmentation(data):
    """Clusters users into behavioral segments using K-Means."""
    features = ["session_duration", "click_rate", "engagement_score"]
    model = KMeans(n_clusters=4, random_state=42)
    data["cluster"] = model.fit_predict(data[features])
    return model

# Train Churn Prediction Model
def train_churn_model(data):
    """Trains a Random Forest model to predict user churn."""
    features = ["session_duration", "click_rate", "engagement_score"]
    X = data[features]
    y = (data["session_duration"] < 10).astype(int)  # Assumes churn if session < 10s
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model

# Train LSTM for Behavioral Forecasting
def train_lstm(data):
    """Trains an LSTM model for user engagement predictions."""
    X, y = [], []
    features = ["session_duration", "click_rate", "engagement_score"]
    data_values = data[features].values
    for i in range(5, len(data_values)):
        X.append(data_values[i-5:i])
        y.append(data_values[i][-1])

    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], X.shape[2]))

    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(X.shape[1], X.shape[2])),
        Dropout(0.2),
        LSTM(50, return_sequences=False),
        Dropout(0.2),
        Dense(25),
        Dense(1)
    ])
    model.compile(optimizer="adam", loss="mse")
    model.fit(X, y, epochs=20, batch_size=16, verbose=1)
    return model

# Real-Time User Behavior Processing
def process_real_time_data():
    """Consumes and processes user behavior data from Kafka in real time."""
    for message in consumer:
        user_data = json.loads(message.value)
        user_behavior = UserBehavior(
            user_id=user_data["user_id"],
            platform=user_data["platform"],
            action=user_data["action"],
            session_duration=user_data["session_duration"],
            click_rate=user_data["click_rate"],
            engagement_score=user_data["engagement_score"]
        )
        session.add(user_behavior)
        session.commit()
        redis_client.set(f"user:{user_data['user_id']}:last_action", json.dumps(user_data))
        logging.info(f"✅ Processed user behavior for {user_data['user_id']} on {user_data['platform']}")

# Predict Churn Probability
def predict_churn(user_data, churn_model):
    """Predicts churn risk for a given user using the trained churn model."""
    X_new = np.array([[user_data["session_duration"], user_data["click_rate"], user_data["engagement_score"]]])
    churn_risk = churn_model.predict(X_new)[0]
    return churn_risk

# Run Real-Time Analysis
def run_real_time_user_analysis():
    """Trains models and processes real-time user behavior data."""
    data = fetch_user_behavior()
    if data.empty:
        logging.warning("⚠️ No user behavior data available.")
        return

    data = preprocess_data(data)
    segmentation_model = train_user_segmentation(data)
    churn_model = train_churn_model(data)
    lstm_model = train_lstm(data)

    logging.info("✅ Real-time user behavior analysis models trained.")
    process_real_time_data()

if __name__ == "__main__":
    run_real_time_user_analysis()

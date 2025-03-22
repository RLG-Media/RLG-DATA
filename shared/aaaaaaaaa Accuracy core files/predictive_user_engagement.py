import os
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("predictive_user_engagement.log"), logging.StreamHandler()]
)

# Database Connection
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///predictive_user_engagement.db")
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# Engagement Data Model
class EngagementData(Base):
    __tablename__ = "engagement_data"
    id = Column(Integer, primary_key=True, autoincrement=True)
    platform = Column(String, nullable=False)
    engagement_score = Column(Float, nullable=False)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)

# Fetch Engagement Data
def fetch_engagement_data():
    """Retrieves the last 90 days of engagement data."""
    query = session.query(EngagementData).order_by(EngagementData.timestamp.desc()).limit(90).all()
    return pd.DataFrame([{col.name: getattr(row, col.name) for col in row.__table__.columns} for row in query])

# Preprocess Data for Prediction
def preprocess_data(data):
    """Scales and structures data for predictive models."""
    scaler = MinMaxScaler()
    features = ["likes", "comments", "shares", "engagement_score"]
    data[features] = scaler.fit_transform(data[features])
    return data, scaler

# Train Random Forest Model
def train_random_forest(data):
    """Trains a Random Forest model for engagement prediction."""
    X = data[["likes", "comments", "shares"]]
    y = data["engagement_score"]
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model

# Train XGBoost Model
def train_xgboost(data):
    """Trains an XGBoost model for engagement prediction."""
    X = data[["likes", "comments", "shares"]]
    y = data["engagement_score"]
    model = xgb.XGBRegressor(objective="reg:squarederror", n_estimators=100, random_state=42)
    model.fit(X, y)
    return model

# Train LSTM Deep Learning Model
def train_lstm(data):
    """Trains an LSTM model for time-series engagement forecasting."""
    X, y = [], []
    features = ["likes", "comments", "shares", "engagement_score"]
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

# Predict Engagement
def predict_engagement(platform, rf_model, xgb_model, lstm_model, scaler):
    """Predicts engagement for the next 7 days using all models."""
    recent_data = fetch_engagement_data()
    recent_data, _ = preprocess_data(recent_data)

    X_new = recent_data[["likes", "comments", "shares"]].values[-1].reshape(1, -1)

    rf_prediction = rf_model.predict(X_new)[0]
    xgb_prediction = xgb_model.predict(X_new)[0]

    # LSTM requires time-series input
    X_lstm = np.expand_dims(recent_data[["likes", "comments", "shares", "engagement_score"]].values[-5:], axis=0)
    lstm_prediction = lstm_model.predict(X_lstm)[0][0]

    final_prediction = (rf_prediction + xgb_prediction + lstm_prediction) / 3
    final_prediction = scaler.inverse_transform([[0, 0, 0, final_prediction]])[0][-1]

    logging.info(f"📈 Predicted engagement for {platform}: {final_prediction:.2f}")
    return final_prediction

# Run Engagement Prediction
def run_engagement_prediction():
    """Trains models and generates engagement forecasts for all platforms."""
    data = fetch_engagement_data()
    if data.empty:
        logging.warning("⚠️ No engagement data found.")
        return

    data, scaler = preprocess_data(data)
    rf_model = train_random_forest(data)
    xgb_model = train_xgboost(data)
    lstm_model = train_lstm(data)

    predictions = {}
    for platform in ["facebook", "instagram", "twitter", "tiktok", "linkedin", "youtube",
                     "reddit", "snapchat", "threads", "pinterest"]:
        predictions[platform] = predict_engagement(platform, rf_model, xgb_model, lstm_model, scaler)

    logging.info("✅ Engagement predictions completed.")
    return predictions

if __name__ == "__main__":
    run_engagement_prediction()

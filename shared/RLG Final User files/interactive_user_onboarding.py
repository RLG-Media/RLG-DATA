import os
import json
import logging
import time
import random
import requests
import threading
import redis
from datetime import datetime
from flask import Flask, request, jsonify, session
from openai import OpenAI
from deepseek import DeepSeekClient
from sqlalchemy import create_engine, text

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("user_onboarding.log"), logging.StreamHandler()]
)

# Flask App Initialization
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

# Redis for Session Management
REDIS_HOST = "localhost"
REDIS_PORT = 6379
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=1, decode_responses=True)

# Database Connection
DATABASE_URI = "postgresql://user:password@localhost/rlg_data"
engine = create_engine(DATABASE_URI)

# AI Clients for Interactive Assistance
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
deepseek_client = DeepSeekClient(api_key=os.getenv("DEEPSEEK_API_KEY"))

# Step Definitions
ONBOARDING_STEPS = [
    {"step": 1, "title": "Welcome to RLG", "description": "Let's set up your profile."},
    {"step": 2, "title": "Choose Your Interests", "description": "Select industries, topics, and data sources you care about."},
    {"step": 3, "title": "Connect Social Accounts", "description": "Sync Twitter, LinkedIn, and other platforms for personalized insights."},
    {"step": 4, "title": "Understand Your Dashboard", "description": "Learn how to navigate and access real-time insights."},
    {"step": 5, "title": "First Data Report", "description": "Get your first AI-generated data insights."},
]

class UserOnboarding:
    """
    Manages the interactive user onboarding process for RLG Data and RLG Fans.
    """

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.session_key = f"user:{user_id}:onboarding"

    def start_onboarding(self):
        """Start the onboarding process."""
        redis_client.hmset(self.session_key, {"step": 1, "completed": False})
        return ONBOARDING_STEPS[0]

    def get_current_step(self):
        """Retrieve the current step for the user."""
        step = int(redis_client.hget(self.session_key, "step") or 1)
        return next((s for s in ONBOARDING_STEPS if s["step"] == step), None)

    def advance_step(self):
        """Move the user to the next step in onboarding."""
        step = int(redis_client.hget(self.session_key, "step") or 1)
        next_step = step + 1
        if next_step > len(ONBOARDING_STEPS):
            redis_client.hset(self.session_key, "completed", "True")
            return {"message": "🎉 Onboarding complete!", "status": "completed"}
        redis_client.hset(self.session_key, "step", next_step)
        return next((s for s in ONBOARDING_STEPS if s["step"] == next_step), None)

    def is_completed(self):
        """Check if onboarding is completed."""
        return redis_client.hget(self.session_key, "completed") == "True"

    def ai_assist(self, query):
        """AI-powered chat assistant for onboarding guidance."""
        ai_response = openai_client.Completion.create(
            model="gpt-4",
            prompt=f"Assist a new user with onboarding. Question: {query}",
            max_tokens=100
        )
        return ai_response["choices"][0]["text"].strip()

    def deepseek_recommendations(self):
        """DeepSeek AI-driven feature recommendations based on user activity."""
        user_interests = self.get_user_interests()
        recommendations = deepseek_client.suggest_features(user_interests)
        return recommendations

    def get_user_interests(self):
        """Retrieve user-selected interests from the database."""
        query = text("SELECT interests FROM users WHERE user_id = :user_id")
        with engine.connect() as connection:
            result = connection.execute(query, {"user_id": self.user_id}).fetchone()
            return result["interests"] if result else []

@app.route("/onboarding/start", methods=["POST"])
def start_onboarding():
    """API endpoint to start user onboarding."""
    user_id = request.json.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    onboarding = UserOnboarding(user_id)
    return jsonify(onboarding.start_onboarding())

@app.route("/onboarding/step", methods=["GET"])
def get_step():
    """API endpoint to get the current onboarding step."""
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    onboarding = UserOnboarding(user_id)
    return jsonify(onboarding.get_current_step())

@app.route("/onboarding/next", methods=["POST"])
def next_step():
    """API endpoint to move to the next onboarding step."""
    user_id = request.json.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    onboarding = UserOnboarding(user_id)
    return jsonify(onboarding.advance_step())

@app.route("/onboarding/ai-assist", methods=["POST"])
def ai_assist():
    """API endpoint for AI-powered onboarding guidance."""
    user_id = request.json.get("user_id")
    query = request.json.get("query")
    if not user_id or not query:
        return jsonify({"error": "Missing user_id or query"}), 400
    onboarding = UserOnboarding(user_id)
    return jsonify({"response": onboarding.ai_assist(query)})

@app.route("/onboarding/recommendations", methods=["GET"])
def get_recommendations():
    """API endpoint for AI-based feature recommendations."""
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    onboarding = UserOnboarding(user_id)
    return jsonify({"recommendations": onboarding.deepseek_recommendations()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)

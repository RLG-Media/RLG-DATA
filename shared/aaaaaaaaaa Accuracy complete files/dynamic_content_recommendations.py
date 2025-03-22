import os
import json
import random
import numpy as np
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer, util
from sklearn.preprocessing import StandardScaler
from transformers import pipeline
from datetime import datetime, timedelta
from collections import defaultdict

# Load AI models
content_embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
sentiment_analyzer = pipeline("sentiment-analysis")
trending_analysis_model = pipeline("text-classification", model="facebook/bart-large-mnli")

class DynamicContentRecommendations:
    def __init__(self, user_id=None):
        self.user_id = user_id
        self.content_db = "content_data.json"
        self.user_activity_db = "user_activity.json"
        self.trending_topics_db = "trending_topics.json"
        self.personalization_weight = 0.7  # Adjust weight of personalization vs. trending

    def load_data(self, file_path):
        """
        Loads JSON data from a file.
        """
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        return {}

    def save_data(self, file_path, data):
        """
        Saves JSON data to a file.
        """
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def analyze_trending_topics(self):
        """
        Extracts and ranks trending topics from stored content.
        """
        content_data = self.load_data(self.content_db)
        topic_scores = defaultdict(int)

        for item in content_data.get("articles", []):
            result = trending_analysis_model(item["title"])
            topic = result[0]["label"]
            topic_scores[topic] += 1

        sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
        trending_topics = [topic for topic, _ in sorted_topics[:5]]  # Top 5 topics

        self.save_data(self.trending_topics_db, {"trending_topics": trending_topics})
        return trending_topics

    def get_user_preferences(self):
        """
        Retrieves user preferences based on past interactions.
        """
        user_activity = self.load_data(self.user_activity_db).get(self.user_id, {})
        return user_activity.get("preferred_topics", [])

    def rank_content(self, content_list):
        """
        Ranks content based on personalization, trending topics, and sentiment.
        """
        user_preferences = self.get_user_preferences()
        trending_topics = self.analyze_trending_topics()

        rankings = []
        for content in content_list:
            title_embedding = content_embedding_model.encode(content["title"], convert_to_tensor=True)
            content_embedding = content_embedding_model.encode(content["text"], convert_to_tensor=True)
            sentiment = sentiment_analyzer(content["text"])[0]

            # Compute similarity score
            relevance_score = 0
            for topic in user_preferences:
                topic_embedding = content_embedding_model.encode(topic, convert_to_tensor=True)
                relevance_score += util.pytorch_cos_sim(title_embedding, topic_embedding).item()

            # Adjust scores based on trending topics
            trending_score = 1 if any(topic in content["title"] for topic in trending_topics) else 0

            # Adjust score based on sentiment (prefer positive content)
            sentiment_score = 1 if sentiment["label"] == "POSITIVE" else 0.5

            # Compute final ranking score
            final_score = (self.personalization_weight * relevance_score) + (0.2 * trending_score) + (0.1 * sentiment_score)
            rankings.append((content, final_score))

        # Sort by ranking score
        ranked_content = sorted(rankings, key=lambda x: x[1], reverse=True)
        return [item[0] for item in ranked_content]

    def recommend_content(self):
        """
        Recommends content dynamically based on trends and user preferences.
        """
        content_data = self.load_data(self.content_db)
        if not content_data.get("articles"):
            return []

        ranked_content = self.rank_content(content_data["articles"])
        return ranked_content[:10]  # Return top 10 recommendations

if __name__ == "__main__":
    recommender = DynamicContentRecommendations(user_id="12345")
    recommendations = recommender.recommend_content()

    print("🔍 Recommended Content for User 12345:")
    for idx, content in enumerate(recommendations, start=1):
        print(f"{idx}. {content['title']} (Source: {content['source']})")

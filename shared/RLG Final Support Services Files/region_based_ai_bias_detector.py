import json
import os
import numpy as np
import pandas as pd
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
from collections import defaultdict

# Load AI models
bias_detection_model = pipeline("text-classification", model="facebook/bart-large-mnli")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

class RegionBasedAIBiasDetector:
    def __init__(self):
        self.region_bias_db = "region_bias_data.json"
        self.content_db = "content_data.json"
        self.user_activity_db = "user_activity.json"
        self.bias_threshold = 0.6  # Adjust sensitivity for bias detection

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

    def detect_bias(self, text, region):
        """
        Detects potential bias in text based on regional norms.
        """
        classification = bias_detection_model(text)
        label = classification[0]["label"]
        confidence = classification[0]["score"]

        # Adjust for region-based sensitivity
        region_bias_rules = self.load_data(self.region_bias_db).get(region, {})
        region_bias_score = 0

        if label in region_bias_rules:
            region_bias_score = confidence * region_bias_rules[label]

        return {"label": label, "score": confidence, "region_bias_score": region_bias_score}

    def analyze_bias_in_content(self):
        """
        Analyzes all stored content for regional AI bias.
        """
        content_data = self.load_data(self.content_db)
        if not content_data.get("articles"):
            return []

        bias_results = []
        for article in content_data["articles"]:
            region = article.get("region", "Global")
            result = self.detect_bias(article["text"], region)
            if result["region_bias_score"] > self.bias_threshold:
                bias_results.append({"title": article["title"], "bias": result})

        return bias_results

    def recommend_bias_corrections(self):
        """
        Provides recommendations to mitigate regional AI bias.
        """
        bias_results = self.analyze_bias_in_content()
        recommendations = []

        for bias in bias_results:
            recommendations.append({
                "title": bias["title"],
                "action": "Consider rewording content to be more neutral.",
                "bias_score": bias["bias"]["region_bias_score"]
            })

        return recommendations

if __name__ == "__main__":
    bias_detector = RegionBasedAIBiasDetector()
    bias_issues = bias_detector.analyze_bias_in_content()
    corrections = bias_detector.recommend_bias_corrections()

    print("⚠️ Detected AI Bias in Content:")
    for issue in bias_issues:
        print(f"Title: {issue['title']} | Bias Score: {issue['bias']['region_bias_score']}")

    print("\n🔧 Recommended Corrections:")
    for correction in corrections:
        print(f"Title: {correction['title']} | Action: {correction['action']} | Bias Score: {correction['bias_score']}")

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from datetime import datetime
import logging

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("ai_content_recommendations.log"), logging.StreamHandler()]
)

class AIContentRecommendations:
    def __init__(self, content_data, engagement_data, trends_data):
        """
        Initialize the recommendation engine with datasets.
        :param content_data: DataFrame containing existing user content.
        :param engagement_data: DataFrame containing engagement metrics for content.
        :param trends_data: DataFrame containing trending topics and hashtags.
        """
        self.content_data = content_data
        self.engagement_data = engagement_data
        self.trends_data = trends_data
        self.tfidf_vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)
        self.model = None
        logging.info("AIContentRecommendations initialized.")

    def preprocess_data(self):
        """
        Preprocess the input datasets.
        """
        try:
            # Merge content and engagement data on a common identifier (e.g., content ID)
            self.content_data = pd.merge(
                self.content_data, self.engagement_data, on="content_id", how="left"
            )
            # Fill missing values
            self.content_data.fillna({"engagement_score": 0, "content_text": ""}, inplace=True)
            logging.info("Data preprocessing completed.")
        except Exception as e:
            logging.error(f"Error during data preprocessing: {e}")

    def calculate_content_similarity(self):
        """
        Calculate similarity scores between pieces of content using TF-IDF.
        """
        try:
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.content_data["content_text"])
            similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
            self.content_data["similarity_scores"] = list(similarity_matrix)
            logging.info("Content similarity calculated.")
        except Exception as e:
            logging.error(f"Error during similarity calculation: {e}")

    def identify_trending_content(self):
        """
        Identify trending topics from the trends_data and match them with existing content.
        """
        try:
            trending_topics = self.trends_data["topic"].tolist()
            self.content_data["is_trending"] = self.content_data["content_text"].apply(
                lambda text: any(topic in text for topic in trending_topics)
            )
            logging.info("Trending content identified.")
        except Exception as e:
            logging.error(f"Error during trending content identification: {e}")

    def recommend_content(self, user_preferences, top_n=5):
        """
        Recommend content based on user preferences and engagement scores.
        :param user_preferences: Dictionary containing user preferences (e.g., topics, keywords).
        :param top_n: Number of recommendations to return.
        :return: DataFrame containing top recommended content.
        """
        try:
            # Filter content based on user preferences
            filtered_content = self.content_data[
                self.content_data["content_text"].str.contains(
                    "|".join(user_preferences.get("keywords", [])), case=False, na=False
                )
            ]
            # Sort by engagement score and trending status
            filtered_content.sort_values(
                by=["is_trending", "engagement_score"], ascending=[False, False], inplace=True
            )
            recommendations = filtered_content.head(top_n)
            logging.info("Content recommendations generated.")
            return recommendations
        except Exception as e:
            logging.error(f"Error during content recommendation: {e}")
            return pd.DataFrame()

    def cluster_content(self, n_clusters=5):
        """
        Cluster content into groups using K-Means clustering.
        :param n_clusters: Number of clusters.
        """
        try:
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.content_data["content_text"])
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            self.content_data["cluster"] = kmeans.fit_predict(tfidf_matrix)
            logging.info("Content clustering completed.")
        except Exception as e:
            logging.error(f"Error during content clustering: {e}")

    def generate_insights(self):
        """
        Generate insights based on clustered content and engagement metrics.
        :return: Dictionary containing insights.
        """
        try:
            insights = {}
            for cluster, group in self.content_data.groupby("cluster"):
                top_content = group.sort_values("engagement_score", ascending=False).head(1)
                insights[cluster] = {
                    "top_content": top_content["content_text"].values[0],
                    "average_engagement": group["engagement_score"].mean(),
                }
            logging.info("Insights generation completed.")
            return insights
        except Exception as e:
            logging.error(f"Error during insights generation: {e}")
            return {}

# Example usage
if __name__ == "__main__":
    # Example datasets
    content_data = pd.DataFrame({
        "content_id": [1, 2, 3, 4],
        "content_text": [
            "Learn how to grow your audience on TikTok.",
            "Best practices for monetizing YouTube content.",
            "How to engage your followers on Instagram.",
            "Using hashtags effectively on Twitter."
        ]
    })

    engagement_data = pd.DataFrame({
        "content_id": [1, 2, 3, 4],
        "engagement_score": [80, 95, 60, 50]
    })

    trends_data = pd.DataFrame({
        "topic": ["TikTok", "YouTube", "Instagram"]
    })

    # Initialize recommendation engine
    recommender = AIContentRecommendations(content_data, engagement_data, trends_data)
    recommender.preprocess_data()
    recommender.calculate_content_similarity()
    recommender.identify_trending_content()

    # Generate recommendations
    user_preferences = {"keywords": ["YouTube", "TikTok"]}
    recommendations = recommender.recommend_content(user_preferences, top_n=3)
    print("Recommendations:")
    print(recommendations)

    # Cluster content and generate insights
    recommender.cluster_content(n_clusters=3)
    insights = recommender.generate_insights()
    print("Insights:")
    print(insights)

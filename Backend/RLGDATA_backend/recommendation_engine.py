# recommendation_engine.py

import logging
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    A recommendation engine for generating actionable insights and content suggestions
    for RLG Data and RLG Fans.
    """

    def __init__(self):
        """
        Initializes the recommendation engine with default configurations.
        """
        self.vectorizer = TfidfVectorizer(stop_words="english")
        logger.info("Recommendation Engine initialized.")

    def recommend_content(self, content_data, user_preferences, top_n=5):
        """
        Recommends content based on user preferences and existing data.
        :param content_data: DataFrame containing content details.
        :param user_preferences: A string representing user preferences or interests.
        :param top_n: Number of top recommendations to return.
        :return: DataFrame containing recommended content.
        """
        logger.info("Generating content recommendations...")
        content_data["combined_features"] = content_data["title"] + " " + content_data["tags"]

        # Vectorize the combined features and user preferences
        content_vectors = self.vectorizer.fit_transform(content_data["combined_features"])
        user_vector = self.vectorizer.transform([user_preferences])

        # Compute cosine similarity
        similarity_scores = cosine_similarity(user_vector, content_vectors).flatten()
        content_data["similarity_score"] = similarity_scores

        # Sort by similarity and return top results
        recommendations = content_data.sort_values(by="similarity_score", ascending=False).head(top_n)
        logger.info(f"Top {top_n} recommendations generated.")
        return recommendations

    def recommend_platforms(self, platform_data, user_goals):
        """
        Recommends platforms based on user goals and platform attributes.
        :param platform_data: DataFrame containing platform performance and features.
        :param user_goals: A dictionary of goals (e.g., {"engagement": True, "monetization": True}).
        :return: DataFrame containing recommended platforms.
        """
        logger.info("Generating platform recommendations...")
        platform_data["relevance_score"] = 0

        # Assign weights based on user goals
        for goal, weight in user_goals.items():
            if goal in platform_data.columns:
                platform_data["relevance_score"] += platform_data[goal] * weight

        # Sort platforms by relevance score
        recommended_platforms = platform_data.sort_values(by="relevance_score", ascending=False)
        logger.info("Platform recommendations generated.")
        return recommended_platforms

    def generate_actionable_insights(self, analytics_data):
        """
        Generates actionable insights based on analytics data.
        :param analytics_data: DataFrame containing performance metrics.
        :return: List of insights.
        """
        logger.info("Analyzing data to generate actionable insights...")
        insights = []

        # Identify high-performing content
        high_performance = analytics_data[analytics_data["engagement_rate"] > 0.8]
        if not high_performance.empty:
            insights.append("Focus on amplifying content with high engagement rates.")

        # Suggest content improvements
        low_reach = analytics_data[analytics_data["reach"] < 500]
        if not low_reach.empty:
            insights.append("Improve SEO and tagging for content with low reach.")

        # Highlight trending topics
        trending_topics = analytics_data[analytics_data["trending"] == True]
        if not trending_topics.empty:
            insights.append(f"Create more content around these trending topics: {', '.join(trending_topics['topic'])}.")

        logger.info(f"{len(insights)} insights generated.")
        return insights


# Example Usage
if __name__ == "__main__":
    # Simulate content data
    content_data = pd.DataFrame({
        "title": ["How to grow on OnlyFans", "Patreon monetization tips", "Content ideas for TikTok"],
        "tags": ["OnlyFans growth", "monetization strategies", "TikTok trends"]
    })

    # Simulate user preferences
    user_preferences = "growth and monetization strategies"

    # Instantiate the recommendation engine
    engine = RecommendationEngine()

    # Get content recommendations
    recommendations = engine.recommend_content(content_data, user_preferences, top_n=3)
    print("Content Recommendations:")
    print(recommendations)

    # Simulate platform data
    platform_data = pd.DataFrame({
        "platform": ["OnlyFans", "Patreon", "TikTok"],
        "engagement": [0.9, 0.8, 0.95],
        "monetization": [0.95, 0.9, 0.7]
    })

    user_goals = {"engagement": 1.0, "monetization": 1.5}
    platform_recommendations = engine.recommend_platforms(platform_data, user_goals)
    print("Platform Recommendations:")
    print(platform_recommendations)

    # Simulate analytics data
    analytics_data = pd.DataFrame({
        "content_id": [1, 2, 3],
        "engagement_rate": [0.85, 0.65, 0.9],
        "reach": [1000, 400, 1500],
        "trending": [True, False, True],
        "topic": ["growth", "SEO", "monetization"]
    })

    insights = engine.generate_actionable_insights(analytics_data)
    print("Actionable Insights:")
    print(insights)

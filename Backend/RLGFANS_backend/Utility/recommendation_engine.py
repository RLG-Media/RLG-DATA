# recommendation_engine.py

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecommendationEngine:
    def __init__(self, content_data, user_data):
        """
        Initializes the RecommendationEngine with content data and user engagement data.
        :param content_data: DataFrame containing columns 'content_id', 'title', 'tags', 'platform', 'content_type'.
        :param user_data: DataFrame containing columns 'user_id', 'content_id', 'engagement_score'.
        """
        self.content_data = content_data
        self.user_data = user_data
        self.recommendations = None

    def preprocess_content_data(self):
        """
        Prepares the content data by creating a combined 'text' feature and applying TF-IDF vectorization.
        """
        logger.info("Preprocessing content data for recommendations...")
        self.content_data['text'] = self.content_data['title'] + " " + self.content_data['tags'] + " " + self.content_data['content_type']
        
        # Apply TF-IDF to the combined text feature for content similarity
        tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        self.content_tfidf_matrix = tfidf_vectorizer.fit_transform(self.content_data['text'])
        logger.info("Content data preprocessing complete.")

    def calculate_similarity(self):
        """
        Calculates similarity between content items using cosine similarity on the TF-IDF matrix.
        """
        logger.info("Calculating content similarity...")
        self.similarity_matrix = cosine_similarity(self.content_tfidf_matrix)
        logger.info("Content similarity calculation complete.")

    def get_top_content_recommendations(self, content_id, top_n=5):
        """
        Returns top content recommendations based on a specific content ID.
        :param content_id: ID of the content for which to generate recommendations.
        :param top_n: Number of top recommendations to return.
        :return: List of recommended content IDs.
        """
        content_idx = self.content_data.index[self.content_data['content_id'] == content_id].tolist()[0]
        similarity_scores = list(enumerate(self.similarity_matrix[content_idx]))
        
        # Sort content by similarity score
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        
        # Get top_n similar content IDs
        top_content_idx = [i[0] for i in similarity_scores[1:top_n+1]]  # Exclude the content itself
        
        top_content_ids = self.content_data.iloc[top_content_idx]['content_id'].tolist()
        logger.info(f"Top {top_n} recommendations for content ID {content_id}: {top_content_ids}")
        return top_content_ids

    def get_user_recommendations(self, user_id, top_n=5):
        """
        Recommends content for a specific user based on their past engagement scores.
        :param user_id: User ID for which to generate recommendations.
        :param top_n: Number of top recommendations to return.
        :return: List of recommended content IDs.
        """
        logger.info(f"Generating recommendations for user ID {user_id}...")
        
        # Filter user data for the user's past engagement
        user_engaged_content = self.user_data[self.user_data['user_id'] == user_id]
        
        # Get content that the user has engaged with and calculate average engagement score for each content
        content_engagement = user_engaged_content.groupby('content_id')['engagement_score'].mean().reset_index()
        
        # Sort content by engagement score in descending order
        content_engagement = content_engagement.sort_values(by='engagement_score', ascending=False)
        
        # Get the top_n content IDs with the highest engagement scores
        top_engaged_content_ids = content_engagement.head(top_n)['content_id'].tolist()
        logger.info(f"Top {top_n} content recommendations based on user engagement: {top_engaged_content_ids}")
        
        return top_engaged_content_ids

    def cross_platform_recommendations(self, user_id, platform, top_n=5):
        """
        Provides cross-platform recommendations based on user engagement across multiple platforms.
        :param user_id: User ID for which to generate recommendations.
        :param platform: The platform (OnlyFans, Patreon, etc.) for which to generate recommendations.
        :param top_n: Number of top recommendations to return.
        :return: List of recommended content IDs.
        """
        logger.info(f"Generating cross-platform recommendations for user ID {user_id} on platform {platform}...")
        
        # Filter the user engagement data based on the platform
        user_engaged_on_platform = self.user_data[
            (self.user_data['user_id'] == user_id) & (self.user_data['platform'] == platform)
        ]
        
        # Get content IDs from the user's engagement and fetch their average engagement scores
        content_engagement = user_engaged_on_platform.groupby('content_id')['engagement_score'].mean().reset_index()
        content_engagement = content_engagement.sort_values(by='engagement_score', ascending=False)
        
        # Get the top_n content IDs
        top_cross_platform_content_ids = content_engagement.head(top_n)['content_id'].tolist()
        logger.info(f"Top {top_n} cross-platform recommendations for user ID {user_id} on {platform}: {top_cross_platform_content_ids}")
        
        return top_cross_platform_content_ids


if __name__ == "__main__":
    # Example: Assuming you have the content and user data loaded in Pandas DataFrames
    content_data = pd.DataFrame({
        'content_id': ['c1', 'c2', 'c3', 'c4', 'c5'],
        'title': ['Content A', 'Content B', 'Content C', 'Content D', 'Content E'],
        'tags': ['tag1 tag2', 'tag2 tag3', 'tag1 tag3', 'tag4 tag5', 'tag1 tag5'],
        'content_type': ['video', 'image', 'video', 'live', 'image'],
        'platform': ['OnlyFans', 'Patreon', 'OnlyFans', 'Patreon', 'OnlyFans']
    })
    
    user_data = pd.DataFrame({
        'user_id': ['u1', 'u1', 'u2', 'u2', 'u3'],
        'content_id': ['c1', 'c2', 'c3', 'c4', 'c5'],
        'engagement_score': [80, 90, 70, 60, 85],
        'platform': ['OnlyFans', 'Patreon', 'OnlyFans', 'Patreon', 'OnlyFans']
    })
    
    # Initialize the recommendation engine
    engine = RecommendationEngine(content_data, user_data)
    
    # Preprocess content and calculate similarity
    engine.preprocess_content_data()
    engine.calculate_similarity()
    
    # Get recommendations
    user_id = 'u1'
    top_content = engine.get_user_recommendations(user_id)
    print("Top content for user:", top_content)

    platform_recs = engine.cross_platform_recommendations(user_id, platform='OnlyFans')
    print("Cross-platform recommendations:", platform_recs)

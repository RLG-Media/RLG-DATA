"""
content_recommendations.py

This module defines the ContentRecommendations class for generating content recommendations
based on user behavior and content attributes. It uses cosine similarity to compare the user's 
profile (derived from their interaction history) with content feature vectors, and provides multiple
methods to fetch recommendations based on tags, new content, popularity, freshness, and even hybrid 
approaches.

The class is designed to be robust, scalable, and extensible. It can be used for both RLG Data and RLG Fans,
and can be further extended to incorporate region, country, city, and town-based adjustments if the content 
metadata and user data include such details.

Additional Recommendations:
  1. Further integrate location data into the recommendation process if available.
  2. Consider using a more advanced hybrid model that combines collaborative filtering with content-based filtering.
  3. Implement asynchronous or batch processing for large datasets.
  4. Enhance evaluation methods and A/B testing to continuously refine the recommendations.
  5. Securely log and monitor recommendation outputs for debugging and quality control.

Dependencies:
  - numpy, pandas, scikit-learn (for cosine_similarity and NearestNeighbors), and logging.
"""

import logging
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Configure logging for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

class ContentRecommendations:
    """
    Class for generating content recommendations based on user behavior and content attributes.
    """
    
    def __init__(self, user_history, content_database, content_features):
        """
        Initializes the ContentRecommendations instance.

        Args:
            user_history: An object or dictionary that provides a method get_user_interactions(user_id)
                          which returns a list of content IDs the user has interacted with.
            content_database: A list (or similar sequence) where each element is a dictionary representing
                              content details (e.g., title, tags, popularity, freshness, diversity_score, etc.).
            content_features: A list or 2D numpy array of feature vectors corresponding to the content in content_database.
                              Each feature vector should be a 1D array.
        """
        self.user_history = user_history
        self.content_database = content_database
        self.content_features = np.array(content_features)
        if self.content_features.ndim != 2:
            logger.error("Content features must be a 2D array (matrix).")
            raise ValueError("Content features must be a 2D array (matrix).")

    def _generate_user_profile(self, user_id):
        """
        Generate a user profile based on their interaction history.
        It aggregates the feature vectors of the content items the user interacted with.

        Args:
            user_id: The ID of the user.

        Returns:
            np.array: The user profile vector (mean of content vectors) or a zero vector if no interactions.
        """
        try:
            user_interactions = self.user_history.get_user_interactions(user_id)
            if not user_interactions:
                logger.warning(f"No interactions found for user {user_id}. Returning zero vector.")
                return np.zeros(self.content_features.shape[1])
            # Collect feature vectors corresponding to each content ID.
            content_vectors = [self.content_features[idx] for idx in user_interactions if idx < len(self.content_features)]
            if not content_vectors:
                logger.warning(f"No valid content vectors found for user {user_id}.")
                return np.zeros(self.content_features.shape[1])
            user_profile = np.mean(content_vectors, axis=0)
            logger.info(f"Generated user profile for user {user_id}.")
            return user_profile
        except Exception as e:
            logger.error(f"Error generating profile for user {user_id}: {e}")
            return np.zeros(self.content_features.shape[1])

    def _calculate_similarities(self, user_profile):
        """
        Calculate cosine similarity between the user profile and all content feature vectors.

        Args:
            user_profile (np.array): The user's profile vector.

        Returns:
            np.array: Array of similarity scores.
        """
        try:
            similarities = cosine_similarity([user_profile], self.content_features)
            return similarities[0]
        except Exception as e:
            logger.error(f"Error calculating similarities: {e}")
            return np.zeros(self.content_features.shape[0])

    def get_top_recommendations(self, user_id, top_n=10):
        """
        Retrieve top content recommendations for a user based on similarity scores.

        Args:
            user_id: The user's ID.
            top_n (int): Number of recommendations to return.

        Returns:
            list: A list of recommended content dictionaries.
        """
        try:
            user_profile = self._generate_user_profile(user_id)
            similarities = self._calculate_similarities(user_profile)
            sorted_indices = np.argsort(similarities)[::-1]  # Descending order
            recommended_content = [self.content_database[idx] for idx in sorted_indices[:top_n]]
            logger.info(f"Top {top_n} recommendations for user {user_id}: {recommended_content}")
            return recommended_content
        except Exception as e:
            logger.error(f"Error generating recommendations for user {user_id}: {e}")
            return []

    def get_content_by_tags(self, tags, top_n=5):
        """
        Fetch content based on specific tags for recommendation purposes.

        Args:
            tags (list): List of tags to match.
            top_n (int): Number of top recommendations to return.

        Returns:
            list: List of content dictionaries matching the tags, sorted by popularity.
        """
        try:
            tagged_content = [content for content in self.content_database if any(tag in content.get('tags', []) for tag in tags)]
            sorted_content = sorted(tagged_content, key=lambda x: x.get('popularity', 0), reverse=True)[:top_n]
            logger.info(f"Content fetched by tags {tags}, top {top_n}: {sorted_content}")
            return sorted_content
        except Exception as e:
            logger.error(f"Error fetching content by tags: {e}")
            return []

    def get_new_content_recommendations(self, user_id, new_content, top_n=10):
        """
        Provide recommendations based on newly added content in addition to the existing database.

        Args:
            user_id: The user's ID.
            new_content (list): A list of new content dictionaries (each should contain a 'features' key).
            top_n (int): Number of recommendations to return.

        Returns:
            list: Recommended content items.
        """
        try:
            user_profile = self._generate_user_profile(user_id)
            new_content_features = [content['features'] for content in new_content if 'features' in content]
            if len(new_content_features) == 0:
                logger.warning("No valid features found in new content.")
                return []
            # Combine existing and new content features into one matrix.
            all_features = np.vstack([self.content_features, np.array(new_content_features)])
            similarities = cosine_similarity([user_profile], all_features)[0]
            sorted_indices = np.argsort(similarities)[::-1]
            # Use indices to fetch recommendations from combined content:
            # First part corresponds to existing database, new content follows.
            recommended_content = []
            for idx in sorted_indices[:top_n]:
                if idx < len(self.content_database):
                    recommended_content.append(self.content_database[idx])
                else:
                    recommended_content.append(new_content[idx - len(self.content_database)])
            logger.info(f"New content recommendations for user {user_id}: {recommended_content}")
            return recommended_content
        except Exception as e:
            logger.error(f"Error generating new content recommendations for user {user_id}: {e}")
            return []

    def get_popular_content_recommendations(self, top_n=10):
        """
        Get content recommendations based purely on popularity.
        
        Returns:
            list: Top content items sorted by their 'popularity' attribute.
        """
        try:
            sorted_content = sorted(self.content_database, key=lambda x: x.get('popularity', 0), reverse=True)[:top_n]
            logger.info(f"Popular content recommendations: {sorted_content}")
            return sorted_content
        except Exception as e:
            logger.error(f"Error generating popular content recommendations: {e}")
            return []

    def get_fresh_content_recommendations(self, top_n=10):
        """
        Get content recommendations based on freshness (recency).

        Returns:
            list: Top content items sorted by their 'freshness' attribute.
        """
        try:
            sorted_content = sorted(self.content_database, key=lambda x: x.get('freshness', 0), reverse=True)[:top_n]
            logger.info(f"Fresh content recommendations: {sorted_content}")
            return sorted_content
        except Exception as e:
            logger.error(f"Error generating fresh content recommendations: {e}")
            return []

    def get_diverse_content_recommendations(self, top_n=10):
        """
        Get content recommendations that emphasize diversity using a 'diversity_score' attribute.
        
        Returns:
            list: Top content items sorted by diversity score.
        """
        try:
            sorted_content = sorted(self.content_database, key=lambda x: x.get('diversity_score', 0), reverse=True)[:top_n]
            logger.info(f"Diverse content recommendations: {sorted_content}")
            return sorted_content
        except Exception as e:
            logger.error(f"Error generating diverse content recommendations: {e}")
            return []

    def incorporate_user_feedback(self, feedback_data):
        """
        Incorporates user feedback to refine content recommendations by adjusting content features.
        
        Args:
            feedback_data (list): A list of feedback dictionaries. Each should have 'user_id', 'content_id', and 'liked' (bool).
        """
        try:
            for feedback in feedback_data:
                content_id = feedback.get('content_id')
                liked = feedback.get('liked', True)
                if content_id is not None and 0 <= content_id < len(self.content_features):
                    if liked:
                        self.content_features[content_id] *= 1.1
                    else:
                        self.content_features[content_id] *= 0.9
            logger.info("User feedback incorporated into content features.")
        except Exception as e:
            logger.error(f"Error incorporating user feedback: {e}")

    def _combine_content_based_and_collaborative_filtering(self, user_profile, top_n=10):
        """
        Hybrid recommendation combining content-based similarity and popularity.
        
        Args:
            user_profile (np.array): The user's profile vector.
            top_n (int): Number of recommendations to return.
        
        Returns:
            list: List of recommended content items.
        """
        try:
            content_similarities = self._calculate_similarities(user_profile)
            # For popularity, assume each content dict has a 'popularity' key.
            popularity_scores = np.array([content.get('popularity', 0) for content in self.content_database])
            # Normalize popularity scores to the same scale as similarities.
            if popularity_scores.max() > 0:
                popularity_scores = popularity_scores / popularity_scores.max()
            combined_scores = (content_similarities + popularity_scores) / 2
            sorted_indices = np.argsort(combined_scores)[::-1]
            recommended_content = [self.content_database[idx] for idx in sorted_indices[:top_n]]
            logger.info(f"Hybrid recommendations: {recommended_content}")
            return recommended_content
        except Exception as e:
            logger.error(f"Error combining content and popularity recommendations: {e}")
            return []

    def get_contextual_content_recommendations(self, contextual_factors, top_n=10):
        """
        Optimizes content discovery based on contextual factors such as freshness, diversity, and recency.
        
        Args:
            contextual_factors (dict): A dictionary where keys are content attribute names and values are weights.
            top_n (int): Number of recommendations to return.
        
        Returns:
            list: List of content items sorted by a combined contextual score.
        """
        try:
            content_scores = []
            for content in self.content_database:
                score = 0
                for key, weight in contextual_factors.items():
                    score += content.get(key, 0) * weight
                content_scores.append(score)
            sorted_indices = np.argsort(content_scores)[::-1]
            optimized_content = [self.content_database[idx] for idx in sorted_indices[:top_n]]
            logger.info(f"Contextual content recommendations: {optimized_content}")
            return optimized_content
        except Exception as e:
            logger.error(f"Error optimizing contextual content recommendations: {e}")
            return []

    def _enable_real_time_updates(self, user_id, new_content, top_n=10):
        """
        Provides real-time recommendation updates based on changing user preferences.
        
        Args:
            user_id: The user's ID.
            new_content (list): A list of new content dictionaries, each with a 'features' key.
            top_n (int): Number of recommendations to return.
        
        Returns:
            list: List of updated recommendations.
        """
        try:
            updated_user_profile = self._generate_user_profile(user_id)
            new_content_features = [content['features'] for content in new_content if 'features' in content]
            if len(new_content_features) == 0:
                logger.warning("No new content features found for real-time update.")
                return []
            all_features = np.vstack([self.content_features, np.array(new_content_features)])
            updated_similarities = cosine_similarity([updated_user_profile], all_features)[0]
            sorted_indices = np.argsort(updated_similarities)[::-1]
            recommended_content = []
            total_existing = len(self.content_database)
            for idx in sorted_indices[:top_n]:
                if idx < total_existing:
                    recommended_content.append(self.content_database[idx])
                else:
                    recommended_content.append(new_content[idx - total_existing])
            logger.info(f"Real-time recommendations for user {user_id}: {recommended_content}")
            return recommended_content
        except Exception as e:
            logger.error(f"Error enabling real-time updates: {e}")
            return []

# -------------------------------
# Additional Recommendations:
# -------------------------------
# 1. Integrate location data into the recommendation process if available to further refine personalization.
# 2. Consider advanced hybrid models that combine content-based, collaborative, and contextual filtering.
# 3. Use asynchronous processing or batch updates if the dataset is very large.
# 4. Extend evaluation methods to include metrics such as RMSE or user satisfaction scores.
# 5. Continuously monitor and A/B test recommendations to improve effectiveness.

# -------------------------------
# Standalone Testing Example:
# -------------------------------
if __name__ == "__main__":
    # Mock user history with a simple implementation for testing purposes.
    class MockUserHistory:
        def __init__(self, interactions):
            # interactions is a dict mapping user IDs to lists of content indices they've interacted with.
            self.interactions = interactions
        def get_user_interactions(self, user_id):
            return self.interactions.get(user_id, [])
    
    # Example mock data:
    user_history_example = MockUserHistory({
        "user_1": [0, 2],
        "user_2": [1, 3],
    })
    
    # Create a sample content database (list of dicts with attributes)
    content_database_example = [
        {"id": 0, "title": "Content A", "tags": ["tech"], "popularity": 80, "freshness": 0.9, "diversity_score": 0.7, "features": np.array([0.1, 0.3, 0.5])},
        {"id": 1, "title": "Content B", "tags": ["news"], "popularity": 60, "freshness": 0.8, "diversity_score": 0.6, "features": np.array([0.2, 0.1, 0.4])},
        {"id": 2, "title": "Content C", "tags": ["tech", "innovation"], "popularity": 90, "freshness": 0.95, "diversity_score": 0.8, "features": np.array([0.3, 0.4, 0.2])},
        {"id": 3, "title": "Content D", "tags": ["entertainment"], "popularity": 50, "freshness": 0.7, "diversity_score": 0.5, "features": np.array([0.1, 0.2, 0.3])},
    ]
    
    # Create a matrix of content features (ordered as in content_database_example)
    content_features_example = [content['features'] for content in content_database_example]
    
    # Initialize the ContentRecommendations engine with mock data
    engine = ContentRecommendations(user_history_example, content_database_example, content_features_example)
    
    # Generate recommendations for a user
    recommendations = engine.get_top_recommendations("user_1", top_n=3)
    print("Top recommendations for user_1:", recommendations)
    
    # Example: Fetch content by tags
    tag_recommendations = engine.get_content_by_tags(["tech"], top_n=2)
    print("Content recommendations by tags (tech):", tag_recommendations)
    
    # Example: Get popular content recommendations
    popular_recommendations = engine.get_popular_content_recommendations(top_n=2)
    print("Popular content recommendations:", popular_recommendations)
    
    # Example: Incorporate user feedback
    feedback_data_example = [
        {"user_id": "user_1", "content_id": 0, "liked": True},
        {"user_id": "user_1", "content_id": 2, "liked": False}
    ]
    engine.incorporate_user_feedback(feedback_data_example)
    
    # Example: Get fresh content recommendations
    fresh_recommendations = engine.get_fresh_content_recommendations(top_n=2)
    print("Fresh content recommendations:", fresh_recommendations)
    
    # Example: Get diverse content recommendations
    diverse_recommendations = engine.get_diverse_content_recommendations(top_n=2)
    print("Diverse content recommendations:", diverse_recommendations)
    
    # Example: Get hybrid recommendations (if needed)
    user_profile = engine._generate_user_profile("user_1")
    hybrid_recommendations = engine._combine_content_based_and_collaborative_filtering(user_profile, top_n=2)
    print("Hybrid content recommendations:", hybrid_recommendations)
    
    # Example: Get contextual content recommendations
    contextual_factors = {"freshness": 0.5, "diversity_score": 0.5}
    contextual_recommendations = engine.get_contextual_content_recommendations(contextual_factors, top_n=2)
    print("Contextual content recommendations:", contextual_recommendations)

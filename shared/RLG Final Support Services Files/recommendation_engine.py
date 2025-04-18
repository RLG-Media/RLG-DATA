import logging
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

logger = logging.getLogger(__name__)

class ContentRecommendations:
    """Class for generating content recommendations based on user behavior and content attributes."""

    def __init__(self, user_history, content_database, content_features):
        self.user_history = user_history  # Mechanism to access user interactions with content.
        self.content_database = content_database  # Database or storage of content information.
        self.content_features = content_features  # Feature vectors for all available content.

    def _generate_user_profile(self, user_id):
        """Generate a user profile based on their interaction history."""
        user_content_interactions = self.user_history.get_user_interactions(user_id)
        content_vectors = [self.content_features[content_id] for content_id in user_content_interactions]
        user_profile = np.mean(content_vectors, axis=0) if content_vectors else np.zeros_like(self.content_features[0])
        logger.info(f"Generated user profile for User ID: {user_id}")
        return user_profile

    def _calculate_similarities(self, user_profile):
        """Calculate cosine similarity between the user profile and content features."""
        similarities = cosine_similarity([user_profile], self.content_features)
        return similarities[0]

    def get_top_recommendations(self, user_id, top_n=10):
        """Retrieve top content recommendations for a user."""
        try:
            user_profile = self._generate_user_profile(user_id)
            similarities = self._calculate_similarities(user_profile)
            sorted_indices = np.argsort(similarities)[::-1]  # Sort by similarity descending
            recommended_content = [self.content_database[idx] for idx in sorted_indices[:top_n]]
            logger.info(f"Top {top_n} recommendations fetched for User ID: {user_id}")
            return recommended_content
        except Exception as e:
            logger.error(f"Error generating content recommendations: {e}")
            return []

    def get_content_by_tags(self, tags, top_n=5):
        """Fetch content based on specific tags for recommendation purposes."""
        try:
            tagged_content = [content for content in self.content_database if any(tag in content['tags'] for tag in tags)]
            sorted_content = sorted(tagged_content, key=lambda x: x['popularity'], reverse=True)[:top_n]
            logger.info(f"Content fetched by tags: {tags}, Top {top_n}")
            return sorted_content
        except Exception as e:
            logger.error(f"Error fetching content by tags: {e}")
            return []

    def get_new_content_recommendations(self, user_id, new_content, top_n=10):
        """Provide recommendations based on newly added content."""
        try:
            user_profile = self._generate_user_profile(user_id)
            new_content_features = [content['features'] for content in new_content]
            all_features = np.vstack([self.content_features] + new_content_features)
            similarities = cosine_similarity([user_profile], all_features)
            sorted_indices = np.argsort(similarities[0])[::-1]
            recommended_content = [self.content_database[idx] for idx in sorted_indices[:top_n]]
            logger.info(f"New content recommendations fetched for User ID: {user_id}, Top {top_n}")
            return recommended_content
        except Exception as e:
            logger.error(f"Error generating new content recommendations: {e}")
            return []

    # Additional recommendations
    def _calculate_popularity_based_similarities(self, content_id):
        """Calculate popularity-based similarities."""
        content_popularity = self.content_database[content_id]['popularity']
        all_content_popularity = [content['popularity'] for content in self.content_database]
        return cosine_similarity([[content_popularity]], [all_content_popularity])[0]

    def get_popular_content_recommendations(self, top_n=10):
        """Get content recommendations based on popularity."""
        try:
            similarities = [self._calculate_popularity_based_similarities(content_id) for content_id in range(len(self.content_database))]
            sorted_indices = np.argsort(similarities)[::-1]  # Sort by popularity descending
            popular_content = [self.content_database[idx] for idx in sorted_indices[:top_n]]
            logger.info(f"Popular content recommendations fetched, Top {top_n}")
            return popular_content
        except Exception as e:
            logger.error(f"Error generating popular content recommendations: {e}")
            return []

    # Additional Enhancements
    def _combine_content_based_and_collaborative_filtering(self, user_profile, top_n=10):
        """Hybrid recommendation combining content-based and collaborative filtering."""
        try:
            content_similarities = self._calculate_similarities(user_profile)
            popularity_similarities = self._calculate_popularity_based_similarities(user_profile)
            combined_similarities = (content_similarities + popularity_similarities) / 2
            sorted_indices = np.argsort(combined_similarities)[::-1]
            recommended_content = [self.content_database[idx] for idx in sorted_indices[:top_n]]
            logger.info(f"Hybrid recommendations fetched, Top {top_n}")
            return recommended_content
        except Exception as e:
            logger.error(f"Error combining recommendations: {e}")
            return []

    def _enable_real_time_updates(self, user_id, new_content, top_n=10):
        """Real-time recommendation updates based on changing user preferences."""
        try:
            updated_user_profile = self._generate_user_profile(user_id)
            similarities = self._calculate_similarities(updated_user_profile)
            new_content_features = [content['features'] for content in new_content]
            all_features = np.vstack([self.content_features] + new_content_features)
            updated_similarities = cosine_similarity([updated_user_profile], all_features)
            sorted_indices = np.argsort(updated_similarities[0])[::-1]
            recommended_content = [self.content_database[idx] for idx in sorted_indices[:top_n]]
            logger.info(f"Real-time recommendations fetched for User ID: {user_id}, Top {top_n}")
            return recommended_content
        except Exception as e:
            logger.error(f"Error enabling real-time updates: {e}")
            return []

    # Incorporating additional recommendation factors
    def _calculate_freshness_based_similarities(self, content_id):
        """Content freshness and recency-based recommendations."""
        content_freshness = self.content_database[content_id]['freshness']
        all_content_freshness = [content['freshness'] for content in self.content_database]
        return cosine_similarity([[content_freshness]], [all_content_freshness])[0]

    def get_fresh_content_recommendations(self, top_n=10):
        """Content recommendations based on freshness and recency."""
        try:
            similarities = [self._calculate_freshness_based_similarities(content_id) for content_id in range(len(self.content_database))]
            sorted_indices = np.argsort(similarities)[::-1]
            fresh_content = [self.content_database[idx] for idx in sorted_indices[:top_n]]
            logger.info(f"Fresh content recommendations fetched, Top {top_n}")
            return fresh_content
        except Exception as e:
            logger.error(f"Error generating freshness-based content recommendations: {e}")
            return []

    # Adding user feedback to refine recommendations
    def incorporate_user_feedback(self, feedback_data):
        """Use user feedback to refine content recommendations."""
        try:
            for feedback in feedback_data:
                user_id = feedback['user_id']
                content_id = feedback['content_id']
                liked = feedback['liked']
                if liked:
                    self.content_features[content_id] *= 1.1
                else:
                    self.content_features[content_id] *= 0.9
            logger.info("User feedback incorporated into content features.")
        except Exception as e:
            logger.error(f"Error incorporating user feedback: {e}")

    # Content diversity and contextual recommendations
    def _calculate_diversity_based_similarities(self, content_id):
        """Content diversity calculation based on various attributes."""
        content_diversity = self.content_database[content_id]['diversity_score']
        all_content_diversity = [content['diversity_score'] for content in self.content_database]
        return cosine_similarity([[content_diversity]], [all_content_diversity])[0]

    def get_diverse_content_recommendations(self, top_n=10):
        """Get diverse content recommendations."""
        try:
            similarities = [self._calculate_diversity_based_similarities(content_id) for content_id in range(len(self.content_database))]
            sorted_indices = np.argsort(similarities)[::-1]
            diverse_content = [self.content_database[idx] for idx in sorted_indices[:top_n]]
            logger.info(f"Diverse content recommendations fetched, Top {top_n}")
            return diverse_content
        except Exception as e:
            logger.error(f"Error generating diversity-based content recommendations: {e}")
            return []

    def _optimize_content_discovery(self, contextual_factors, top_n=10):
        """Optimize content discovery based on contextual factors."""
        try:
            content_scores = []
            for content in self.content_database:
                score = 0
                for key, value in contextual_factors.items():
                    score += content[key] * value
                content_scores.append(score)
            sorted_indices = np.argsort(content_scores)[::-1]
            optimized_content = [self.content_database[idx] for idx in sorted_indices[:top_n]]
            logger.info(f"Contextual content discovery optimized, Top {top_n}")
            return optimized_content
        except Exception as e:
            logger.error(f"Error optimizing content discovery: {e}")
            return []

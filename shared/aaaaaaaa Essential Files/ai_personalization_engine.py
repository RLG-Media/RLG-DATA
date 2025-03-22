import logging
from typing import Dict, Any, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json

# Configure logging: logs will be output to both file and console.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("ai_personalization_engine.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AIPersonalizationEngine:
    """
    AI Personalization Engine for RLG Data and RLG Fans.
    
    Provides tailored content recommendations and personalized user experiences using
    collaborative filtering and content-based similarity via TF-IDF vectorization.
    """
    
    def __init__(self, model_config: Dict[str, Any]):
        """
        Initialize the AI Personalization Engine.
        
        Args:
            model_config (Dict[str, Any]): Configuration dictionary for model parameters.
                Example: {"max_features": 5000, "ngram_range": (1,2), ...}
        """
        self.model_config = model_config
        self.vectorizer = TfidfVectorizer(**model_config)
        logger.info("AI Personalization Engine initialized with model configuration: %s", model_config)

    def preprocess_data(self, data: List[str]) -> Any:
        """
        Preprocess text data for model input using TF-IDF vectorization.
        
        Args:
            data (List[str]): List of text strings to preprocess.
        
        Returns:
            Transformed data (sparse matrix) suitable for similarity computation.
        
        Raises:
            Exception: If data preprocessing fails.
        """
        try:
            transformed_data = self.vectorizer.fit_transform(data)
            logger.info("Data successfully preprocessed with TF-IDF.")
            return transformed_data
        except Exception as e:
            logger.error("Error during data preprocessing: %s", e)
            raise

    def generate_recommendations(self, user_data: str, content_pool: List[str]) -> List[Dict[str, Any]]:
        """
        Generate personalized recommendations based on user input and a pool of content.
        
        Args:
            user_data (str): User's input or preferences (e.g., a search query, recent activity text).
            content_pool (List[str]): List of content items (e.g., titles or descriptions) to compare.
        
        Returns:
            List[Dict[str, Any]]: A list of recommended content items with relevance scores.
                Example: [{"content": "Title A", "score": 0.85}, ...]
        """
        try:
            # Combine the user's input with the content pool for vectorization.
            data = [user_data] + content_pool
            transformed_data = self.preprocess_data(data)
            # Compute cosine similarity between the user input and each content item.
            similarities = cosine_similarity(transformed_data[0:1], transformed_data[1:]).flatten()
            recommendations = [
                {"content": content_pool[i], "score": similarities[i]} for i in range(len(content_pool))
            ]
            # Sort recommendations by score in descending order.
            recommendations.sort(key=lambda x: x["score"], reverse=True)
            logger.info("Generated %d recommendations.", len(recommendations))
            return recommendations
        except Exception as e:
            logger.error("Error during recommendation generation: %s", e)
            raise

    def personalize_content(self, user_profile: Dict[str, Any], content_pool: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Personalize content for the user based on their profile and preferences.
        
        This method filters the content pool by matching content tags with keywords from the user profile.
        
        Args:
            user_profile (Dict[str, Any]): Dictionary containing user information (e.g., {"keywords": ["AI", "data"]}).
            content_pool (List[Dict[str, Any]]): List of content dictionaries (each should include a "tags" key).
        
        Returns:
            List[Dict[str, Any]]: List of content items that match the user's preferences.
        """
        try:
            keywords = [kw.lower() for kw in user_profile.get("keywords", [])]
            personalized_content = [
                content for content in content_pool
                if any(keyword in [tag.lower() for tag in content.get("tags", [])] for keyword in keywords)
            ]
            logger.info("Personalized content filtered based on user profile.")
            return personalized_content
        except Exception as e:
            logger.error("Error during content personalization: %s", e)
            raise

    def analyze_behavior(self, user_behavior_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze user behavior to derive deeper personalization insights.
        
        Args:
            user_behavior_data (List[Dict[str, Any]]): List of user activity logs, each containing metrics like "views" and "engagement".
        
        Returns:
            Dict[str, Any]: Dictionary containing insights, e.g., most viewed category and aggregate engagement score.
        """
        try:
            if not user_behavior_data:
                logger.warning("No user behavior data provided.")
                return {}
            # Determine the category with the highest views.
            most_viewed = max(user_behavior_data, key=lambda x: x.get("views", 0)).get("category", "None")
            total_engagement = sum(item.get("engagement", 0) for item in user_behavior_data)
            insights = {
                "most_viewed_category": most_viewed,
                "engagement_score": total_engagement
            }
            logger.info("User behavior analysis completed.")
            return insights
        except Exception as e:
            logger.error("Error during user behavior analysis: %s", e)
            raise

    def save_model_state(self, file_path: str):
        """
        Save the current model configuration state to a file.
        
        Args:
            file_path (str): The path to save the model state (as JSON).
        """
        try:
            with open(file_path, "w") as file:
                json.dump(self.model_config, file)
            logger.info("Model state saved to %s", file_path)
        except Exception as e:
            logger.error("Error saving model state: %s", e)
            raise

    def load_model_state(self, file_path: str):
        """
        Load a model state from a file.
        
        Args:
            file_path (str): The path from which to load the model state.
        """
        try:
            with open(file_path, "r") as file:
                self.model_config = json.load(file)
            logger.info("Model state loaded from %s", file_path)
        except Exception as e:
            logger.error("Error loading model state: %s", e)
            raise

# -------------------------------
# Additional Recommendations:
# -------------------------------
# 1. For even more accurate personalization, consider combining the TF-IDF approach with advanced deep learning models.
# 2. Integrate additional contextual data such as region, location, and recent trends into the recommendation process.
# 3. Use asynchronous processing (e.g., via Celery) to handle large-scale recommendation generation.
# 4. Enhance evaluation metrics (like user click-through rate or satisfaction scores) to continuously refine the model.
# 5. Securely log recommendation outputs and performance metrics for monitoring and debugging.

# -------------------------------
# Standalone Testing Example:
# -------------------------------
if __name__ == "__main__":
    # Initialize the engine with example model configuration.
    engine = AIPersonalizationEngine(model_config={"max_features": 5000, "ngram_range": (1, 2)})

    # Example user input and content pool (list of content titles)
    user_data = "Advancements in AI and data analytics in 2023"
    content_pool = [
        "Latest AI Trends in 2023",
        "Data Science: A Comprehensive Guide",
        "Machine Learning Breakthroughs",
        "Innovative Data Solutions",
        "AI Ethics and Regulation"
    ]

    recommendations = engine.generate_recommendations(user_data, content_pool)
    print("Recommendations:", recommendations)

    # Example user profile and content pool with tags for personalization.
    user_profile = {"keywords": ["AI", "data"]}
    content_pool_dict = [
        {"title": "AI Trends", "tags": ["AI", "technology"], "popularity": 80},
        {"title": "Data Science 101", "tags": ["data", "education"], "popularity": 70},
        {"title": "Machine Learning Basics", "tags": ["ML", "AI"], "popularity": 85}
    ]
    personalized = engine.personalize_content(user_profile, content_pool_dict)
    print("Personalized Content:", personalized)

    # Example user behavior analysis.
    user_behavior_data = [
        {"category": "AI", "views": 15, "engagement": 80},
        {"category": "Data Science", "views": 10, "engagement": 50}
    ]
    insights = engine.analyze_behavior(user_behavior_data)
    print("Behavior Insights:", insights)

    # Save and load model state example.
    engine.save_model_state("ai_personalization_state.json")
    engine.load_model_state("ai_personalization_state.json")

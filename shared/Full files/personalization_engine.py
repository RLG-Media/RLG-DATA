import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors
import logging

# Configure logging for the personalization engine
logger = logging.getLogger("PersonalizationEngine")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

class PersonalizationEngine:
    """
    PersonalizationEngine class to provide personalized content recommendations using collaborative filtering.
    
    This class uses a user–item interaction matrix (as a Pandas DataFrame) where rows represent users and 
    columns represent items (e.g., content IDs). It normalizes the matrix, fits a nearest neighbors model,
    and then uses cosine similarity to recommend items for each user.
    
    Attributes:
        user_item_matrix (pd.DataFrame): The raw user–item interaction matrix.
        k (int): The number of neighbors to consider.
        scaler (MinMaxScaler): Scaler for normalizing interaction values.
        model (NearestNeighbors): Nearest neighbors model fitted on normalized data.
        user_item_matrix_scaled (np.array): Normalized matrix.
    """
    
    def __init__(self, user_item_matrix, k=10):
        """
        Initializes the PersonalizationEngine with a user–item matrix and number of neighbors.
        
        Args:
            user_item_matrix (pd.DataFrame): DataFrame with users as rows and items as columns.
            k (int, optional): Number of neighbors to consider. Default is 10.
        """
        self.user_item_matrix = user_item_matrix
        self.k = k
        self.scaler = MinMaxScaler()
        self.model = NearestNeighbors(n_neighbors=self.k, metric='cosine')
        self._fit_model()
    
    def _fit_model(self):
        """
        Fits the nearest neighbors model on the normalized user–item matrix.
        
        Missing values are filled with 0 before scaling.
        """
        # Fill missing values and scale the matrix
        self.user_item_matrix_scaled = self.scaler.fit_transform(self.user_item_matrix.fillna(0))
        # Fit the nearest neighbors model on the scaled matrix
        self.model.fit(self.user_item_matrix_scaled)
        logger.info("NearestNeighbors model fitted on the scaled user–item matrix.")
    
    def _get_user_vector(self, user_id):
        """
        Retrieves the normalized user vector for the given user_id.
        
        Note: This assumes that the user_item_matrix index corresponds to user_id's integer position.
        For non-integer indices, consider using .loc or .iloc appropriately.
        
        Args:
            user_id: The identifier of the user.
            
        Returns:
            np.array: The normalized interaction vector for the user.
        """
        try:
            # If user_item_matrix is indexed by user_id, adjust accordingly (e.g., .loc[user_id])
            user_index = self.user_item_matrix.index.get_loc(user_id)
            return self.user_item_matrix_scaled[user_index]
        except Exception as e:
            logger.error("Error retrieving user vector for user_id %s: %s", user_id, e)
            raise
    
    def _recommend_items(self, user_vector):
        """
        Recommends items based on the cosine similarity of the given user vector.
        
        Args:
            user_vector (np.array): The normalized interaction vector for the user.
            
        Returns:
            pd.Index: The list of item column names corresponding to the recommended items.
        """
        distances, indices = self.model.kneighbors([user_vector], n_neighbors=self.k)
        recommendations = self.user_item_matrix.columns[indices.flatten()]
        return recommendations

    def generate_personalized_recommendations(self, user_id):
        """
        Generates personalized item recommendations for a given user.
        
        Args:
            user_id: The identifier of the user.
            
        Returns:
            list: A list of recommended item identifiers.
        """
        user_vector = self._get_user_vector(user_id)
        recommendations = self._recommend_items(user_vector)
        logger.info("Generated recommendations for user %s: %s", user_id, recommendations.tolist())
        return recommendations.tolist()
    
    def update_user_preferences(self, user_id, item_id, interaction_value):
        """
        Updates the user–item matrix with a new interaction and refits the model.
        
        Args:
            user_id: The identifier of the user.
            item_id: The identifier of the item.
            interaction_value: The new interaction value (e.g., rating, like count).
        """
        self.user_item_matrix.at[user_id, item_id] = interaction_value
        logger.info("Updated user %s preferences for item %s with value %s", user_id, item_id, interaction_value)
        self._fit_model()  # Refit the model to incorporate the update
    
    def evaluate_model(self, test_data):
        """
        Evaluates the recommendation model using test data.
        
        The test_data DataFrame should include columns 'user_id' and 'item_id', where 'item_id' is a comma-separated
        string of actual items interacted with by the user.
        
        Returns:
            tuple: (precision, recall) scores averaged over the test dataset.
        """
        predictions = test_data.apply(lambda x: self.generate_personalized_recommendations(x['user_id']), axis=1)
        
        precision = 0
        recall = 0
        for i, row in test_data.iterrows():
            actual_items = set(row['item_id'].split(','))
            recommended_items = set(predictions[i])
            precision += len(actual_items & recommended_items) / len(recommended_items) if recommended_items else 0
            recall += len(actual_items & recommended_items) / len(actual_items) if actual_items else 0
        
        n = len(test_data)
        precision /= n
        recall /= n
        logger.info("Model evaluation completed with precision: %.4f and recall: %.4f", precision, recall)
        return precision, recall
    
    def save_model(self, filepath):
        """
        Saves the current user–item matrix and scaler to a file using pickle.
        
        Args:
            filepath (str): The path to save the model.
        """
        try:
            pd.to_pickle((self.user_item_matrix, self.scaler), filepath)
            logger.info("Model saved to %s", filepath)
        except Exception as e:
            logger.error("Error saving model: %s", e)
            raise
    
    def load_model(self, filepath):
        """
        Loads a saved user–item matrix and scaler from a pickle file, then refits the model.
        
        Args:
            filepath (str): The path to load the model from.
        """
        try:
            self.user_item_matrix, self.scaler = pd.read_pickle(filepath)
            self._fit_model()
            logger.info("Model loaded from %s", filepath)
        except Exception as e:
            logger.error("Error loading model: %s", e)
            raise

# -------------------------------
# Additional Recommendations:
# -------------------------------
# 1. For region/country/city/town awareness, consider extending the user_item_matrix to include metadata
#    (or maintain a separate mapping) and adjust recommendations accordingly.
# 2. Explore other collaborative filtering approaches or hybrid models to improve recommendation quality.
# 3. Implement caching or asynchronous updates if the matrix is large or the system faces high traffic.
# 4. Integrate A/B testing to measure the effectiveness of recommendations in a live environment.
# 5. Enhance evaluation methods by incorporating additional metrics (e.g., RMSE for rating predictions).

# -------------------------------
# Standalone Testing Example:
# -------------------------------
if __name__ == "__main__":
    # Create a sample user–item interaction matrix
    data = {
        'item_A': [5, 3, np.nan, 1],
        'item_B': [4, np.nan, 2, 1],
        'item_C': [np.nan, 4, 5, 2],
        'item_D': [1, 2, 3, 4]
    }
    user_ids = ['user_1', 'user_2', 'user_3', 'user_4']
    user_item_matrix = pd.DataFrame(data, index=user_ids)
    
    # Initialize the personalization engine with the sample matrix
    engine = PersonalizationEngine(user_item_matrix, k=3)
    
    # Generate recommendations for a specific user
    recommendations = engine.generate_personalized_recommendations('user_1')
    print("Recommendations for user_1:", recommendations)
    
    # Update user preferences (simulate new interaction) and generate recommendations again
    engine.update_user_preferences('user_1', 'item_C', 4)
    updated_recommendations = engine.generate_personalized_recommendations('user_1')
    print("Updated recommendations for user_1:", updated_recommendations)
    
    # For evaluation, create a dummy test set (adjust as needed)
    test_data = pd.DataFrame({
        'user_id': ['user_1', 'user_2'],
        'item_id': ['item_A,item_C', 'item_B,item_D']
    })
    precision, recall = engine.evaluate_model(test_data)
    print(f"Evaluation - Precision: {precision:.4f}, Recall: {recall:.4f}")
    
    # Save and load the model
    engine.save_model("personalization_model.pkl")
    engine.load_model("personalization_model.pkl")

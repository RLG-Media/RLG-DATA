import logging
from typing import Any
import numpy as np
from sklearn.decomposition import TruncatedSVD

# Configure logging (if not already configured elsewhere)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def collaborative_filtering(user_item_matrix: np.ndarray, n_components: int = 10) -> np.ndarray:
    """
    Perform collaborative filtering using Truncated SVD on the user-item matrix.

    This function factorizes the user-item matrix using TruncatedSVD to capture latent factors,
    and then reconstructs the matrix to predict missing values or generate recommendation scores.
    
    Args:
        user_item_matrix (np.ndarray): A 2D NumPy array where rows represent users and columns represent items.
        n_components (int): The number of latent factors to extract (default is 10).
    
    Returns:
        np.ndarray: A reconstructed matrix (predicted scores) of the same shape as the input matrix.
    
    Raises:
        ValueError: If the input matrix is not a 2D NumPy array.
        Exception: For other errors during matrix decomposition or reconstruction.
    
    Additional Recommendations:
        - Consider normalizing the user_item_matrix before factorization for improved performance.
        - Experiment with different values of n_components to find the optimal latent factor dimension.
        - Extend this function to return recommendations (e.g., top N items per user) based on the predicted scores.
    """
    try:
        if not isinstance(user_item_matrix, np.ndarray) or user_item_matrix.ndim != 2:
            raise ValueError("user_item_matrix must be a 2D NumPy array.")

        logger.info("Starting collaborative filtering with n_components=%d", n_components)
        # Initialize and fit the Truncated SVD model.
        svd = TruncatedSVD(n_components=n_components, random_state=42)
        decomposed_matrix = svd.fit_transform(user_item_matrix)
        logger.info("Matrix decomposition completed successfully.")

        # Reconstruct the matrix to obtain predicted scores.
        predicted_scores = np.dot(decomposed_matrix, svd.components_)
        logger.info("Reconstructed matrix with predicted scores successfully.")
        return predicted_scores

    except Exception as e:
        logger.error(f"Error in collaborative filtering: {e}")
        raise

# -------------------------------
# Example Usage (for testing purposes)
# -------------------------------
if __name__ == "__main__":
    # Example user-item matrix (rows: users, columns: items)
    # In a real scenario, replace this with your actual interaction matrix.
    sample_matrix = np.array([
        [5, 3, 0, 1],
        [4, 0, 0, 1],
        [1, 1, 0, 5],
        [1, 0, 0, 4],
        [0, 1, 5, 4],
    ])

    try:
        predicted = collaborative_filtering(sample_matrix, n_components=2)
        print("Predicted Scores Matrix:")
        print(predicted)
    except Exception as error:
        print(f"An error occurred during collaborative filtering: {error}")

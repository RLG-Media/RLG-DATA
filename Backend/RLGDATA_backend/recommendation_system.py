import logging
from typing import Dict, List, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def create_user_profile(user_data: Dict[str, Any]) -> str:
    """
    Combine user data into a single profile string for analysis.
    
    Args:
        user_data (Dict[str, Any]): Dictionary containing user preferences,
                                    e.g., {'keywords': [...], 'previous_tools': [...]}.
    
    Returns:
        str: A concatenated string representing the user's profile.
    """
    try:
        keywords = user_data.get('keywords', [])
        previous_tools = user_data.get('previous_tools', [])
        profile = ' '.join(keywords) + ' ' + ' '.join(previous_tools)
        return profile.strip()
    except Exception as e:
        logger.error(f"Error creating user profile: {e}")
        return ""

def recommend_tools(user_data: Dict[str, Any], available_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Recommend tools based on the similarity between the user's profile and available tool descriptions.
    
    This function performs the following steps:
      1. Creates a user profile string from the user_data.
      2. Extracts tool descriptions from available_tools.
      3. Vectorizes the user profile and tool descriptions using TF-IDF.
      4. Computes cosine similarity between the user profile and each tool's description.
      5. Returns the list of tools sorted by similarity (highest first).

    Args:
        user_data (Dict[str, Any]): User preferences and previous interactions.
        available_tools (List[Dict[str, Any]]): List of tool dictionaries with at least a 'description' key.
    
    Returns:
        List[Dict[str, Any]]: Sorted list of recommended tools.
    """
    try:
        # Step 1: Create a user profile
        user_profile = create_user_profile(user_data)
        if not user_profile:
            logger.warning("User profile is empty. Unable to provide recommendations.")
            return []

        # Step 2: Extract descriptions from available tools that have a valid description.
        tool_descriptions = []
        valid_tools = []
        for tool in available_tools:
            desc = tool.get('description', '').strip()
            if desc:
                tool_descriptions.append(desc)
                valid_tools.append(tool)
        
        if not tool_descriptions:
            logger.warning("No available tools with valid descriptions.")
            return []

        # Step 3: Prepare the combined text data.
        # The first element is the user profile, followed by the tool descriptions.
        all_texts = [user_profile] + tool_descriptions

        # Step 4: Vectorize using TF-IDF
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(all_texts)

        # Step 5: Compute cosine similarity between user profile and each tool description.
        similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

        # Step 6: Sort the valid tools by similarity scores in descending order.
        sorted_indices = np.argsort(similarity_scores)[::-1]
        recommended_tools = [valid_tools[i] for i in sorted_indices]

        logger.info(f"Recommended {len(recommended_tools)} tools based on user profile.")
        return recommended_tools
    except Exception as e:
        logger.error(f"Error in recommending tools: {e}")
        return []

# -------------------------------
# Example Usage (for testing purposes)
# -------------------------------
if __name__ == "__main__":
    # Example user data
    sample_user_data = {
        "keywords": ["data analysis", "machine learning", "automation"],
        "previous_tools": ["Google Analytics", "SEO Insights"]
    }
    
    # Example available tools
    sample_tools = [
        {
            "name": "Sentiment Analysis",
            "description": "Analyze social media sentiment in real-time.",
            "link": "/sentiment-analysis"
        },
        {
            "name": "Brand Health Monitoring",
            "description": "Monitor your brand's online presence and mentions.",
            "link": "/brand-health"
        },
        {
            "name": "Content Planning",
            "description": "Generate content ideas based on trending topics.",
            "link": "/content-planning"
        }
    ]
    
    recommendations = recommend_tools(sample_user_data, sample_tools)
    print("Recommended Tools:")
    for tool in recommendations:
        print(f"- {tool.get('name')}: {tool.get('description')}")

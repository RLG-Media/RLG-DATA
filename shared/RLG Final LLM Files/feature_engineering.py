# feature_engineering.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, f_classif
import logging
from your_project_name.config import FEATURE_ENGINEERING_CONFIG
from your_project_name.data_cleaning import clean_data
from your_project_name.error_handling import handle_error

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for feature engineering
PLATFORM_LIST = ['OnlyFans', 'Patreon', 'Fansly', 'Instagram', 'TikTok', 'YouTube']
SCALING_METHOD = 'standard'  # Options: 'standard', 'minmax'
FEATURE_SELECTION_METHOD = 'kbest'  # Options: 'kbest', 'pca'


def generate_features(platforms=PLATFORM_LIST, start_date=None, end_date=None, scaling_method=SCALING_METHOD, feature_selection_method=FEATURE_SELECTION_METHOD):
    """
    Generate engineered features for specified platforms and date range.
    
    Args:
        platforms (list): List of platforms to analyze.
        start_date (str): Optional start date for filtering the data (format: 'YYYY-MM-DD').
        end_date (str): Optional end date for filtering the data (format: 'YYYY-MM-DD').
        scaling_method (str): Method for scaling data ('standard' or 'minmax').
        feature_selection_method (str): Method for feature selection ('kbest' or 'pca').
    
    Returns:
        features_df (DataFrame): DataFrame with engineered features.
    """
    try:
        logger.info(f"Generating features for platforms: {', '.join(platforms)}")

        all_features = []

        for platform in platforms:
            # Step 1: Fetch and clean data for the platform
            platform_data = fetch_and_clean_data(platform, start_date, end_date)
            
            if platform_data is None or platform_data.empty:
                logger.warning(f"No valid data available for platform: {platform}")
                continue

            # Step 2: Feature engineering
            features = perform_feature_engineering(platform_data, platform, scaling_method, feature_selection_method)

            if features is not None:
                features['platform'] = platform
                all_features.append(features)

        # Step 3: Combine features from all platforms
        features_df = pd.concat(all_features, ignore_index=True)

        # Step 4: Save the engineered features
        save_engineered_features(features_df)

        return features_df

    except Exception as e:
        handle_error(e)
        return None


def fetch_and_clean_data(platform, start_date=None, end_date=None):
    """
    Fetch and clean data for a specific platform.
    
    Args:
        platform (str): The platform name (e.g., 'OnlyFans', 'Patreon').
        start_date (str): Optional start date for filtering.
        end_date (str): Optional end date for filtering.
    
    Returns:
        cleaned_data (DataFrame): The cleaned data for the platform.
    """
    try:
        logger.info(f"Fetching and cleaning data for platform: {platform}")

        # Fetch raw data from the database or APIs
        raw_data = get_platform_data(platform, start_date, end_date)
        
        # Clean the data
        cleaned_data = clean_data(raw_data, platform)
        
        if cleaned_data.empty:
            logger.warning(f"No cleaned data available for platform: {platform}")
        
        return cleaned_data

    except Exception as e:
        handle_error(e)
        return pd.DataFrame()


def perform_feature_engineering(data, platform, scaling_method='standard', feature_selection_method='kbest'):
    """
    Perform feature engineering on the cleaned data.
    
    Args:
        data (DataFrame): The cleaned data for feature engineering.
        platform (str): The platform name for which the feature engineering is performed.
        scaling_method (str): The scaling method ('standard' or 'minmax').
        feature_selection_method (str): The feature selection method ('kbest' or 'pca').
    
    Returns:
        engineered_features (DataFrame): DataFrame with engineered features.
    """
    try:
        logger.info(f"Performing feature engineering for platform: {platform}")

        # Step 1: Basic feature extraction (e.g., creating new columns or aggregations)
        engineered_data = extract_basic_features(data)

        # Step 2: Scaling the features
        scaled_data = scale_data(engineered_data, scaling_method)

        # Step 3: Feature selection
        final_features = select_features(scaled_data, feature_selection_method)

        return final_features

    except Exception as e:
        handle_error(e)
        return pd.DataFrame()


def extract_basic_features(data):
    """
    Extract basic features from the raw data (e.g., interactions, engagement rates, etc.).
    
    Args:
        data (DataFrame): Raw cleaned data to extract features from.
    
    Returns:
        engineered_data (DataFrame): DataFrame with basic features.
    """
    try:
        logger.info("Extracting basic features from the data")

        engineered_data = data.copy()

        # Example: Calculate engagement rate
        engineered_data['engagement_rate'] = engineered_data['likes'] / engineered_data['followers']
        
        # Example: Calculate average interaction per post
        engineered_data['avg_interaction_per_post'] = engineered_data['likes'] / engineered_data['posts']
        
        # Add other relevant features based on domain knowledge

        return engineered_data

    except Exception as e:
        handle_error(e)
        return data


def scale_data(data, scaling_method='standard'):
    """
    Scale the data using the specified scaling method.
    
    Args:
        data (DataFrame): The data to scale.
        scaling_method (str): The scaling method to use ('standard' or 'minmax').
    
    Returns:
        scaled_data (DataFrame): The scaled data.
    """
    try:
        logger.info(f"Scaling data using method: {scaling_method}")

        if scaling_method == 'standard':
            scaler = StandardScaler()
        elif scaling_method == 'minmax':
            scaler = MinMaxScaler()
        else:
            raise ValueError("Invalid scaling method. Use 'standard' or 'minmax'.")

        # Assuming the numeric columns are those that need scaling
        numeric_columns = data.select_dtypes(include=np.number).columns
        scaled_data = data.copy()
        scaled_data[numeric_columns] = scaler.fit_transform(data[numeric_columns])

        return scaled_data

    except Exception as e:
        handle_error(e)
        return data


def select_features(data, feature_selection_method='kbest'):
    """
    Perform feature selection on the data using the specified method.
    
    Args:
        data (DataFrame): The scaled data to perform feature selection on.
        feature_selection_method (str): The feature selection method to use ('kbest' or 'pca').
    
    Returns:
        selected_data (DataFrame): The data with selected features.
    """
    try:
        logger.info(f"Performing feature selection using method: {feature_selection_method}")

        if feature_selection_method == 'kbest':
            selector = SelectKBest(score_func=f_classif, k='all')  # You can change 'k' to a specific number
            selected_data = selector.fit_transform(data.drop(columns=['platform']), data['platform'])
            selected_columns = data.columns[selector.get_support()]
            selected_data = pd.DataFrame(selected_data, columns=selected_columns)

        elif feature_selection_method == 'pca':
            pca = PCA(n_components=0.95)  # Preserve 95% of variance
            selected_data = pca.fit_transform(data.select_dtypes(include=np.number))

            # Add the PCA components as columns to the data
            selected_data = pd.DataFrame(selected_data, columns=[f'PCA_{i+1}' for i in range(selected_data.shape[1])])
        else:
            raise ValueError("Invalid feature selection method. Use 'kbest' or 'pca'.")

        return selected_data

    except Exception as e:
        handle_error(e)
        return data


def save_engineered_features(features_df):
    """
    Save the engineered features to a CSV file.
    
    Args:
        features_df (DataFrame): The DataFrame containing the engineered features.
    """
    try:
        logger.info("Saving engineered features...")

        # Generate a timestamped file name for the features
        file_name = f"engineered_features_{pd.Timestamp.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        features_path = f"{FEATURE_ENGINEERING_CONFIG['FEATURES_PATH']}/{file_name}"
        
        features_df.to_csv(features_path, index=False)

        logger.info(f"Engineered features saved to: {features_path}")

    except Exception as e:
        handle_error(e)


if __name__ == "__main__":
    # Generate features for the specified platforms and date range
    engineered_features_df = generate_features(platforms=PLATFORM_LIST, start_date="2024-01-01", end_date="2024-12-31")
    
    if engineered_features_df is not None and not engineered_features_df.empty:
        logger.info("Feature engineering completed successfully.")
    else:
        logger.error("Feature engineering failed.")

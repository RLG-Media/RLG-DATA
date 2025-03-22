# data_analysis.py - Processes and analyzes scraped data for insights and recommendations

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import logging
from database import db_session
from models import ContentAnalysis, PlatformInsights
from sentiment_analysis import analyze_sentiment
from engagement_metrics import calculate_engagement_score, calculate_growth_rate

# Configure logging
logging.basicConfig(filename='data_analysis.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')

def process_scraped_data(scraped_data):
    """
    Process raw scraped data into a structured format.
    """
    logging.info("Starting data processing for scraped content.")
    try:
        # Convert scraped data to a DataFrame for analysis
        df = pd.DataFrame(scraped_data)
        df['created_at'] = pd.to_datetime(df['created_at'])

        # Perform initial cleaning
        df['content'] = df['content'].str.strip().fillna('')
        df['engagement_score'] = df.apply(
            lambda row: calculate_engagement_score(row['likes'], row['comments'], row['shares']),
            axis=1
        )

        logging.info("Data processing completed successfully.")
        return df
    except Exception as e:
        logging.error(f"Data processing failed: {str(e)}")
        raise e


def analyze_content_trends(df):
    """
    Analyze content trends to identify high-performing content types and trends.
    """
    logging.info("Starting content trend analysis.")
    try:
        # TF-IDF Vectorization to find trending keywords
        tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=50)
        tfidf_matrix = tfidf_vectorizer.fit_transform(df['content'])
        keywords = tfidf_vectorizer.get_feature_names_out()

        # Identify content similarity
        similarity_matrix = cosine_similarity(tfidf_matrix)
        df['trend_score'] = similarity_matrix.mean(axis=1)

        # Group by content type to analyze performance trends
        content_type_trends = df.groupby('content_type').agg({
            'engagement_score': 'mean',
            'trend_score': 'mean'
        }).sort_values(by='engagement_score', ascending=False)

        logging.info("Content trend analysis completed successfully.")
        return content_type_trends, keywords
    except Exception as e:
        logging.error(f"Content trend analysis failed: {str(e)}")
        raise e


def generate_platform_insights(df, platform_name):
    """
    Generate insights for a given platform based on the processed data.
    """
    logging.info(f"Generating insights for platform: {platform_name}")
    try:
        # Aggregate insights
        avg_engagement = df['engagement_score'].mean()
        growth_rate = calculate_growth_rate(df['created_at'], df['engagement_score'])

        # Sentiment Analysis
        df['sentiment'] = df['content'].apply(analyze_sentiment)
        sentiment_distribution = df['sentiment'].value_counts(normalize=True).to_dict()

        # Save insights to database
        insights = PlatformInsights(
            platform=platform_name,
            avg_engagement_score=avg_engagement,
            growth_rate=growth_rate,
            sentiment_distribution=sentiment_distribution,
            analysis_date=datetime.utcnow()
        )
        db_session.add(insights)
        db_session.commit()

        logging.info(f"Insights for platform {platform_name} generated and saved successfully.")
        return insights
    except Exception as e:
        logging.error(f"Failed to generate insights for platform {platform_name}: {str(e)}")
        raise e


def analyze_user_engagement(df, user_id):
    """
    Analyze user engagement data and identify top content.
    """
    logging.info(f"Analyzing engagement data for user {user_id}")
    try:
        # Filter user's data and identify high-engagement content
        user_df = df[df['user_id'] == user_id]
        top_content = user_df.sort_values(by='engagement_score', ascending=False).head(5)

        # Summarize engagement data
        avg_likes = user_df['likes'].mean()
        avg_comments = user_df['comments'].mean()
        avg_shares = user_df['shares'].mean()
        engagement_summary = {
            "average_likes": avg_likes,
            "average_comments": avg_comments,
            "average_shares": avg_shares,
            "top_content": top_content[['content', 'engagement_score']]
        }

        logging.info(f"Engagement analysis for user {user_id} completed successfully.")
        return engagement_summary
    except Exception as e:
        logging.error(f"Engagement analysis failed for user {user_id}: {str(e)}")
        raise e


def create_recommendations(df, user_id):
    """
    Generate tailored recommendations for the user based on analysis.
    """
    logging.info(f"Generating content recommendations for user {user_id}.")
    try:
        # Identify high-engagement content types
        content_type_performance = df.groupby('content_type')['engagement_score'].mean()
        recommended_content_type = content_type_performance.idxmax()

        # Analyze user's trending keywords
        tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=10)
        tfidf_matrix = tfidf_vectorizer.fit_transform(df['content'])
        keywords = tfidf_vectorizer.get_feature_names_out()

        # Create a recommendation summary
        recommendations = {
            "recommended_content_type": recommended_content_type,
            "trending_keywords": keywords,
            "engagement_strategy": f"Focus on creating more {recommended_content_type} content "
                                   f"and use trending keywords like {', '.join(keywords)}"
        }

        # Save recommendations to the database
        recommendation_entry = ContentAnalysis(
            user_id=user_id,
            recommended_content_type=recommended_content_type,
            trending_keywords=keywords,
            created_at=datetime.utcnow()
        )
        db_session.add(recommendation_entry)
        db_session.commit()

        logging.info(f"Recommendations generated successfully for user {user_id}.")
        return recommendations
    except Exception as e:
        logging.error(f"Failed to generate recommendations for user {user_id}: {str(e)}")
        raise e

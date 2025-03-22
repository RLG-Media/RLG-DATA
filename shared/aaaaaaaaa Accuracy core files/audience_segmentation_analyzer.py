import json
import numpy as np
import pandas as pd
from collections import defaultdict
from sklearn.cluster import KMeans
from sentiment_analysis import SentimentAnalyzer
from engagement_metrics import EngagementCalculator
from demographic_data import DemographicFetcher

class AudienceSegmentationAnalyzer:
    """
    Analyzes and segments audience based on demographics, behavior, engagement, and sentiment analysis.
    Supports data from multiple platforms (Twitter, Facebook, Instagram, LinkedIn, TikTok, etc.).
    """
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.engagement_calculator = EngagementCalculator()
        self.demographic_fetcher = DemographicFetcher()

    def fetch_audience_data(self, platform_data):
        """Aggregates audience data from multiple social media platforms."""
        all_data = []
        for platform, data in platform_data.items():
            df = pd.DataFrame(data)
            df['platform'] = platform
            all_data.append(df)
        return pd.concat(all_data, ignore_index=True)

    def analyze_engagement(self, data):
        """Calculates engagement metrics (likes, shares, comments, reach)."""
        data['engagement_score'] = data.apply(lambda row: self.engagement_calculator.calculate(row), axis=1)
        return data

    def analyze_sentiment(self, data):
        """Performs sentiment analysis on audience comments and posts."""
        data['sentiment_score'] = data['text'].apply(self.sentiment_analyzer.analyze)
        return data

    def segment_audience(self, data, num_clusters=5):
        """Clusters audience into segments based on engagement and sentiment."""
        features = data[['engagement_score', 'sentiment_score']].fillna(0)
        kmeans = KMeans(n_clusters=num_clusters, random_state=42)
        data['segment'] = kmeans.fit_predict(features)
        return data

    def get_demographic_insights(self, data):
        """Fetches demographic insights (age, gender, location) for audience segmentation."""
        demographics = self.demographic_fetcher.fetch_bulk(data['user_id'].unique())
        demographics_df = pd.DataFrame(demographics)
        return data.merge(demographics_df, on='user_id', how='left')

    def generate_report(self, segmented_data):
        """Generates a comprehensive audience segmentation report."""
        report = defaultdict(lambda: {'count': 0, 'avg_engagement': 0, 'avg_sentiment': 0})
        for _, row in segmented_data.iterrows():
            segment = row['segment']
            report[segment]['count'] += 1
            report[segment]['avg_engagement'] += row['engagement_score']
            report[segment]['avg_sentiment'] += row['sentiment_score']
        for segment in report:
            report[segment]['avg_engagement'] /= report[segment]['count']
            report[segment]['avg_sentiment'] /= report[segment]['count']
        return json.dumps(report, indent=4)

    def run_analysis(self, platform_data):
        """Runs the complete audience segmentation analysis pipeline."""
        data = self.fetch_audience_data(platform_data)
        data = self.analyze_engagement(data)
        data = self.analyze_sentiment(data)
        data = self.segment_audience(data)
        data = self.get_demographic_insights(data)
        return self.generate_report(data)

# Example Usage
if __name__ == "__main__":
    mock_data = {
        "Twitter": [{"user_id": 1, "text": "Love this brand!", "likes": 50, "shares": 10}],
        "Facebook": [{"user_id": 2, "text": "Not a fan of the new update", "likes": 5, "shares": 1}],
    }
    analyzer = AudienceSegmentationAnalyzer()
    report = analyzer.run_analysis(mock_data)
    print(report)

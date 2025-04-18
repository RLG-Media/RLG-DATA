import logging
from typing import List, Dict, Optional
from textblob import TextBlob
from collections import Counter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("user_feedback_sentiment_analyzer.log"),
        logging.StreamHandler()
    ]
)

class UserFeedbackSentimentAnalyzer:
    """
    Analyzes user feedback sentiment for RLG Data and RLG Fans.
    Performs sentiment scoring, feedback categorization, and generates actionable insights.
    """

    def __init__(self):
        logging.info("UserFeedbackSentimentAnalyzer initialized.")

    def analyze_sentiment(self, feedback: str) -> Dict:
        """
        Analyze the sentiment of a single feedback entry.

        Args:
            feedback: The feedback text to analyze.

        Returns:
            A dictionary containing sentiment polarity, subjectivity, and sentiment category.
        """
        try:
            analysis = TextBlob(feedback)
            polarity = analysis.sentiment.polarity
            subjectivity = analysis.sentiment.subjectivity

            sentiment_category = "neutral"
            if polarity > 0.2:
                sentiment_category = "positive"
            elif polarity < -0.2:
                sentiment_category = "negative"

            logging.info("Feedback sentiment analyzed: %s", sentiment_category)

            return {
                "polarity": polarity,
                "subjectivity": subjectivity,
                "category": sentiment_category
            }
        except Exception as e:
            logging.error("Error analyzing sentiment: %s", e)
            return {
                "polarity": 0,
                "subjectivity": 0,
                "category": "error"
            }

    def batch_analyze(self, feedback_list: List[str]) -> List[Dict]:
        """
        Perform sentiment analysis on a batch of feedback entries.

        Args:
            feedback_list: A list of feedback strings to analyze.

        Returns:
            A list of dictionaries containing sentiment analysis results for each feedback.
        """
        logging.info("Starting batch analysis for %d feedback entries.", len(feedback_list))
        results = [self.analyze_sentiment(feedback) for feedback in feedback_list]
        return results

    def generate_summary(self, sentiment_results: List[Dict]) -> Dict:
        """
        Generate a summary report from sentiment analysis results.

        Args:
            sentiment_results: A list of sentiment analysis dictionaries.

        Returns:
            A dictionary summarizing positive, neutral, and negative feedback counts.
        """
        logging.info("Generating summary report.")

        categories = [result["category"] for result in sentiment_results]
        counts = Counter(categories)

        summary = {
            "total_feedback": len(sentiment_results),
            "positive": counts.get("positive", 0),
            "neutral": counts.get("neutral", 0),
            "negative": counts.get("negative", 0)
        }

        logging.info("Summary generated: %s", summary)
        return summary

    def actionable_insights(self, feedback_list: List[str]) -> List[Dict]:
        """
        Extract actionable insights from user feedback.

        Args:
            feedback_list: A list of feedback strings to analyze for insights.

        Returns:
            A list of dictionaries containing key actionable insights.
        """
        logging.info("Extracting actionable insights from feedback.")

        insights = []
        for feedback in feedback_list:
            if "bug" in feedback.lower() or "issue" in feedback.lower():
                insights.append({
                    "type": "bug_report",
                    "feedback": feedback
                })
            elif "feature" in feedback.lower() or "add" in feedback.lower():
                insights.append({
                    "type": "feature_request",
                    "feedback": feedback
                })

        logging.info("Extracted %d actionable insights.", len(insights))
        return insights

# Example usage
if __name__ == "__main__":
    analyzer = UserFeedbackSentimentAnalyzer()

    feedback_data = [
        "I love the new dashboard, it's very user-friendly!",
        "There is a bug in the analytics section, it keeps crashing.",
        "The subscription pricing is too high for small businesses.",
        "Could you add a feature for exporting data in CSV format?",
        "Neutral feedback: It works as expected, nothing extraordinary."
    ]

    # Perform sentiment analysis
    results = analyzer.batch_analyze(feedback_data)

    # Generate a summary
    summary = analyzer.generate_summary(results)

    # Extract actionable insights
    insights = analyzer.actionable_insights(feedback_data)

    print("Sentiment Analysis Results:", results)
    print("Summary Report:", summary)
    print("Actionable Insights:", insights)

import openai
from typing import List, Dict
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("ai_content_optimizer.log"),
        logging.StreamHandler()
    ]
)

class AIContentOptimizer:
    """
    Service for optimizing content using AI for RLG Data and RLG Fans.
    Provides keyword optimization, sentiment adjustment, and platform-specific content formatting.
    """

    def __init__(self, openai_api_key: str):
        openai.api_key = openai_api_key
        logging.info("AI Content Optimizer initialized.")

    def optimize_content_for_keywords(self, content: str, keywords: List[str]) -> str:
        """
        Optimize content by emphasizing specified keywords.

        Args:
            content: The original content to optimize.
            keywords: A list of keywords to emphasize.

        Returns:
            Optimized content as a string.
        """
        try:
            prompt = (
                f"Optimize the following content by emphasizing these keywords: {', '.join(keywords)}.\n"
                f"Content: {content}"
            )
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=500
            )
            optimized_content = response.choices[0].text.strip()
            logging.info("Content optimized for keywords.")
            return optimized_content
        except Exception as e:
            logging.error("Failed to optimize content for keywords: %s", e)
            raise

    def adjust_sentiment(self, content: str, target_sentiment: str) -> str:
        """
        Adjust the sentiment of the content to the target sentiment.

        Args:
            content: The original content.
            target_sentiment: The desired sentiment (e.g., "positive", "neutral", "negative").

        Returns:
            Content adjusted for sentiment as a string.
        """
        try:
            prompt = (
                f"Adjust the sentiment of the following content to be {target_sentiment}:\n"
                f"Content: {content}"
            )
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=500
            )
            adjusted_content = response.choices[0].text.strip()
            logging.info("Content sentiment adjusted to %s.", target_sentiment)
            return adjusted_content
        except Exception as e:
            logging.error("Failed to adjust sentiment: %s", e)
            raise

    def format_for_platform(self, content: str, platform: str) -> str:
        """
        Format content specifically for a social media platform.

        Args:
            content: The original content.
            platform: The platform to format the content for (e.g., "Twitter", "Instagram", "LinkedIn").

        Returns:
            Platform-specific formatted content as a string.
        """
        try:
            prompt = (
                f"Format the following content specifically for {platform}. Include any best practices for engagement on {platform}.\n"
                f"Content: {content}"
            )
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=500
            )
            formatted_content = response.choices[0].text.strip()
            logging.info("Content formatted for %s.", platform)
            return formatted_content
        except Exception as e:
            logging.error("Failed to format content for %s: %s", platform, e)
            raise

    def generate_seo_report(self, content: str, target_audience: str) -> Dict:
        """
        Generate an SEO report for the given content.

        Args:
            content: The content to analyze.
            target_audience: The target audience for the content.

        Returns:
            A dictionary containing SEO insights and recommendations.
        """
        try:
            prompt = (
                f"Analyze the following content for SEO performance and provide recommendations tailored to the target audience ({target_audience}):\n"
                f"Content: {content}"
            )
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=500
            )
            seo_report = response.choices[0].text.strip()
            logging.info("SEO report generated.")
            return {"report": seo_report}
        except Exception as e:
            logging.error("Failed to generate SEO report: %s", e)
            raise

# Example usage
if __name__ == "__main__":
    api_key = "your_openai_api_key"
    optimizer = AIContentOptimizer(api_key)

    sample_content = "RLG Data and RLG Fans provide cutting-edge data analytics and social media solutions."
    keywords = ["data analytics", "social media"]
    optimized_content = optimizer.optimize_content_for_keywords(sample_content, keywords)
    print("Optimized Content:", optimized_content)

    sentiment_adjusted_content = optimizer.adjust_sentiment(sample_content, "positive")
    print("Sentiment Adjusted Content:", sentiment_adjusted_content)

    formatted_content = optimizer.format_for_platform(sample_content, "Twitter")
    print("Formatted Content for Twitter:", formatted_content)

    seo_report = optimizer.generate_seo_report(sample_content, "marketing professionals")
    print("SEO Report:", seo_report)

import os
from typing import Dict, Any, Optional, List
from PIL import Image
import moviepy.editor as mp
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer


class ContentOptimizer:
    """
    A comprehensive tool for optimizing content for various platforms and formats.
    """

    def __init__(self):
        """
        Initializes the Content Optimizer with preloaded models and settings.
        """
        nltk.download("punkt")
        nltk.download("stopwords")
        self.supported_platforms = ["Instagram", "TikTok", "YouTube", "Twitter", "LinkedIn"]
        self.image_formats = ["jpg", "jpeg", "png", "webp"]
        self.video_formats = ["mp4", "mov", "avi", "webm"]

    # --- Text Optimization ---
    def optimize_text(self, text: str, platform: str) -> Dict[str, Any]:
        """
        Optimizes text content for a specific platform.
        :param text: The text content to optimize.
        :param platform: The target platform for optimization.
        :return: A dictionary with optimization recommendations.
        """
        word_count = len(text.split())
        sentences = nltk.sent_tokenize(text)
        avg_sentence_length = sum(len(sentence.split()) for sentence in sentences) / len(sentences)
        
        recommendations = []
        
        # Platform-specific checks
        if platform == "Twitter" and word_count > 280:
            recommendations.append("Reduce text length to fit within Twitter's character limit.")
        elif platform == "LinkedIn" and word_count < 300:
            recommendations.append("Expand content for better engagement on LinkedIn.")

        # General recommendations
        if avg_sentence_length > 20:
            recommendations.append("Use shorter sentences for better readability.")
        if len(text.split()) > 3 and len(set(text.split())) / len(text.split()) < 0.5:
            recommendations.append("Avoid repetitive words to improve content quality.")

        return {
            "word_count": word_count,
            "sentence_count": len(sentences),
            "recommendations": recommendations,
        }

    # --- Image Optimization ---
    def optimize_image(self, file_path: str, platform: str) -> Dict[str, Any]:
        """
        Optimizes an image for a specific platform.
        :param file_path: Path to the image file.
        :param platform: The target platform for optimization.
        :return: A dictionary with optimization details.
        """
        if not os.path.exists(file_path):
            return {"error": "File not found."}
        if file_path.split(".")[-1].lower() not in self.image_formats:
            return {"error": "Unsupported image format."}

        image = Image.open(file_path)
        width, height = image.size

        # Platform-specific size recommendations
        platform_recommendations = {
            "Instagram": (1080, 1080),
            "YouTube": (1280, 720),
            "TikTok": (1080, 1920),
        }
        target_size = platform_recommendations.get(platform, (1080, 1080))

        # Resize if necessary
        resized = False
        if width != target_size[0] or height != target_size[1]:
            image = image.resize(target_size)
            resized = True

        return {
            "original_size": (width, height),
            "optimized_size": target_size if resized else (width, height),
            "resized": resized,
        }

    # --- Video Optimization ---
    def optimize_video(self, file_path: str, platform: str) -> Dict[str, Any]:
        """
        Optimizes a video for a specific platform.
        :param file_path: Path to the video file.
        :param platform: The target platform for optimization.
        :return: A dictionary with optimization details.
        """
        if not os.path.exists(file_path):
            return {"error": "File not found."}
        if file_path.split(".")[-1].lower() not in self.video_formats:
            return {"error": "Unsupported video format."}

        video = mp.VideoFileClip(file_path)
        duration = video.duration
        resolution = video.size

        # Platform-specific recommendations
        platform_recommendations = {
            "Instagram": {"max_duration": 60, "resolution": (1080, 1080)},
            "TikTok": {"max_duration": 180, "resolution": (1080, 1920)},
            "YouTube": {"max_duration": None, "resolution": (1920, 1080)},
        }
        recommendations = []
        target = platform_recommendations.get(platform, {"resolution": resolution})

        if target.get("max_duration") and duration > target["max_duration"]:
            recommendations.append(f"Trim video to {target['max_duration']} seconds for {platform}.")
        if resolution != target["resolution"]:
            recommendations.append(f"Adjust resolution to {target['resolution']} for {platform}.")

        return {
            "duration": duration,
            "resolution": resolution,
            "recommendations": recommendations,
        }

    # --- Keyword Recommendations ---
    def suggest_keywords(self, text: str) -> List[str]:
        """
        Suggests keywords for a given text.
        :param text: The text content.
        :return: A list of suggested keywords.
        """
        vectorizer = CountVectorizer(stop_words="english")
        tfidf = TfidfTransformer()
        word_counts = vectorizer.fit_transform([text])
        tfidf_weights = tfidf.fit_transform(word_counts)

        keywords = sorted(
            [(word, tfidf_weights[0, idx]) for word, idx in vectorizer.vocabulary_.items()],
            key=lambda x: x[1],
            reverse=True,
        )
        return [word for word, _ in keywords[:10]]


# Example Usage
if __name__ == "__main__":
    optimizer = ContentOptimizer()

    # Text Optimization
    text_result = optimizer.optimize_text(
        "This is an example text that is quite long and might need optimization for specific platforms.", "Twitter"
    )
    print("Text Optimization:", text_result)

    # Image Optimization
    image_result = optimizer.optimize_image("example.jpg", "Instagram")
    print("Image Optimization:", image_result)

    # Video Optimization
    video_result = optimizer.optimize_video("example.mp4", "TikTok")
    print("Video Optimization:", video_result)

    # Keyword Suggestions
    keywords = optimizer.suggest_keywords("Content optimization helps improve engagement and visibility.")
    print("Suggested Keywords:", keywords)

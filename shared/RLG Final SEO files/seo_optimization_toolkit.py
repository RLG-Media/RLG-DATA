import logging
import re
import requests
from typing import List, Dict, Optional
from shared.utils import log_info, log_error, validate_url, send_alert
from shared.config import SEO_API_KEY, SOCIAL_MEDIA_PLATFORMS, ALERT_EMAILS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/seo_optimization_toolkit.log"),
    ],
)


class SEOOptimizationToolkit:
    """
    Toolkit for comprehensive SEO optimization and analysis for RLG Data and RLG Fans.
    """

    def __init__(self):
        self.api_key = SEO_API_KEY
        self.keyword_cache = {}

    def analyze_page(self, url: str) -> Dict:
        """
        Analyze a webpage for SEO performance.

        Args:
            url: The URL of the webpage to analyze.

        Returns:
            A dictionary with SEO metrics and recommendations.
        """
        if not validate_url(url):
            log_error(f"Invalid URL provided for SEO analysis: {url}")
            return {"error": "Invalid URL"}

        try:
            log_info(f"Analyzing page: {url}")
            response = requests.post(
                "https://seo-api.example.com/analyze",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"url": url},
            )
            response.raise_for_status()
            seo_metrics = response.json()
            log_info(f"SEO analysis completed for {url}.")
            return seo_metrics
        except Exception as e:
            log_error(f"Error analyzing SEO for {url}: {e}")
            return {"error": "Failed to analyze page SEO. Please try again later."}

    def generate_keyword_suggestions(self, seed_keyword: str, region: Optional[str] = None) -> List[str]:
        """
        Generate keyword suggestions based on a seed keyword.

        Args:
            seed_keyword: The seed keyword to base suggestions on.
            region: Optional region for localized keyword suggestions.

        Returns:
            A list of suggested keywords.
        """
        try:
            log_info(f"Generating keyword suggestions for: {seed_keyword}, region: {region}")
            response = requests.get(
                "https://seo-api.example.com/keywords",
                headers={"Authorization": f"Bearer {self.api_key}"},
                params={"seed": seed_keyword, "region": region},
            )
            response.raise_for_status()
            keywords = response.json().get("keywords", [])
            self.keyword_cache[seed_keyword] = keywords
            log_info(f"Generated {len(keywords)} keyword suggestions for {seed_keyword}.")
            return keywords
        except Exception as e:
            log_error(f"Error generating keywords for {seed_keyword}: {e}")
            return []

    def optimize_social_media_profiles(self) -> List[Dict]:
        """
        Optimize social media profiles for SEO performance.

        Returns:
            A list of optimization recommendations for each platform.
        """
        recommendations = []
        for platform in SOCIAL_MEDIA_PLATFORMS:
            try:
                log_info(f"Optimizing SEO for social media platform: {platform}")
                response = requests.get(
                    f"https://seo-api.example.com/social/{platform}",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                response.raise_for_status()
                platform_recommendations = response.json()
                recommendations.append({platform: platform_recommendations})
                log_info(f"SEO optimization recommendations fetched for {platform}.")
            except Exception as e:
                log_error(f"Error optimizing SEO for {platform}: {e}")
                recommendations.append({platform: {"error": str(e)}})
        return recommendations

    def monitor_ranking_changes(self, keywords: List[str]) -> Dict:
        """
        Monitor ranking changes for a list of keywords.

        Args:
            keywords: A list of keywords to monitor.

        Returns:
            A dictionary with ranking changes and trends.
        """
        try:
            log_info("Monitoring keyword ranking changes.")
            response = requests.post(
                "https://seo-api.example.com/rankings",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"keywords": keywords},
            )
            response.raise_for_status()
            ranking_data = response.json()
            log_info("Keyword ranking monitoring completed.")
            return ranking_data
        except Exception as e:
            log_error(f"Error monitoring keyword rankings: {e}")
            return {"error": "Failed to monitor rankings. Please try again later."}

    def perform_audit(self, url: str) -> Dict:
        """
        Perform a full SEO audit for a given URL.

        Args:
            url: The URL to audit.

        Returns:
            A dictionary with audit results and recommendations.
        """
        if not validate_url(url):
            log_error(f"Invalid URL provided for audit: {url}")
            return {"error": "Invalid URL"}

        try:
            log_info(f"Performing SEO audit for: {url}")
            response = requests.post(
                "https://seo-api.example.com/audit",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"url": url},
            )
            response.raise_for_status()
            audit_results = response.json()
            log_info(f"SEO audit completed for {url}.")
            return audit_results
        except Exception as e:
            log_error(f"Error performing SEO audit for {url}: {e}")
            return {"error": "Failed to perform audit. Please try again later."}

    def send_alerts_for_critical_issues(self, issues: List[Dict]) -> None:
        """
        Send alerts for critical SEO issues.

        Args:
            issues: A list of critical SEO issues.
        """
        if not issues:
            log_info("No critical SEO issues detected. No alerts sent.")
            return

        for email in ALERT_EMAILS:
            try:
                message = f"Critical SEO issues detected:\n\n{json.dumps(issues, indent=2)}"
                send_alert(email, "Critical SEO Issues Detected", message)
                log_info(f"SEO alert sent to {email}.")
            except Exception as e:
                log_error(f"Error sending SEO alert to {email}: {e}")


# Example Usage
if __name__ == "__main__":
    toolkit = SEOOptimizationToolkit()

    # Analyze a webpage
    page_analysis = toolkit.analyze_page("https://example.com")
    print(page_analysis)

    # Generate keyword suggestions
    keyword_suggestions = toolkit.generate_keyword_suggestions("AI tools", region="US")
    print(keyword_suggestions)

    # Optimize social media profiles
    social_media_optimizations = toolkit.optimize_social_media_profiles()
    print(social_media_optimizations)

    # Monitor ranking changes
    ranking_changes = toolkit.monitor_ranking_changes(["AI tools", "data analysis"])
    print(ranking_changes)

    # Perform an audit
    audit_results = toolkit.perform_audit("https://example.com")
    print(audit_results)

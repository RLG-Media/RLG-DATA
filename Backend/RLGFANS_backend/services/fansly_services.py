# fansly_service.py - Fansly Integration Service
import os
import json
import logging
import requests
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from ratelimiter import RateLimiter
from pydantic import BaseModel, ValidationError
from shared.data_models import (
    CreatorMetrics,
    ContentRecommendation,
    TrendingContent,
    GeographicDistribution,
    PlatformPerformance,
    EngagementMetrics
)
from shared.utilities import (
    validate_username,
    format_engagement_rate,
    cache_response,
    get_geographic_context,
    normalize_metrics
)
from shared.scraping import (
    BaseScraper,
    AntiBotDetectionMixin,
    RotatingProxyMixin,
    ScrapeConfig
)
from shared.exceptions import (
    ScrapingError,
    InvalidCredentialsError,
    RateLimitExceededError
)
from shared.config import CONFIG
from shared.logging import setup_logger
from shared.analytics import TrendAnalyzer, RecommendationEngine

# Configure logging
logger = setup_logger(__name__)

class FanslyMetrics(BaseModel):
    followers: int
    total_likes: int
    engagement_rate: float
    post_metrics: EngagementMetrics
    geographic_distribution: GeographicDistribution
    performance_history: PlatformPerformance
    last_updated: datetime

class FanslyService(AntiBotDetectionMixin, RotatingProxyMixin, BaseScraper):
    """
    Advanced Fansly integration service with real-time engagement analytics,
    content performance tracking, and AI-powered optimization recommendations.
    """
    API_BASE = CONFIG.get('fansly', 'api_base', fallback='https://fansly.com')
    RATE_LIMIT = CONFIG.getint('fansly', 'rate_limit', fallback=10)  # Requests per minute
    REQUEST_TIMEOUT = CONFIG.getint('fansly', 'request_timeout', fallback=25)
    
    def __init__(self, session: Optional[requests.Session] = None):
        super().__init__()
        self.session = session or self._create_session()
        self.scrape_config = ScrapeConfig(
            retries=4,
            backoff_factor=1.5,
            cache_ttl=timedelta(minutes=45)
        )
        self._configure_session()
        self._setup_proxy_rotation()
        self.recommendation_engine = RecommendationEngine()
        self.trend_analyzer = TrendAnalyzer(window_size=7)

    def _create_session(self) -> requests.Session:
        """Create resilient session with retry logic"""
        session = requests.Session()
        retry = Retry(
            total=self.scrape_config.retries,
            backoff_factor=self.scrape_config.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def _configure_session(self):
        """Configure session headers and security settings"""
        self.session.headers.update({
            'User-Agent': CONFIG.get('scraping', 'user_agent'),
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': self.API_BASE
        })
        self._apply_anti_bot_headers()

    @RateLimiter(max_calls=RATE_LIMIT, period=60)
    @cache_response('fansly_metrics')
    def get_creator_metrics(self, username: str) -> FanslyMetrics:
        """
        Retrieve comprehensive creator metrics with engagement analysis
        and geographic distribution insights.
        """
        if not validate_username(username):
            raise ValueError(f"Invalid Fansly username: {username}")

        try:
            profile_data = self._fetch_profile_data(username)
            metrics = self._parse_metrics(profile_data)
            geo_data = self._get_geographic_distribution(username)
            performance = self._get_performance_history(username)
            
            return FanslyMetrics(
                **metrics.dict(),
                geographic_distribution=geo_data,
                performance_history=performance,
                last_updated=datetime.utcnow()
            )
        except (ScrapingError, ValidationError) as e:
            logger.error(f"Metrics retrieval failed for {username}: {str(e)}")
            raise

    def _fetch_profile_data(self, username: str) -> Dict:
        """Fetch and validate profile data with bot mitigation"""
        url = f"{self.API_BASE}/@{username}"
        try:
            response = self.session.get(
                url,
                timeout=self.REQUEST_TIMEOUT,
                proxies=self.current_proxy
            )
            response.raise_for_status()
            self._detect_bot_checks(response)
            return self._parse_profile_response(response.text)
        except requests.exceptions.RequestException as e:
            raise ScrapingError(f"Profile fetch failed: {str(e)}")

    def _parse_profile_response(self, html: str) -> Dict:
        """Parse profile HTML using configurable selectors"""
        selectors = CONFIG['fansly_selectors']
        soup = BeautifulSoup(html, 'lxml')
        
        try:
            return {
                'followers': self._parse_number(soup, selectors['followers']),
                'likes': self._parse_number(soup, selectors['likes']),
                'posts': self._parse_posts(soup),
                'engagement': self._calculate_engagement(soup)
            }
        except KeyError as e:
            raise ScrapingError(f"Missing selector: {str(e)}")

    def _parse_number(self, soup: BeautifulSoup, selector: str) -> int:
        """Extract numeric value from page element"""
        element = soup.select_one(selector)
        return int(re.sub(r'\D', '', element.text.strip())) if element else 0

    def _parse_posts(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse post engagement metrics"""
        posts = []
        for post in soup.select(CONFIG['fansly_selectors']['posts']):
            posts.append({
                'likes': self._parse_number(post, CONFIG['selectors']['likes']),
                'comments': self._parse_number(post, CONFIG['selectors']['comments']),
                'timestamp': self._parse_timestamp(post)
            })
        return posts

    def _parse_timestamp(self, post: BeautifulSoup) -> datetime:
        """Convert post date text to datetime object"""
        date_str = post.select_one(CONFIG['selectors']['timestamp']).text.strip()
        return datetime.strptime(date_str, CONFIG.get('fansly', 'date_format', '%b %d, %Y'))

    def _calculate_engagement(self, soup: BeautifulSoup) -> float:
        """Calculate comprehensive engagement rate"""
        total_likes = self._parse_number(soup, CONFIG['fansly_selectors']['likes'])
        followers = self._parse_number(soup, CONFIG['fansly_selectors']['followers'])
        return (total_likes / followers) * 100 if followers > 0 else 0.0

    def _get_geographic_distribution(self, username: str) -> GeographicDistribution:
        """
        Retrieve geographic distribution data using viewer IP analysis
        """
        # Implementation would use internal analytics data
        # Placeholder for demonstration
        return GeographicDistribution(
            region='North America',
            country='US',
            city='Los Angeles',
            town='Hollywood',
            distribution={'US': 70, 'EU': 20, 'ASIA': 10}
        )

    def _get_performance_history(self, username: str) -> PlatformPerformance:
        """
        Retrieve historical performance data from internal analytics
        """
        # Placeholder implementation
        return PlatformPerformance(
            weekly_trend=[1500, 1650, 1700, 1580, 1750, 1800, 1850],
            average_engagement=18.2,
            peak_hours=[19, 20, 21]
        )

    @cache_response('fansly_trending')
    def get_trending_content(self, region: str = 'global') -> List[TrendingContent]:
        """
        Analyze trending content with regional filtering and engagement patterns
        """
        try:
            response = self.session.get(
                f"{self.API_BASE}/trending",
                params={'region': region},
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return self._parse_trending_content(response.text, region)
        except requests.exceptions.RequestException as e:
            raise ScrapingError(f"Trending content fetch failed: {str(e)}")

    def _parse_trending_content(self, html: str, region: str) -> List[TrendingContent]:
        """Parse trending content with regional context"""
        soup = BeautifulSoup(html, 'lxml')
        content_items = []
        
        for item in soup.select(CONFIG['fansly_selectors']['trending_item']):
            try:
                content_items.append(TrendingContent(
                    title=item.select_one(CONFIG['selectors']['title']).text.strip(),
                    content_type=item.select_one(CONFIG['selectors']['type']).text.strip(),
                    likes=self._parse_number(item, CONFIG['selectors']['likes']),
                    comments=self._parse_number(item, CONFIG['selectors']['comments']),
                    region=region,
                    engagement_score=self._calculate_engagement_score(item),
                    trend_velocity=self.trend_analyzer.calculate_velocity(item)
                ))
            except Exception as e:
                logger.warning(f"Skipping invalid trending item: {str(e)}")
                continue
                
        return content_items

    def generate_recommendations(self, metrics: FanslyMetrics) -> List[ContentRecommendation]:
        """
        Generate AI-powered content recommendations with engagement predictions
        and localization strategies
        """
        recommendations = self.recommendation_engine.generate(
            metrics=metrics,
            platform='fansly'
        )
        
        # Add geo-specific recommendations
        if metrics.geographic_distribution.distribution:
            primary_region = max(
                metrics.geographic_distribution.distribution,
                key=metrics.geographic_distribution.distribution.get
            )
            recommendations.append(
                ContentRecommendation(
                    category='localization',
                    action=f"regional_content_{primary_region}",
                    priority='medium',
                    expected_impact=25
                )
            )
        
        logger.info(f"Generated {len(recommendations)} recommendations")
        return recommendations

    def _detect_bot_checks(self, response: requests.Response):
        """Detect and handle bot protection mechanisms"""
        if 'access denied' in response.text.lower():
            self._rotate_user_agent()
            self._rotate_proxy()
            raise InvalidCredentialsError("Bot detection triggered")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

# Example Usage
if __name__ == "__main__":
    service = FanslyService()
    
    try:
        metrics = service.get_creator_metrics("top_creator")
        print(f"Creator Metrics: {metrics.json(indent=2)}")
        
        trending_us = service.get_trending_content(region="United States")
        print(f"US Trending Content: {trending_us[:2]}")
        
        recommendations = service.generate_recommendations(metrics)
        print(f"Optimization Recommendations: {recommendations}")
        
    except ScrapingError as e:
        logger.error(f"Service error: {str(e)}")
        
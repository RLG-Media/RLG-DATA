# stripchat_service.py - Stripchat Integration Service
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
    GrowthRecommendation,
    TrendingContent,
    GeographicDistribution,
    PlatformPerformance
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
from shared.analytics import TrendAnalyzer

# Configure logging
logger = setup_logger(__name__)

class StripchatMetrics(BaseModel):
    followers: int
    total_views: int
    engagement_rate: float
    online_status: bool
    geographic_distribution: GeographicDistribution
    performance_history: PlatformPerformance
    last_updated: datetime

class StripchatService(AntiBotDetectionMixin, RotatingProxyMixin, BaseScraper):
    """
    Advanced Stripchat integration service with real-time analytics,
    regional trend analysis, and AI-powered growth recommendations.
    """
    API_BASE = CONFIG.get('stripchat', 'api_base', fallback='https://stripchat.com')
    RATE_LIMIT = CONFIG.getint('stripchat', 'rate_limit', fallback=10)  # Requests per minute
    REQUEST_TIMEOUT = CONFIG.getint('stripchat', 'request_timeout', fallback=25)
    
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
    @cache_response('stripchat_metrics')
    def get_creator_metrics(self, username: str) -> StripchatMetrics:
        """
        Retrieve comprehensive creator metrics with historical comparison
        and geographic insights.
        """
        if not validate_username(username):
            raise ValueError(f"Invalid Stripchat username: {username}")

        try:
            profile_data = self._fetch_profile_data(username)
            metrics = self._parse_metrics(profile_data)
            geo_data = self._get_geographic_distribution(username)
            performance = self._get_performance_history(username)
            
            return StripchatMetrics(
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
        url = f"{self.API_BASE}/{username}"
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
        selectors = CONFIG['stripchat_selectors']
        soup = BeautifulSoup(html, 'lxml')
        
        try:
            return {
                'followers': self._parse_number(soup, selectors['followers']),
                'views': self._parse_number(soup, selectors['views']),
                'online': self._parse_online_status(soup, selectors['online']),
                'engagement': self._parse_engagement(soup, selectors['engagement'])
            }
        except KeyError as e:
            raise ScrapingError(f"Missing selector: {str(e)}")

    def _parse_number(self, soup: BeautifulSoup, selector: str) -> int:
        """Extract numeric value from page element"""
        element = soup.select_one(selector)
        return int(re.sub(r'\D', '', element.text.strip())) if element else 0

    def _parse_online_status(self, soup: BeautifulSoup, selector: str) -> bool:
        """Determine online status from presence of indicator element"""
        return bool(soup.select_one(selector))

    def _parse_engagement(self, soup: BeautifulSoup, selector: str) -> float:
        """Calculate engagement rate from parsed metrics"""
        likes = self._parse_number(soup, CONFIG['stripchat_selectors']['likes'])
        views = self._parse_number(soup, CONFIG['stripchat_selectors']['views'])
        return (likes / views) * 100 if views > 0 else 0.0

    def _get_geographic_distribution(self, username: str) -> GeographicDistribution:
        """
        Retrieve geographic distribution data using viewer IP analysis
        and regional engagement patterns
        """
        # Implementation would use internal analytics data
        # Placeholder for demonstration
        return GeographicDistribution(
            region='Europe',
            country='DE',
            city='Berlin',
            town='Mitte',
            distribution={'EU': 75, 'NA': 15, 'ASIA': 10}
        )

    def _get_performance_history(self, username: str) -> PlatformPerformance:
        """
        Retrieve historical performance data from internal analytics
        """
        # Placeholder implementation
        return PlatformPerformance(
            weekly_trend=[1200, 1350, 1420, 1300, 1450, 1600, 1550],
            average_engagement=14.5,
            peak_hours=[19, 20, 21]
        )

    @cache_response('stripchat_trending')
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
        
        for item in soup.select(CONFIG['stripchat_selectors']['trending_item']):
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

    def generate_recommendations(self, metrics: StripchatMetrics) -> List[GrowthRecommendation]:
        """
        Generate data-driven growth recommendations using performance metrics
        and AI trend analysis
        """
        recommendations = []
        
        # Follower growth strategies
        if metrics.followers < 5000:
            recommendations.append(
                GrowthRecommendation(
                    category='growth',
                    action='collaboration_campaigns',
                    priority='high',
                    expected_impact=15
                )
            )
        
        # Engagement optimization
        if metrics.engagement_rate < 12.0:
            recommendations.append(
                GrowthRecommendation(
                    category='engagement',
                    action='interactive_streams',
                    priority='medium',
                    expected_impact=20
                )
            )
        
        # Geographic optimization
        if metrics.geographic_distribution.distribution:
            primary_region = max(
                metrics.geographic_distribution.distribution,
                key=metrics.geographic_distribution.distribution.get
            )
            recommendations.append(
                GrowthRecommendation(
                    category='localization',
                    action=f"regional_content_{primary_region}",
                    priority='low',
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
    service = StripchatService()
    
    try:
        metrics = service.get_creator_metrics("top_performer")
        print(f"Creator Metrics: {metrics.json(indent=2)}")
        
        trending_eu = service.get_trending_content(region="Europe")
        print(f"EU Trending Content: {trending_eu[:2]}")
        
        recommendations = service.generate_recommendations(metrics)
        print(f"Growth Recommendations: {recommendations}")
        
    except ScrapingError as e:
        logger.error(f"Service error: {str(e)}")
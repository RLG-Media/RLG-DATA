# onlyfans_service.py - OnlyFans Integration Service
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
    GeographicDistribution
)
from shared.utilities import (
    validate_username,
    format_engagement_rate,
    cache_response,
    get_region_from_ip
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

# Configure logging
logger = setup_logger(__name__)

class OnlyFansMetrics(BaseModel):
    subscriber_count: int
    post_count: int
    view_count: int
    engagement_rate: float
    geographic_distribution: GeographicDistribution
    last_updated: datetime

class OnlyFansService(AntiBotDetectionMixin, RotatingProxyMixin, BaseScraper):
    """
    Comprehensive OnlyFans integration service with advanced scraping capabilities,
    regional analytics, and monetization recommendations.
    """
    API_BASE = CONFIG.get('onlyfans', 'api_base', fallback='https://onlyfans.com')
    RATE_LIMIT = CONFIG.getint('onlyfans', 'rate_limit', fallback=5)  # Requests per minute
    REQUEST_TIMEOUT = CONFIG.getint('onlyfans', 'request_timeout', fallback=30)
    
    def __init__(self, session: Optional[requests.Session] = None):
        super().__init__()
        self.session = session or self._create_session()
        self.scrape_config = ScrapeConfig(
            retries=3,
            backoff_factor=1,
            cache_ttl=timedelta(minutes=30)
        )
        self._configure_session()
        self._setup_proxy_rotation()

    def _create_session(self) -> requests.Session:
        """Create a resilient requests session with retry logic"""
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
        """Configure session headers and bot detection avoidance"""
        self.session.headers.update({
            'User-Agent': CONFIG.get('scraping', 'user_agent'),
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': self.API_BASE
        })
        self._apply_anti_bot_headers()

    @RateLimiter(max_calls=RATE_LIMIT, period=60)
    @cache_response('onlyfans_metrics')
    def get_creator_metrics(self, username: str) -> OnlyFansMetrics:
        """
        Retrieve comprehensive creator metrics with regional breakdown and
        historical data comparison.
        """
        if not validate_username(username):
            raise ValueError(f"Invalid OnlyFans username: {username}")

        try:
            profile_data = self._fetch_profile_data(username)
            metrics = self._parse_metrics(profile_data)
            geo_data = self._get_geographic_distribution(username)
            
            return OnlyFansMetrics(
                **metrics.dict(),
                geographic_distribution=geo_data,
                last_updated=datetime.utcnow()
            )
        except (ScrapingError, ValidationError) as e:
            logger.error(f"Failed to get metrics for {username}: {str(e)}")
            raise

    def _fetch_profile_data(self, username: str) -> Dict:
        """Fetch and validate profile data with bot detection handling"""
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
        selectors = CONFIG['onlyfans_selectors']
        soup = BeautifulSoup(html, 'lxml')
        
        try:
            return {
                'subscribers': self._parse_number(soup, selectors['subscribers']),
                'posts': self._parse_number(soup, selectors['posts']),
                'views': self._parse_number(soup, selectors['views']),
                'engagement': self._parse_engagement(soup, selectors['engagement'])
            }
        except KeyError as e:
            raise ScrapingError(f"Missing selector: {str(e)}")

    def _parse_number(self, soup: BeautifulSoup, selector: str) -> int:
        """Extract numeric value from page element"""
        element = soup.select_one(selector)
        if not element:
            return 0
        return int(re.sub(r'\D', '', element.text.strip()))

    def _parse_engagement(self, soup: BeautifulSoup, selector: str) -> float:
        """Calculate engagement rate from parsed metrics"""
        engagement_text = soup.select_one(selector).text.strip()
        return float(re.search(r'\d+\.\d+', engagement_text).group())

    def _get_geographic_distribution(self, username: str) -> GeographicDistribution:
        """
        Retrieve geographic distribution data using IP analysis and
        regional engagement metrics
        """
        # Implementation would use internal analytics data
        # Placeholder for demonstration
        return GeographicDistribution(
            region='North America',
            country='US',
            city='Los Angeles',
            town='Hollywood',
            distribution={'US': 65, 'EU': 25, 'ASIA': 10}
        )

    @cache_response('onlyfans_trending')
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
        
        for item in soup.select(CONFIG['onlyfans_selectors']['trending_item']):
            try:
                content_items.append(TrendingContent(
                    title=item.select_one(CONFIG['onlyfans_selectors']['title']).text.strip(),
                    content_type=item.select_one(CONFIG['selectors']['type']).text.strip(),
                    likes=self._parse_number(item, CONFIG['selectors']['likes']),
                    views=self._parse_number(item, CONFIG['selectors']['views']),
                    region=region,
                    engagement_score=self._calculate_engagement_score(item)
                ))
            except Exception as e:
                logger.warning(f"Failed to parse trending item: {str(e)}")
                continue
                
        return content_items

    def generate_recommendations(self, metrics: CreatorMetrics) -> List[ContentRecommendation]:
        """
        Generate AI-powered content recommendations based on performance metrics
        and regional trends
        """
        recommendations = []
        
        # Subscriber growth recommendations
        if metrics.subscriber_count < 1000:
            recommendations.append(
                ContentRecommendation(
                    category='growth',
                    action='promote_exclusive_offers',
                    priority='high'
                )
            )
        
        # Engagement optimization
        if metrics.engagement_rate < 8.0:
            recommendations.append(
                ContentRecommendation(
                    category='engagement',
                    action='schedule_live_sessions',
                    priority='medium'
                )
            )
        
        # Regional content adaptation
        if metrics.geographic_distribution:
            primary_region = max(
                metrics.geographic_distribution.distribution,
                key=metrics.geographic_distribution.distribution.get
            )
            recommendations.append(
                ContentRecommendation(
                    category='localization',
                    action=f"create_{primary_region}_specific_content",
                    priority='low'
                )
            )
        
        logger.info(f"Generated {len(recommendations)} recommendations")
        return recommendations

    def _calculate_engagement_score(self, item: BeautifulSoup) -> float:
        """Calculate normalized engagement score for content items"""
        likes = self._parse_number(item, CONFIG['selectors']['likes'])
        views = self._parse_number(item, CONFIG['selectors']['views'])
        return (likes / views) * 100 if views > 0 else 0.0

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
    service = OnlyFansService()
    
    try:
        metrics = service.get_creator_metrics("example_creator")
        print(f"Creator Metrics: {metrics}")
        
        trending = service.get_trending_content(region="North America")
        print(f"Trending Content: {trending[:2]}")
        
        recommendations = service.generate_recommendations(metrics)
        print(f"Recommendations: {recommendations}")
        
    except ScrapingError as e:
        logger.error(f"Service error: {str(e)}")
# api_limits_and_throttling.py
import os
import json
import logging
import time
import redis
from typing import Dict, Optional, Tuple
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from geolocation_service import (
    get_user_location,
    is_user_in_special_region,
    validate_location_lock
)
from pricing import REGIONAL_PRICING, SADC_COUNTRIES
from shared.data_models import UserSession, APIMetrics
from shared.utilities import (
    get_real_ip,
    calculate_cost_per_call,
    format_currency
)
from shared.config import (
    REDIS_CONFIG,
    RATE_LIMIT_CONFIG,
    SECURITY_CONFIG,
    COST_TRACKING_CONFIG
)

# Configure logging
logger = logging.getLogger("APILimiter")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)

# Redis connection pool
redis_pool = redis.ConnectionPool(**REDIS_CONFIG)

class APILimitManager:
    def __init__(self):
        self.redis = redis.Redis(connection_pool=redis_pool)
        self.circuit_breakers = {}
        self._init_rate_limits()
        
    def _init_rate_limits(self):
        """Load dynamic rate limits from config"""
        self.rate_limits = {
            tier: {
                'global': RATE_LIMIT_CONFIG['tiers'][tier],
                'regional': RATE_LIMIT_CONFIG['regional_multipliers']
            }
            for tier in ['Creator', 'Pro', 'Enterprise', 'RLG Media Pack']
        }
        
        # Hardcode special region limits
        self.rate_limits['Special'] = RATE_LIMIT_CONFIG['special_region']

    async def enforce_limits(self, request: Request, user: UserSession) -> Tuple[bool, Optional[Dict]]:
        """
        Enforce API limits with regional awareness and cost tracking
        Returns: (allowed, headers)
        """
        # 1. Compliance and Geolocation Check
        if not await self._validate_location_lock(user):
            return False, self._blocked_response("Location validation failed")
            
        # 2. Circuit Breaker Check
        if self._check_circuit_breaker(user):
            return False, self._blocked_response("API access temporarily suspended")

        # 3. Rate Limit Calculation
        endpoint = request.url.path
        region = await self._determine_rate_limit_region(user)
        tier = user.subscription_tier
        
        # Get limits based on region and tier
        limit_config = self._get_limit_config(tier, region, endpoint)
        cost = calculate_cost_per_call(endpoint, user.location_data)
        
        # 4. Cost Tracking
        if not self._track_api_cost(user, cost):
            return False, self._blocked_response("API budget exceeded")

        # 5. Rate Limit Enforcement
        key = f"rl:{user.id}:{endpoint}"
        current = self.redis.incr(key)
        
        if current > limit_config['requests']:
            self._trigger_circuit_breaker(user)
            return False, self._rate_limit_response(limit_config)
            
        if current == 1:
            self.redis.expire(key, limit_config['window'])
            
        return True, self._build_headers(current, limit_config, cost)

    async def _validate_location_lock(self, user: UserSession) -> bool:
        """Enforce special region restrictions"""
        if user.location_data.get('country') == 'IL':
            if not validate_location_lock(user.id, 'IL'):
                logger.warning(f"Israel location tamper attempt: {user.id}")
                return False
                
            # Re-validate location periodically
            if time.time() - user.location_validated > 86400:
                fresh_location = get_user_location(user.last_ip)
                if fresh_location.get('country') != 'IL':
                    logger.critical(f"Israel user location changed: {user.id}")
                    await self._handle_location_violation(user)
                    return False
        return True

    def _get_limit_config(self, tier: str, region: str, endpoint: str) -> Dict:
        """Get rate limits considering regional multipliers"""
        base = self.rate_limits[tier]['global']
        multiplier = self.rate_limits[tier]['regional'].get(region, 1.0)
        
        # Endpoint-specific adjustments
        if endpoint in RATE_LIMIT_CONFIG['expensive_endpoints']:
            base['requests'] = max(1, base['requests'] // 2)
            
        return {
            'requests': int(base['requests'] * multiplier),
            'window': base['window'],
            'region': region,
            'tier': tier
        }

    def _track_api_cost(self, user: UserSession, cost: float) -> bool:
        """Track and enforce API usage costs"""
        monthly_key = f"cost:{user.id}:{time.strftime('%Y-%m')}"
        daily_key = f"cost:{user.id}:{time.strftime('%Y-%m-%d')}"
        
        with self.redis.pipeline() as pipe:
            pipe.incrfloat(monthly_key, cost)
            pipe.incrfloat(daily_key, cost)
            pipe.expire(monthly_key, 2678400)  # 31 days
            pipe.expire(daily_key, 86400)
            monthly_cost, daily_cost, _ = pipe.execute()
            
        if monthly_cost > user.monthly_budget * COST_TRACKING_CONFIG['alert_threshold']:
            self._trigger_cost_alert(user, monthly_cost)
            
        return monthly_cost <= user.monthly_budget

    def _check_circuit_breaker(self, user: UserSession) -> bool:
        """Check if user is in circuit breaker state"""
        cb_key = f"cb:{user.id}"
        if self.redis.exists(cb_key):
            logger.warning(f"Circuit breaker active for {user.id}")
            return True
            
        # Check error rate
        error_rate = self.redis.get(f"err:{user.id}") or 0
        if error_rate > SECURITY_CONFIG['max_error_rate']:
            self._trigger_circuit_breaker(user)
            return True
            
        return False

    def _trigger_circuit_breaker(self, user: UserSession):
        """Activate circuit breaker for problematic users"""
        cb_key = f"cb:{user.id}"
        self.redis.setex(cb_key, SECURITY_CONFIG['circuit_breaker_ttl'], 1)
        logger.warning(f"Circuit breaker triggered for {user.id}")

    def _build_headers(self, current: int, limits: Dict, cost: float) -> Dict:
        """Build rate limit headers"""
        return {
            "X-RateLimit-Limit": str(limits['requests']),
            "X-RateLimit-Remaining": str(limits['requests'] - current),
            "X-RateLimit-Reset": str(limits['window']),
            "X-RateLimit-Region": limits['region'],
            "X-RateLimit-Tier": limits['tier'],
            "X-API-Cost": format_currency(cost, limits['region'])
        }

    def _rate_limit_response(self, limits: Dict) -> JSONResponse:
        """Generate rate limit exceeded response"""
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "detail": {
                    "tier": limits['tier'],
                    "region": limits['region'],
                    "limit": limits['requests'],
                    "window": f"{limits['window']} seconds",
                    "upgrade_url": "/subscription/upgrade",
                    "regional_pricing": self._get_pricing_hint(limits['region'])
                }
            },
            headers={
                "Retry-After": str(limits['window'])
            }
        )

    def _blocked_response(self, reason: str) -> JSONResponse:
        """Generate blocked response"""
        return JSONResponse(
            status_code=403,
            content={
                "error": "Access blocked",
                "detail": reason,
                "support_contact": SECURITY_CONFIG['abuse_contact']
            }
        )

    def _get_pricing_hint(self, region: str) -> Optional[Dict]:
        """Provide regional pricing hints for upgrades"""
        if region == "Special":
            return None  # No upgrade path for special region
            
        return {
            "current_region": region,
            "recommended_tiers": REGIONAL_PRICING.get(region, REGIONAL_PRICING["DEFAULT"])
        }

    async def _handle_location_violation(self, user: UserSession):
        """Handle special region location violations"""
        # Log incident
        logger.critical(f"Special region violation detected: {user.id}")
        
        # Notify security team
        await self._send_alert(
            "Location Tampering Alert",
            f"User {user.id} attempted to bypass regional restrictions"
        )
        
        # Apply sanctions
        self._trigger_circuit_breaker(user)
        await self._disable_account(user.id)

    async def _disable_account(self, user_id: str):
        """Disable compromised account"""
        # Implementation depends on user storage system
        pass

    async def _send_alert(self, subject: str, message: str):
        """Send security alert"""
        # Implementation depends on alerting system
        pass

# Real-time Monitoring Integration
class APIMonitor:
    def __init__(self):
        self.redis = redis.Redis(connection_pool=redis_pool)
        
    def get_global_metrics(self) -> APIMetrics:
        """Get real-time global API metrics"""
        return APIMetrics(
            total_requests=int(self.redis.get("global:requests") or 0),
            blocked_requests=int(self.redis.get("global:blocked") or 0),
            error_rate=float(self.redis.get("global:error_rate") or 0),
            top_endpoints=self.redis.zrevrange("global:endpoints", 0, 5, withscores=True)
        )

    def get_user_metrics(self, user_id: str) -> APIMetrics:
        """Get detailed metrics for specific user"""
        return APIMetrics(
            requests=int(self.redis.get(f"user:{user_id}:requests") or 0),
            costs=float(self.redis.get(f"user:{user_id}:costs") or 0),
            error_rate=float(self.redis.get(f"user:{user_id}:error_rate") or 0),
            circuit_breakers=int(self.redis.get(f"user:{user_id}:cb_triggers") or 0)
        )

# Middleware Integration
async def api_limit_middleware(request: Request, call_next):
    """FastAPI middleware for API limiting"""
    user = get_current_user(request)  # Implement your auth system
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
        
    limiter = APILimitManager()
    allowed, headers = await limiter.enforce_limits(request, user)
    
    if not allowed:
        return headers  # Returns the prepared error response
        
    response = await call_next(request)
    
    # Track successful request
    if headers:
        for header, value in headers.items():
            response.headers[header] = value
            
    return response
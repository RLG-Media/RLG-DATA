"""
RLG API Limits and Throttling System
====================================

A sophisticated, region-aware API management system that:
- Enforces tiered rate limits with regional adjustments
- Implements strict location locking for special regions (Israel)
- Provides real-time cost tracking and budget enforcement
- Detects and prevents abuse patterns with circuit breakers
- Delivers personalized user experiences with localized messaging
"""

import time
import logging
import json
import redis
from functools import wraps
from typing import Dict, Optional, Tuple, Callable
from flask import request, jsonify, abort, Response
from dataclasses import dataclass
from geolocation_service import (
    get_user_location,
    validate_location_lock,
    is_special_region
)
from pricing import (
    REGIONAL_PRICING,
    get_user_pricing,
    SADC_COUNTRIES
)
from shared.config import (
    REDIS_CONFIG,
    API_THROTTLE_CONFIG,
    SECURITY_CONFIG,
    COST_TRACKING_CONFIG
)
from shared.utilities import (
    get_real_ip,
    calculate_cost_per_call,
    format_currency,
    send_security_alert
)
from shared.exceptions import (
    LocationTamperingError,
    BudgetExceededError,
    RateLimitExceededError
)

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("api_limits.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("RLGAPILimiter")

# Redis connection pool
redis_pool = redis.ConnectionPool(**REDIS_CONFIG)

@dataclass
class UserContext:
    """Container for all user-specific context needed for rate limiting"""
    user_id: str
    ip_address: str
    tier: str
    location_data: Dict
    monthly_budget: float
    current_spend: float = 0.0

class APILimitManager:
    """
    Comprehensive API management system for RLG Data and RLG Fans that:
    - Enforces regional pricing and access controls
    - Prevents location tampering (especially for Israel)
    - Tracks API costs against user budgets
    - Implements circuit breakers for abusive patterns
    """
    
    def __init__(self):
        self.redis = redis.Redis(connection_pool=redis_pool)
        self._load_configurations()
        self._init_circuit_breakers()
        
    def _load_configurations(self):
        """Load dynamic configurations from central config"""
        self.tier_limits = API_THROTTLE_CONFIG["tier_limits"]
        self.region_multipliers = API_THROTTLE_CONFIG["region_multipliers"]
        self.special_region_limits = API_THROTTLE_CONFIG["special_region_limits"]
        self.expensive_endpoints = API_THROTTLE_CONFIG["expensive_endpoints"]
        
    def _init_circuit_breakers(self):
        """Initialize circuit breaker thresholds"""
        self.circuit_breaker_config = {
            "error_threshold": SECURITY_CONFIG["max_error_rate"],
            "window_seconds": SECURITY_CONFIG["circuit_breaker_window"],
            "cooldown_period": SECURITY_CONFIG["circuit_breaker_ttl"]
        }

    def enforce_limits(self, endpoint: str) -> Callable:
        """
        Decorator factory for endpoint-specific rate limiting
        with regional awareness and cost tracking
        """
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                try:
                    # 1. Extract and validate user context
                    user = self._get_user_context()
                    
                    # 2. Special region enforcement
                    if is_special_region(user.location_data):
                        if not validate_location_lock(user.user_id, 'IL'):
                            raise LocationTamperingError("Invalid location change detected")
                    
                    # 3. Calculate dynamic rate limits
                    limit_config = self._calculate_limits(user, endpoint)
                    
                    # 4. Check circuit breakers
                    if self._check_circuit_breaker(user):
                        raise RateLimitExceededError("Service temporarily suspended")
                    
                    # 5. Track API costs
                    cost = calculate_cost_per_call(endpoint, user.location_data)
                    if not self._track_api_cost(user, cost):
                        raise BudgetExceededError("API budget exceeded")
                    
                    # 6. Apply rate limiting
                    if not self._check_rate_limit(user, limit_config):
                        raise RateLimitExceededError("Rate limit exceeded")
                    
                    # Call the actual endpoint
                    response = f(*args, **kwargs)
                    
                    # Add rate limit headers to response
                    self._add_rate_limit_headers(response, user, limit_config)
                    
                    return response
                
                except LocationTamperingError as e:
                    self._handle_location_violation(user)
                    return self._error_response(403, str(e))
                except BudgetExceededError as e:
                    return self._error_response(429, str(e), {"upgrade_url": "/subscription"})
                except RateLimitExceededError as e:
                    return self._error_response(429, str(e), {"retry_after": limit_config['window']})
                
            return wrapper
        return decorator

    def _get_user_context(self) -> UserContext:
        """Extract and validate all user context from request"""
        user_id = request.headers.get("X-User-ID")
        if not user_id:
            abort(401, "Authentication required")
            
        ip_address = get_real_ip(request)
        location_data = get_user_location(ip_address)
        
        return UserContext(
            user_id=user_id,
            ip_address=ip_address,
            tier=self.redis.get(f"user:{user_id}:tier") or "free",
            location_data=location_data,
            monthly_budget=float(self.redis.get(f"user:{user_id}:budget") or 0.0
        )

    def _calculate_limits(self, user: UserContext, endpoint: str) -> Dict:
        """Calculate dynamic limits considering region, tier and endpoint"""
        base_limit = self.tier_limits[user.tier]
        
        # Apply regional adjustments
        region = user.location_data.get('country', 'GLOBAL')
        if is_special_region(user.location_data):
            return self.special_region_limits
        elif region in self.region_multipliers:
            base_limit['requests'] = int(base_limit['requests'] * self.region_multipliers[region])
        
        # Reduce limits for expensive endpoints
        if endpoint in self.expensive_endpoints:
            base_limit['requests'] = max(1, base_limit['requests'] // 2)
            
        return base_limit

    def _track_api_cost(self, user: UserContext, cost: float) -> bool:
        """Track and enforce API usage costs"""
        monthly_key = f"cost:{user.user_id}:{time.strftime('%Y-%m')}"
        daily_key = f"cost:{user.user_id}:{time.strftime('%Y-%m-%d')}"
        
        with self.redis.pipeline() as pipe:
            pipe.incrfloat(monthly_key, cost)
            pipe.incrfloat(daily_key, cost)
            pipe.expire(monthly_key, 2678400)  # 31 days
            pipe.expire(daily_key, 86400)
            monthly_cost, daily_cost, _ = pipe.execute()
            
        # Check budget limits
        if monthly_cost > user.monthly_budget:
            return False
            
        # Trigger alerts at thresholds
        if monthly_cost > user.monthly_budget * 0.8:
            self._trigger_budget_alert(user, monthly_cost)
            
        return True

    def _check_circuit_breaker(self, user: UserContext) -> bool:
        """Check if user should be blocked by circuit breaker"""
        cb_key = f"cb:{user.user_id}"
        if self.redis.exists(cb_key):
            return True
            
        # Check error rate
        error_rate = float(self.redis.get(f"err:{user.user_id}") or 0)
        if error_rate > self.circuit_breaker_config["error_threshold"]:
            self._trigger_circuit_breaker(user)
            return True
            
        return False

    def _trigger_circuit_breaker(self, user: UserContext):
        """Activate circuit breaker for problematic users"""
        cb_key = f"cb:{user.user_id}"
        self.redis.setex(
            cb_key,
            self.circuit_breaker_config["cooldown_period"],
            int(time.time())
        )
        logger.warning(f"Circuit breaker triggered for user {user.user_id}")

    def _check_rate_limit(self, user: UserContext, limits: Dict) -> bool:
        """Enforce rate limits with Redis counters"""
        key = f"rl:{user.user_id}:{request.path}"
        current = self.redis.incr(key)
        
        if current == 1:
            self.redis.expire(key, limits['window'])
            
        return current <= limits['requests']

    def _add_rate_limit_headers(self, response: Response, user: UserContext, limits: Dict):
        """Add rate limit headers to response"""
        remaining = limits['requests'] - int(self.redis.get(f"rl:{user.user_id}:{request.path}") or 0)
        response.headers.extend({
            "X-RateLimit-Limit": str(limits['requests']),
            "X-RateLimit-Remaining": str(max(0, remaining)),
            "X-RateLimit-Reset": str(limits['window']),
            "X-RateLimit-Region": user.location_data.get('country', 'GLOBAL'),
            "X-RateLimit-Tier": user.tier,
            "X-API-Cost": format_currency(
                calculate_cost_per_call(request.path, user.location_data),
                user.location_data.get('country')
            )
        })

    def _handle_location_violation(self, user: UserContext):
        """Handle special region location violations"""
        logger.critical(f"Location tampering detected for user {user.user_id}")
        send_security_alert(
            "Location Tampering Alert",
            f"User {user.user_id} attempted to bypass regional restrictions"
        )
        self._trigger_circuit_breaker(user)
        self._disable_account(user.user_id)

    def _disable_account(self, user_id: str):
        """Disable compromised account"""
        self.redis.setex(f"disabled:{user_id}", 86400, 1)  # 24-hour disable
        logger.info(f"Temporarily disabled account {user_id}")

    def _trigger_budget_alert(self, user: UserContext, current_spend: float):
        """Notify user about budget thresholds"""
        logger.info(f"User {user.user_id} reached {current_spend/user.monthly_budget:.0%} of budget")
        # Would integrate with notification system in production

    def _error_response(self, code: int, message: str, details: Optional[Dict] = None) -> Response:
        """Generate standardized error responses"""
        response = {
            "error": message,
            "documentation": "https://docs.rlgdata.com/api/limits",
            "support_contact": SECURITY_CONFIG["support_contact"]
        }
        if details:
            response.update(details)
            
        return jsonify(response), code

# Initialize the rate limiter
api_limiter = APILimitManager()

# Example usage in Flask routes
from flask import Flask
app = Flask(__name__)

@app.route("/api/v1/content", methods=["GET"])
@api_limiter.enforce_limits("content_api")
def get_content():
    """Example protected endpoint with rate limiting"""
    return jsonify({"data": "protected content"})

@app.route("/api/v1/analytics", methods=["GET"])
@api_limiter.enforce_limits("analytics_api")
def get_analytics():
    """More expensive endpoint with stricter limits"""
    return jsonify({"data": "analytics data"})

if __name__ == "__main__":
    app.run()
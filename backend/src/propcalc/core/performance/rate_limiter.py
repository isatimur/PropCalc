"""
Rate limiting implementation
"""

import logging
import time

logger = logging.getLogger(__name__)

_rate_limiter = None

def init_rate_limiter(redis_client):
    """Initialize rate limiter"""
    global _rate_limiter
    _rate_limiter = RateLimiter(redis_client)
    logger.info("Rate limiter initialized")

def get_rate_limiter():
    """Get rate limiter instance"""
    return _rate_limiter

class RateLimiter:
    """Rate limiting implementation"""

    def __init__(self, redis_client):
        self.redis = redis_client
        self.default_limit = 100  # requests per minute
        self.default_window = 60  # seconds

    def get_client_identifier(self, request) -> str:
        """Get client identifier from request (IP address or user ID)"""
        # For now, just use IP address to avoid authentication issues
        try:
            client_ip = request.client.host if request.client else "unknown"
            return f"ip_{client_ip}"
        except (AttributeError, TypeError):
            return "ip_unknown"

    def check_rate_limit(self, endpoint: str, client_id: str, limit: int = None, window: int = None) -> tuple[bool, dict]:
        """Check if request is allowed and return rate limit info"""
        if not self.redis:
            return True, {"limit": limit or self.default_limit, "remaining": float('inf'), "reset_time": 0}
        
        limit = limit or self.default_limit
        window = window or self.default_window
        
        key = f"rate_limit:{endpoint}:{client_id}"
        current = int(time.time())
        window_start = current - window
        
        # Count requests in window
        count = self.redis.zcount(key, window_start, current)
        
        # Remove expired entries
        self.redis.zremrangebyscore(key, 0, window_start - 1)
        
        if count < limit:
            # Add request to window
            self.redis.zadd(key, {str(current): current})
            self.redis.expire(key, window)
            
            return True, {
                "limit": limit,
                "remaining": limit - count - 1,
                "reset_time": current + window,
                "window": window
            }
        
        return False, {
            "limit": limit,
            "remaining": 0,
            "reset_time": current + window,
            "window": window,
            "retry_after": window
        }

    def get_rate_limit_stats(self, endpoint: str, client_id: str) -> dict:
        """Get rate limit statistics for an endpoint and client"""
        if not self.redis:
            return {"limit": self.default_limit, "remaining": float('inf'), "reset_time": 0}
        
        key = f"rate_limit:{endpoint}:{client_id}"
        current = int(time.time())
        window_start = current - self.default_window
        
        # Count requests in window
        count = self.redis.zcount(key, window_start, current)
        
        return {
            "limit": self.default_limit,
            "remaining": max(0, self.default_limit - count),
            "reset_time": current + self.default_window,
            "window": self.default_window,
            "current_usage": count
        }

    def is_allowed(self, key: str, limit: int = None, window: int = None) -> bool:
        """Check if request is allowed (legacy method)"""
        if not self.redis:
            return True  # Allow if no Redis

        limit = limit or self.default_limit
        window = window or self.default_window

        current = int(time.time())
        window_start = current - window

        # Count requests in window
        count = self.redis.zcount(key, window_start, current)

        if count < limit:
            # Add request to window
            self.redis.zadd(key, {str(current): current})
            self.redis.expire(key, window)
            return True

        return False

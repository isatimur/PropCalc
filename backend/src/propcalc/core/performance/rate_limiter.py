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

    def is_allowed(self, key: str, limit: int = None, window: int = None) -> bool:
        """Check if request is allowed"""
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

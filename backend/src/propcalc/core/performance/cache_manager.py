"""
Cache management implementation
"""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

_cache_manager = None

def init_cache_manager(redis_client):
    """Initialize cache manager"""
    global _cache_manager
    _cache_manager = CacheManager(redis_client)
    logger.info("Cache manager initialized")

def get_cache_manager():
    """Get cache manager instance"""
    return _cache_manager

class CacheManager:
    """Cache management implementation"""

    def __init__(self, redis_client):
        self.redis = redis_client

    def get(self, key: str) -> dict[str, Any] | None:
        """Get cached data"""
        if not self.redis:
            return None

        try:
            data = self.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Failed to get cache key {key}: {e}")
            return None

    def set(self, key: str, data: dict[str, Any], ttl: int = 3600):
        """Set cached data"""
        if not self.redis:
            return

        try:
            self.redis.setex(key, ttl, json.dumps(data))
        except Exception as e:
            logger.error(f"Failed to set cache key {key}: {e}")

    def delete(self, key: str):
        """Delete cached data"""
        if not self.redis:
            return

        try:
            self.redis.delete(key)
        except Exception as e:
            logger.error(f"Failed to delete cache key {key}: {e}")

    def clear(self):
        """Clear all cache"""
        if not self.redis:
            return

        try:
            self.redis.flushdb()
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")

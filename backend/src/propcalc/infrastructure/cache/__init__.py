"""
Cache infrastructure module
"""

from .redis_cache import close_redis, get_cache_stats, init_redis, redis_client

__all__ = [
    'init_redis',
    'close_redis',
    'get_cache_stats',
    'redis_client'
]

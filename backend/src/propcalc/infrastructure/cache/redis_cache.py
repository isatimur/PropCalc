"""
Redis cache implementation
"""

import json
import logging
import os
from typing import Any

import redis

logger = logging.getLogger(__name__)

# Global Redis client
redis_client = None

def init_redis():
    """Initialize Redis connection"""
    global redis_client
    try:
        redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            decode_responses=True
        )
        # Test connection
        redis_client.ping()
        logger.info("Redis connection initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {e}")
        raise

def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        redis_client.close()
        logger.info("Redis connection closed")

def get_cache_stats() -> dict[str, Any]:
    """Get Redis cache statistics"""
    if not redis_client:
        return {"error": "Redis not initialized"}

    try:
        info = redis_client.info()
        return {
            "connected_clients": info.get('connected_clients', 0),
            "used_memory_human": info.get('used_memory_human', '0B'),
            "keyspace_hits": info.get('keyspace_hits', 0),
            "keyspace_misses": info.get('keyspace_misses', 0),
            "hit_rate": calculate_hit_rate(info)
        }
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        return {"error": str(e)}

def calculate_hit_rate(info: dict[str, Any]) -> float:
    """Calculate cache hit rate"""
    hits = info.get('keyspace_hits', 0)
    misses = info.get('keyspace_misses', 0)
    total = hits + misses
    return (hits / total * 100) if total > 0 else 0

def cache_market_overview(data: dict[str, Any], ttl: int = 3600):
    """Cache market overview data"""
    if redis_client:
        try:
            redis_client.setex('market_overview', ttl, json.dumps(data))
        except Exception as e:
            logger.error(f"Failed to cache market overview: {e}")

def cache_projects_list(data: dict[str, Any], ttl: int = 1800):
    """Cache projects list data"""
    if redis_client:
        try:
            redis_client.setex('projects_list', ttl, json.dumps(data))
        except Exception as e:
            logger.error(f"Failed to cache projects list: {e}")

def cache_developers_list(data: dict[str, Any], ttl: int = 1800):
    """Cache developers list data"""
    if redis_client:
        try:
            redis_client.setex('developers_list', ttl, json.dumps(data))
        except Exception as e:
            logger.error(f"Failed to cache developers list: {e}")

import logging
import time
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request

from ..core.metrics import get_metrics_response
from ..core.performance.cache_manager import get_cache_manager
from ..core.performance.connection_pool import get_pool_manager
from ..core.performance.rate_limiter import get_rate_limiter

router = APIRouter()
logger = logging.getLogger(__name__)
USE_POSTGRES = True

@router.get("/")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "database": "postgresql" if USE_POSTGRES else "sqlite", "timestamp": datetime.now().isoformat()}

@router.get("/health")
async def health_check_legacy():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "PropCalc API",
        "version": "1.0.0"
    }

@router.get("/api/v1/health")
async def api_health_check():
    """API health check endpoint"""
    return {"status": "healthy", "database": "postgresql" if USE_POSTGRES else "sqlite", "timestamp": datetime.now().isoformat()}

@router.get("/metrics")
async def metrics():
    """Metrics endpoint"""
    return get_metrics_response()

@router.get("/api/v1/performance/connection-pools")
async def get_connection_pool_stats():
    """Get connection pool statistics"""
    try:
        pool_manager = get_pool_manager()
        stats = pool_manager.get_all_stats()

        return {
            "status": "success",
            "connection_pools": stats,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Error getting connection pool stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get connection pool stats")

@router.get("/api/v1/performance/cache-stats")
async def get_advanced_cache_stats():
    """Get advanced cache statistics"""
    try:
        cache_manager = get_cache_manager()
        stats = cache_manager.get_stats()

        return {
            "status": "success",
            "cache_stats": stats,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get cache stats")

@router.get("/api/v1/performance/rate-limits")
async def get_rate_limit_stats(request: Request):
    """Get rate limiting statistics for current client"""
    try:
        rate_limiter = get_rate_limiter()
        client_id = rate_limiter.get_client_identifier(request)

        # Get stats for main endpoints
        endpoints = ["/api/v1/market/overview", "/api/v1/projects", "/api/v1/ai/calculate-enhanced-score"]
        stats = {}

        for endpoint in endpoints:
            stats[endpoint] = rate_limiter.get_rate_limit_stats(endpoint, client_id)

        return {
            "status": "success",
            "client_id": client_id,
            "rate_limit_stats": stats,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Error getting rate limit stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get rate limit stats")

@router.get("/api/v1/metrics")
async def get_metrics():
    """Get system metrics"""
    try:
        return get_metrics_response()
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/v1/cache/stats")
async def get_cache_stats_endpoint():
    """Get cache statistics"""
    try:
        from ..infrastructure.cache.redis_cache import get_cache_stats
        return get_cache_stats()
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get cache stats")
